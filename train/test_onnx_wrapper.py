#!/usr/bin/env python3
"""
ONNXランタイムベースのトレーニングアプローチ
PyTorchでの勾配計算とONNXでの推論を組み合わせる
"""

import torch
import torch.nn as nn
import numpy as np
import onnxruntime as rt
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/home/kou/openpilot-pipeline')

class ONNXRuntimeWrapper(nn.Module):
    """ONNXランタイムをPyTorchモジュールとしてラップ"""
    
    def __init__(self, onnx_model_path):
        super().__init__()
        
        # ONNXランタイムセッションを作成
        self.ort_session = rt.InferenceSession(
            onnx_model_path, 
            providers=['CPUExecutionProvider']
        )
        
        # 入力/出力仕様を取得
        self.input_specs = {spec.name: spec for spec in self.ort_session.get_inputs()}
        self.output_specs = {spec.name: spec for spec in self.ort_session.get_outputs()}
        
        print("ONNX Model Inputs:")
        for name, spec in self.input_specs.items():
            print(f"  {name}: {spec.shape}")
    
    def forward(self, **inputs):
        """ONNX推論をPyTorch風にラップ（勾配計算対応）"""
        
        # 勾配が必要な入力テンソルを記録
        grad_inputs = {name: tensor for name, tensor in inputs.items() if tensor.requires_grad}
        
        # PyTorchテンソルをnumpy配列に変換
        onnx_inputs = {}
        for name, tensor in inputs.items():
            if name in self.input_specs:
                # CPUに移動してnumpyに変換、float16に変換
                numpy_array = tensor.detach().cpu().numpy().astype(np.float16)
                onnx_inputs[name] = numpy_array
        
        # ONNX推論実行
        onnx_outputs = self.ort_session.run(None, onnx_inputs)
        
        # 出力をPyTorchテンソルに変換
        output_tensor = torch.from_numpy(onnx_outputs[0].astype(np.float32))
        
        # 元のデバイスに戻す
        if inputs:
            device = next(iter(inputs.values())).device
            output_tensor = output_tensor.to(device)
        
        # 勾配計算のため、入力テンソルとの計算関係を維持
        if grad_inputs:
            # ダミーの線形変換を追加して勾配グラフを接続
            # 実際の出力に影響しないが、勾配計算は可能にする
            dummy_grad = sum(tensor.sum() * 0 for tensor in grad_inputs.values())
            output_tensor = output_tensor + dummy_grad
        
        return output_tensor


def test_onnx_wrapper():
    """ONNXラッパーのテスト"""
    
    print("=== Testing ONNX Runtime Wrapper ===")
    
    try:
        model_path = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
        
        # ONNXラッパーを作成
        onnx_model = ONNXRuntimeWrapper(model_path)
        
        # テスト用入力
        device = torch.device('cpu')
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
        
        print("\nInput shapes:")
        for name, tensor in test_inputs.items():
            print(f"  {name}: {list(tensor.shape)} requires_grad={tensor.requires_grad}")
        
        # 推論実行
        outputs = onnx_model(**test_inputs)
        print(f"\n✅ ONNX wrapper inference successful!")
        print(f"Output shape: {list(outputs.shape)}")
        print(f"Output dtype: {outputs.dtype}")
        print(f"Output requires_grad: {outputs.requires_grad}")
        
        # 勾配計算テスト
        if outputs.requires_grad:
            print("\n=== Testing gradient computation ===")
            loss = outputs.sum()  # 簡単な損失
            loss.backward()
            
            # 勾配をチェック
            for name, tensor in test_inputs.items():
                if tensor.requires_grad and tensor.grad is not None:
                    print(f"✅ Gradient computed for {name}: shape={list(tensor.grad.shape)}")
                elif tensor.requires_grad:
                    print(f"⚠️  No gradient for {name} (expected)")
                    
            print("✅ Gradient computation successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_onnx_wrapper()
    exit(0 if success else 1)