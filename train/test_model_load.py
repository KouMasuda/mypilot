#!/usr/bin/env python3
import torch
import traceback
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_model_load():
    """シンプルなモデル読み込みテスト"""
    
    print("=== Simple Model Loading Test ===")
    
    try:
        from model import load_trainable_model
        
        ORIGINAL_MODEL = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
        print(f"Loading model from: {ORIGINAL_MODEL}")
        
        # モデル読み込みのみテスト
        model = load_trainable_model(ORIGINAL_MODEL)
        print("✅ Model loaded successfully")
        
        # モデルの基本情報を取得
        print(f"Model type: {type(model)}")
        
        if hasattr(model, 'input_names'):
            print(f"Input names: {model.input_names}")
        
        # 単精度変換をテスト
        model = model.float()
        print("✅ Model converted to float32")
        
        device = torch.device('cpu')  # CPUのみでテスト
        model = model.to(device)
        print("✅ Model moved to CPU")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_model_load()
    exit(0 if success else 1)