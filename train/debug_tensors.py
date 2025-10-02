#!/usr/bin/env python3
import torch
import numpy as np
from model import load_trainable_model
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_model_tensors():
    """モデルの詳細なテンソル形状デバッグ"""
    
    print("=== PyTorch Model Tensor Shape Debug ===")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # モデル読み込み
    ORIGINAL_MODEL = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
    print(f"Loading model from: {ORIGINAL_MODEL}")
    
    try:
        model = load_trainable_model(ORIGINAL_MODEL)
        model = model.to(device)
        model.eval()
        print("✅ Model loaded successfully")
        
        # テスト用の入力テンソルを作成
        batch_size = 1
        print(f"\n=== Creating test inputs (batch_size={batch_size}) ===")
        
        test_inputs = {
            "input_imgs": torch.randn(batch_size, 12, 128, 256, device=device),
            "big_input_imgs": torch.randn(batch_size, 12, 128, 256, device=device),
            "desire": torch.zeros(batch_size, 8, device=device).unsqueeze(1).expand(-1, 100, -1),
            "traffic_convention": torch.zeros(batch_size, 2, device=device),
            "lateral_control_params": torch.zeros(batch_size, 2, device=device),
            "prev_desired_curv": torch.zeros(batch_size, 100, 1, device=device),
            "nav_features": torch.zeros(batch_size, 256, device=device),
            "nav_instructions": torch.zeros(batch_size, 150, device=device),
            "features_buffer": torch.zeros(batch_size, 99, 512, device=device),
            "initial_state": torch.zeros(batch_size, 512, device=device)
        }
        
        # 入力テンソルの形状を表示
        print("\nInput tensor shapes:")
        for name, tensor in test_inputs.items():
            print(f"  {name}: {list(tensor.shape)}")
        
        # モデル推論を実行
        print(f"\n=== Running model inference ===")
        
        with torch.no_grad():
            try:
                outputs = model(**test_inputs)
                print(f"✅ Model inference successful!")
                print(f"Output shape: {list(outputs.shape)}")
                return True
                
            except Exception as e:
                print(f"❌ Model inference failed: {e}")
                
                # より詳細なエラー情報を取得
                print(f"\nError type: {type(e)}")
                print(f"Error details: {str(e)}")
                
                # 各入力を個別にテスト
                print(f"\n=== Testing individual inputs ===")
                for name, tensor in test_inputs.items():
                    print(f"{name}: shape={list(tensor.shape)}, dtype={tensor.dtype}, device={tensor.device}")
                
                return False
                
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

if __name__ == "__main__":
    success = debug_model_tensors()
    exit(0 if success else 1)