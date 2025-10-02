#!/usr/bin/env python3
import torch
import traceback
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_different_image_sizes():
    """異なる画像サイズでテスト"""
    
    print("=== Testing Different Image Sizes ===")
    
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
        
        # 複数の画像サイズをテスト
        image_sizes = [
            (128, 256),  # Original
            (128, 512),  # Double width
            (256, 256),  # Square
            (256, 512),  # Larger square
        ]
        
        batch_size = 1
        
        for height, width in image_sizes:
            print(f"\n=== Testing image size: {height}x{width} ===")
            
            try:
                inputs = {
                    "input_imgs": torch.randn(batch_size, 12, height, width, device=device, dtype=torch.float32),
                    "big_input_imgs": torch.randn(batch_size, 12, height, width, device=device, dtype=torch.float32),
                    "desire": torch.zeros(batch_size, 100, 8, device=device, dtype=torch.float32),
                    "traffic_convention": torch.zeros(batch_size, 2, device=device, dtype=torch.float32),
                    "lateral_control_params": torch.zeros(batch_size, 2, device=device, dtype=torch.float32),
                    "prev_desired_curv": torch.zeros(batch_size, 100, 1, device=device, dtype=torch.float32),
                    "nav_features": torch.zeros(batch_size, 256, device=device, dtype=torch.float32),
                    "nav_instructions": torch.zeros(batch_size, 150, device=device, dtype=torch.float32),
                    "features_buffer": torch.zeros(batch_size, 99, 512, device=device, dtype=torch.float32),
                }
                
                # 推論実行
                with torch.no_grad():
                    outputs = model(**inputs)
                    print(f"✅ SUCCESS with {height}x{width}! Output shape: {list(outputs.shape)}")
                    return height, width  # 成功した最初のサイズを返す
                    
            except Exception as e:
                print(f"❌ FAILED with {height}x{width}: {e}")
                continue
        
        print(f"\n❌ All image sizes failed!")
        return None, None
                
    except Exception as e:
        print(f"❌ Setup error: {e}")
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    height, width = test_different_image_sizes()
    if height and width:
        print(f"\n🎉 Found working image size: {height}x{width}")
        exit(0)
    else:
        print(f"\n💔 No working image size found")
        exit(1)