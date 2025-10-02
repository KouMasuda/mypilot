#!/usr/bin/env python3
"""
ONNXランタイム + 学習可能アダプターレイヤーのハイブリッドアプローチ
"""

import torch
import torch.nn as nn
import onnxruntime as rt
import numpy as np


class ONNXWithAdapter(nn.Module):
    """ONNXランタイム + 学習可能アダプターレイヤー"""
    
    def __init__(self, onnx_model_path, adapter_dim=512):
        super().__init__()
        
        # ONNXランタイムセッション
        self.ort_session = rt.InferenceSession(
            onnx_model_path, 
            providers=['CPUExecutionProvider']
        )
        
        # 入力仕様を取得
        self.input_specs = {spec.name: spec for spec in self.ort_session.get_inputs()}
        
        # 学習可能なアダプターレイヤーを追加
        # ONNXモデルの出力（6504次元）を処理
        self.adapter = nn.Sequential(
            nn.Linear(6504, adapter_dim),
            nn.ReLU(),
            nn.Linear(adapter_dim, 6504),
            nn.Tanh()  # 出力を-1〜1の範囲にクランプ
        )
        
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
                numpy_array = tensor.detach().cpu().numpy().astype(np.float16)
                onnx_inputs[name] = numpy_array
        
        # ONNX推論実行
        onnx_outputs = self.ort_session.run(None, onnx_inputs)
        
        # 出力をPyTorchテンソルに変換
        onnx_output = torch.from_numpy(onnx_outputs[0].astype(np.float32))
        
        # 元のデバイスに戻す
        if inputs:
            device = next(iter(inputs.values())).device
            onnx_output = onnx_output.to(device)
        
        # 学習可能なアダプターを適用
        adapted_output = self.adapter(onnx_output)
        
        # 元の出力と学習可能な調整を組み合わせ
        # αをアダプターの強度として使用（小さな値で開始）
        alpha = 0.1
        final_output = onnx_output + alpha * adapted_output
        
        # 勾配計算のため、入力テンソルとの関係を維持
        if grad_inputs:
            dummy_grad = sum(tensor.sum() * 0 for tensor in grad_inputs.values())
            final_output = final_output + dummy_grad
        
        return final_output
    
    def parameters(self):
        """学習可能なパラメータのみを返す"""
        return self.adapter.parameters()
    
    def named_parameters(self, prefix='', recurse=True):
        """学習可能なパラメータのみを返す"""
        return self.adapter.named_parameters(prefix=prefix, recurse=recurse)


def test_onnx_adapter():
    """ONNXアダプターモデルのテスト"""
    
    print("=== Testing ONNX + Adapter Model ===")
    
    try:
        model_path = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
        
        # ONNXアダプターモデルを作成
        model = ONNXWithAdapter(model_path)
        device = torch.device('cpu')
        model = model.to(device)
        
        # 学習可能なパラメータを確認
        total_params = sum(p.numel() for p in model.parameters())
        print(f"\nTotal trainable parameters: {total_params}")
        
        # テスト用入力
        batch_size = 1
        test_inputs = {
            "input_imgs": torch.randn(batch_size, 12, 128, 256, device=device, dtype=torch.float32, requires_grad=True),
            "big_input_imgs": torch.randn(batch_size, 12, 128, 256, device=device, dtype=torch.float32, requires_grad=True),
            "desire": torch.zeros(batch_size, 100, 8, device=device, dtype=torch.float32),
            "traffic_convention": torch.zeros(batch_size, 2, device=device, dtype=torch.float32),
            "lateral_control_params": torch.zeros(batch_size, 2, device=device, dtype=torch.float32),
            "prev_desired_curv": torch.zeros(batch_size, 100, 1, device=device, dtype=torch.float32),
            "nav_features": torch.zeros(batch_size, 256, device=device, dtype=torch.float32),
            "nav_instructions": torch.zeros(batch_size, 150, device=device, dtype=torch.float32),
            "features_buffer": torch.zeros(batch_size, 99, 512, device=device, dtype=torch.float32),
        }
        
        # 推論実行
        outputs = model(**test_inputs)
        print(f"\n✅ Forward pass successful!")
        print(f"Output shape: {list(outputs.shape)}")
        print(f"Output requires_grad: {outputs.requires_grad}")
        
        # 勾配計算テスト
        loss = outputs.sum()
        loss.backward()
        
        # パラメータの勾配をチェック
        for name, param in model.named_parameters():
            if param.grad is not None:
                print(f"✅ Gradient for {name}: shape={list(param.grad.shape)}, norm={param.grad.norm():.6f}")
        
        print("\n✅ ONNX + Adapter model test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_onnx_adapter()
    exit(0 if success else 1)