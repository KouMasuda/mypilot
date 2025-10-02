import onnx
import torch
import torch.nn as nn
import onnxruntime as rt
import numpy as np
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_MODEL = os.path.join(parent_dir, 'common/models/supercombo.onnx')


class PureONNXModel(nn.Module):
    """純粋なONNXモデル（学習不要、蒸留用）"""
    
    def __init__(self, onnx_model_path):
        super().__init__()
        
        # ONNXランタイムセッション（最適化設定）
        sess_options = rt.SessionOptions()
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.enable_mem_pattern = False
        sess_options.enable_cpu_mem_arena = False
        
        self.ort_session = rt.InferenceSession(
            onnx_model_path, 
            sess_options,
            providers=['CPUExecutionProvider']
        )
        
        # 入力仕様を取得
        self.input_specs = {spec.name: spec for spec in self.ort_session.get_inputs()}
        
        print("Pure ONNX Model:")
        print(f"  ONNX inputs: {list(self.input_specs.keys())}")
        print(f"  No trainable parameters (distillation target only)")
    
    def forward(self, **inputs):
        """ONNX推論のみ（勾配なし）"""
        
        # PyTorchテンソルをnumpy配列に変換（ONNX用）
        onnx_inputs = {}
        for name, tensor in inputs.items():
            if name in self.input_specs:
                # 入力データの異常値チェック
                if torch.isnan(tensor).any():
                    print(f"WARNING: Input {name} contains NaN values before ONNX!")
                    tensor = torch.nan_to_num(tensor, nan=0.0)
                
                if torch.isinf(tensor).any():
                    print(f"WARNING: Input {name} contains infinite values before ONNX!")
                    tensor = torch.nan_to_num(tensor, posinf=1e6, neginf=-1e6)
                
                # 極端な値のクリッピング
                if tensor.abs().max() > 1e6:
                    print(f"WARNING: Input {name} contains extreme values, clipping...")
                    tensor = torch.clamp(tensor, -1e6, 1e6)
                
                numpy_array = tensor.detach().cpu().numpy().astype(np.float16)
                onnx_inputs[name] = numpy_array
        
        # ONNX推論実行
        import time
        start_time = time.time()
        onnx_outputs = self.ort_session.run(None, onnx_inputs)
        inference_time = time.time() - start_time
        
        # 出力をPyTorchテンソルに変換
        onnx_output = torch.from_numpy(onnx_outputs[0].astype(np.float32))
        
        # 異常値の後処理
        if torch.isnan(onnx_output).any():
            print(f"WARNING: ONNX output contains NaN values!")
            onnx_output = torch.nan_to_num(onnx_output, nan=0.0)
        if torch.isinf(onnx_output).any():
            print(f"WARNING: ONNX output contains infinite values!")
            onnx_output = torch.nan_to_num(onnx_output, posinf=1e6, neginf=-1e6)
        
        # 元のデバイスに戻す
        if inputs:
            device = next(iter(inputs.values())).device
            onnx_output = onnx_output.to(device)
        
        return onnx_output


class ONNXWithAdapter(nn.Module):
    """ONNXランタイム + 学習可能アダプターレイヤー"""
    
    def __init__(self, onnx_model_path, adapter_dim=512):
        super().__init__()
        
        # ONNXランタイムセッション（最適化設定）
        sess_options = rt.SessionOptions()
        sess_options.intra_op_num_threads = 1  # スレッド数を制限してハングを防止
        sess_options.inter_op_num_threads = 1
        sess_options.enable_mem_pattern = False  # メモリパターン最適化を無効化
        sess_options.enable_cpu_mem_arena = False  # メモリアリーナを無効化
        
        self.ort_session = rt.InferenceSession(
            onnx_model_path, 
            sess_options,
            providers=['CPUExecutionProvider']
        )
        
        # 入力仕様を取得
        self.input_specs = {spec.name: spec for spec in self.ort_session.get_inputs()}
        
        # より簡単で安定したアダプターレイヤー
        # 単純な線形変換のみを使用
        self.adapter = nn.Sequential(
            nn.Linear(6504, 6504),
            nn.Dropout(0.1),  # 正規化のため
        )
        
        # アダプターの重みを極めて小さな値で初期化（数値安定性）
        for module in self.adapter:
            if isinstance(module, nn.Linear):
                # Xavierの初期化をさらに小さくしたもの
                nn.init.normal_(module.weight, mean=0.0, std=1e-4)
                nn.init.zeros_(module.bias)
        
        print("ONNX + Adapter Model:")
        print(f"  ONNX inputs: {list(self.input_specs.keys())}")
        print(f"  Adapter parameters: {sum(p.numel() for p in self.adapter.parameters())}")
    
    def forward(self, **inputs):
        """ONNX推論 + アダプター処理"""
        
        # 勾配が必要な入力を記録
        grad_inputs = {name: tensor for name, tensor in inputs.items() if tensor.requires_grad}
        
        # PyTorchテンソルをnumpy配列に変換（ONNX用）
        onnx_inputs = {}
        for name, tensor in inputs.items():
            if name in self.input_specs:
                # 入力データの異常値チェック
                if torch.isnan(tensor).any():
                    print(f"WARNING: Input {name} contains NaN values before ONNX!")
                    # NaNを0に置換
                    tensor = torch.nan_to_num(tensor, nan=0.0)
                
                if torch.isinf(tensor).any():
                    print(f"WARNING: Input {name} contains infinite values before ONNX!")
                    # infを有限値に置換
                    tensor = torch.nan_to_num(tensor, posinf=1e6, neginf=-1e6)
                
                # 極端な値のクリッピング
                if tensor.abs().max() > 1e6:
                    print(f"WARNING: Input {name} contains extreme values (max={tensor.abs().max()}), clipping...")
                    tensor = torch.clamp(tensor, -1e6, 1e6)
                
                numpy_array = tensor.detach().cpu().numpy().astype(np.float16)
                onnx_inputs[name] = numpy_array
        
        # ONNX推論実行（簡略化されたデバッグ）
        import time
        print(f"ONNX inference...")
        
        start_time = time.time()
        onnx_outputs = self.ort_session.run(None, onnx_inputs)
        inference_time = time.time() - start_time
        print(f"ONNX inference: {inference_time:.3f}s")
        
        # 出力をPyTorchテンソルに変換
        onnx_output = torch.from_numpy(onnx_outputs[0].astype(np.float32))
        
        # ONNX出力の後処理とチェック
        if torch.isnan(onnx_output).any():
            print(f"WARNING: ONNX output contains NaN values!")
            onnx_output = torch.nan_to_num(onnx_output, nan=0.0)
        if torch.isinf(onnx_output).any():
            print(f"WARNING: ONNX output contains infinite values!")
            onnx_output = torch.nan_to_num(onnx_output, posinf=1e6, neginf=-1e6)
        
        # 元のデバイスに戻す
        if inputs:
            device = next(iter(inputs.values())).device
            onnx_output = onnx_output.to(device)
        
        # 学習可能なアダプターを適用
        adapted_output = self.adapter(onnx_output)
        
        # アダプター出力の後処理とチェック  
        if torch.isnan(adapted_output).any():
            print(f"WARNING: Adapter output contains NaN values!")
            adapted_output = torch.nan_to_num(adapted_output, nan=0.0)
        if torch.isinf(adapted_output).any():
            print(f"WARNING: Adapter output contains infinite values!")
            adapted_output = torch.nan_to_num(adapted_output, posinf=1.0, neginf=-1.0)
        
        # 元の出力と学習可能な調整を組み合わせ
        # αをアダプターの強度として使用（極めて小さな値で開始）
        alpha = 0.001  # 極めて小さな値で開始
        final_output = onnx_output + alpha * adapted_output
        
        # 最終出力の後処理
        if torch.isnan(final_output).any():
            print(f"WARNING: Final output contains NaN values! Replacing with ONNX output only.")
            final_output = onnx_output  # アダプター無効化
        
        # 最終出力の範囲制限
        final_output = torch.clamp(final_output, -1e6, 1e6)
        
        # 勾配計算のため、入力テンソルとの関係を維持
        if grad_inputs:
            dummy_grad = sum(tensor.sum() * 0 for tensor in grad_inputs.values())
            final_output = final_output + dummy_grad
        
        return final_output

    def parameters(self):
        """アダプターのパラメータのみを返す"""
        return self.adapter.parameters()

    def named_parameters(self):
        """アダプターのパラメータのみを返す"""
        return self.adapter.named_parameters()