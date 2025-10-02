#!/usr/bin/env python3
import numpy as np
import onnxruntime as rt
import torch
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/home/kou/openpilot-pipeline')

def test_onnx_vs_pytorch():
    """ONNXランタイムとPyTorchモデルの比較テスト"""
    
    print("=== ONNX Runtime vs PyTorch Model Comparison ===")
    
    # ONNX Runtime テスト
    print("\n1. Testing ONNX Runtime...")
    try:
        model_path = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
        ort_session = rt.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        # 入力仕様を取得
        input_specs = ort_session.get_inputs()
        print("ONNX Runtime input specifications:")
        for spec in input_specs:
            print(f"  {spec.name}: {spec.shape} ({spec.type})")
        
        # テスト用の入力を作成（ONNX仕様に基づく）
        onnx_inputs = {}
        for spec in input_specs:
            name = spec.name
            shape = [1 if dim is None or isinstance(dim, str) else dim for dim in spec.shape]
            
            if name in ['input_imgs', 'big_input_imgs']:
                onnx_inputs[name] = np.random.randn(*shape).astype(np.float16)
            else:
                onnx_inputs[name] = np.zeros(shape, dtype=np.float16)
        
        print("\nONNX Runtime input shapes:")
        for name, array in onnx_inputs.items():
            print(f"  {name}: {list(array.shape)} dtype={array.dtype}")
        
        # ONNX推論実行
        onnx_outputs = ort_session.run(None, onnx_inputs)
        print(f"✅ ONNX Runtime inference successful!")
        print(f"ONNX output shape: {[list(out.shape) for out in onnx_outputs]}")
        
    except Exception as e:
        print(f"❌ ONNX Runtime failed: {e}")
        return False
    
    # PyTorch モデルテスト
    print("\n2. Testing PyTorch converted model...")
    try:
        from train.model import load_trainable_model
        
        # PyTorchモデル読み込み
        model = load_trainable_model(model_path)
        model = model.float()  # float32に変換
        model.eval()
        
        # ONNX入力をPyTorchテンソルに変換（float32）
        device = torch.device('cpu')
        pytorch_inputs = {}
        
        for name, array in onnx_inputs.items():
            if name != 'initial_state':  # initial_stateは除く（PyTorchモデルでは別途処理）
                pytorch_inputs[name] = torch.from_numpy(array.astype(np.float32)).to(device)
        
        # initial_stateを追加
        pytorch_inputs['initial_state'] = torch.zeros(1, 512, device=device, dtype=torch.float32)
        
        print("\nPyTorch input shapes:")
        for name, tensor in pytorch_inputs.items():
            print(f"  {name}: {list(tensor.shape)} dtype={tensor.dtype}")
        
        # PyTorch推論実行
        with torch.no_grad():
            pytorch_outputs = model(**pytorch_inputs)
            
        print(f"✅ PyTorch inference successful!")
        print(f"PyTorch output shape: {list(pytorch_outputs.shape)}")
        
        return True
        
    except Exception as e:
        print(f"❌ PyTorch inference failed: {e}")
        
        # より詳細なエラー分析
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_onnx_vs_pytorch()
    exit(0 if success else 1)