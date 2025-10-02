#!/usr/bin/env python3
import torch
import traceback
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_minimal_inference():
    """最小限の入力でモデル推論をテスト"""
    
    print("=== Minimal Model Inference Test ===")
    
    try:
        from model import load_trainable_model
        
        ORIGINAL_MODEL = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
        
        # モデル読み込み
        model = load_trainable_model(ORIGINAL_MODEL)
        model = model.float()
        device = torch.device('cpu')
        model = model.to(device)
        model.eval()
        
        print("✅ Model loaded and configured")
        
        # 最小限の入力を作成（batch_size=1で固定）
        batch_size = 1
        
        inputs = {
            "input_imgs": torch.randn(batch_size, 12, 128, 256, device=device, dtype=torch.float32),
            "big_input_imgs": torch.randn(batch_size, 12, 128, 256, device=device, dtype=torch.float32),
            "desire": torch.zeros(batch_size, 100, 8, device=device, dtype=torch.float32),  # 直接 [1, 100, 8] の形状
            "traffic_convention": torch.zeros(batch_size, 2, device=device, dtype=torch.float32),
            "lateral_control_params": torch.zeros(batch_size, 2, device=device, dtype=torch.float32),
            "prev_desired_curv": torch.zeros(batch_size, 100, 1, device=device, dtype=torch.float32),
            "nav_features": torch.zeros(batch_size, 256, device=device, dtype=torch.float32),
            "nav_instructions": torch.zeros(batch_size, 150, device=device, dtype=torch.float32),
            "features_buffer": torch.zeros(batch_size, 99, 512, device=device, dtype=torch.float32),
        }
        
        print("Input shapes:")
        for name, tensor in inputs.items():
            print(f"  {name}: {list(tensor.shape)} dtype={tensor.dtype}")
        
        # 推論実行
        print("\n=== Running inference ===")
        with torch.no_grad():
            try:
                outputs = model(**inputs)
                print(f"✅ Inference successful!")
                print(f"Output shape: {list(outputs.shape)}")
                print(f"Output dtype: {outputs.dtype}")
                return True
                
            except RuntimeError as e:
                print(f"❌ RuntimeError during inference: {e}")
                
                # エラーメッセージを詳しく分析
                error_msg = str(e)
                if "size of tensor a" in error_msg and "must match the size of tensor b" in error_msg:
                    print("\n🔍 Tensor size mismatch detected!")
                    print("This suggests an issue with the model architecture or input shapes.")
                    
                    # より詳細な形状情報を提供
                    print("\nDetailed input analysis:")
                    for name, tensor in inputs.items():
                        print(f"  {name}:")
                        print(f"    Shape: {list(tensor.shape)}")
                        print(f"    Size: {tensor.numel()} elements")
                        print(f"    Memory: {tensor.numel() * 4 / 1024 / 1024:.2f} MB")
                
                return False
                
            except Exception as e:
                print(f"❌ Other error during inference: {e}")
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Setup error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_inference()
    exit(0 if success else 1)