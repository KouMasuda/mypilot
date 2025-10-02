#!/usr/bin/env python3
import torch
import traceback
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pytorch_float16():
    """PyTorchモデルをfloat16で試行"""
    
    print("=== Testing PyTorch Model with float16 ===")
    
    try:
        from model import load_trainable_model
        
        ORIGINAL_MODEL = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
        
        # モデル読み込み（float16のまま）
        model = load_trainable_model(ORIGINAL_MODEL)
        # model = model.float()  # float32変換を削除
        device = torch.device('cpu')
        model = model.to(device)
        model.eval()
        
        print("✅ Model loaded (keeping original dtype)")
        
        # float16の入力を作成
        batch_size = 1
        
        inputs = {
            "input_imgs": torch.randn(batch_size, 12, 128, 256, device=device, dtype=torch.float16),
            "big_input_imgs": torch.randn(batch_size, 12, 128, 256, device=device, dtype=torch.float16),
            "desire": torch.zeros(batch_size, 100, 8, device=device, dtype=torch.float16),
            "traffic_convention": torch.zeros(batch_size, 2, device=device, dtype=torch.float16),
            "lateral_control_params": torch.zeros(batch_size, 2, device=device, dtype=torch.float16),
            "prev_desired_curv": torch.zeros(batch_size, 100, 1, device=device, dtype=torch.float16),
            "nav_features": torch.zeros(batch_size, 256, device=device, dtype=torch.float16),
            "nav_instructions": torch.zeros(batch_size, 150, device=device, dtype=torch.float16),
            "features_buffer": torch.zeros(batch_size, 99, 512, device=device, dtype=torch.float16),
            "initial_state": torch.zeros(batch_size, 512, device=device, dtype=torch.float16),
        }
        
        print("Input shapes (float16):")
        for name, tensor in inputs.items():
            print(f"  {name}: {list(tensor.shape)} dtype={tensor.dtype}")
        
        # 推論実行
        print("\n=== Running inference with float16 ===")
        with torch.no_grad():
            try:
                outputs = model(**inputs)
                print(f"✅ Inference successful with float16!")
                print(f"Output shape: {list(outputs.shape)}")
                print(f"Output dtype: {outputs.dtype}")
                return True
                
            except Exception as e:
                print(f"❌ Float16 inference failed: {e}")
                
                # float32を試す
                print(f"\n=== Trying mixed precision (model float16, inputs float32) ===")
                
                # 入力をfloat32に変換
                inputs_f32 = {k: v.float() for k, v in inputs.items()}
                
                try:
                    outputs = model(**inputs_f32)
                    print(f"✅ Mixed precision successful!")
                    print(f"Output shape: {list(outputs.shape)}")
                    return True
                except Exception as e2:
                    print(f"❌ Mixed precision also failed: {e2}")
                    return False
                
    except Exception as e:
        print(f"❌ Setup error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pytorch_float16()
    exit(0 if success else 1)