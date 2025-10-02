#!/usr/bin/env python3
"""単一のフォワードパステスト"""

import sys
import os
sys.path.append('/home/kou/openpilot-pipeline')

import torch
from train.model import ONNXWithAdapter
from train.dataloader import CommaDataset

def test_single_forward():
    print("=== 単一フォワードパステスト ===")
    
    # データローダーを作成
    train_data = CommaDataset(
        recordings_basedir='/home/kou/openpilot-pipeline/comma_data',
        batch_size=1,
        seq_len=20,
        validation=False,
        shuffle=False,
        seed=42
    )
    
    # モデルを作成
    model = ONNXWithAdapter('/home/kou/openpilot-pipeline/common/models/supercombo.onnx')
    
    print("訓練用のテストスクリプトを直接作成...")
    
    # 簡単なテスト用入力データを手動作成
    batch_size = 1
    seq_len = 20
    
    test_inputs = {
        'input_imgs': torch.randn(batch_size, 12, 128, 256, dtype=torch.float32),
        'big_input_imgs': torch.randn(batch_size, 12, 128, 256, dtype=torch.float32),
        'desire': torch.randn(batch_size, 100, 8, dtype=torch.float32),
        'traffic_convention': torch.randn(batch_size, 2, dtype=torch.float32),
        'lateral_control_params': torch.randn(batch_size, 2, dtype=torch.float32),
        'prev_desired_curv': torch.randn(batch_size, 100, 1, dtype=torch.float32),
        'nav_features': torch.randn(batch_size, 256, dtype=torch.float32),
        'nav_instructions': torch.randn(batch_size, 150, dtype=torch.float32),
        'features_buffer': torch.randn(batch_size, 99, 512, dtype=torch.float32),
    }
    
    print("テスト入力データサイズ:")
    for key, tensor in test_inputs.items():
        print(f"  {key}: {tensor.shape}, {tensor.dtype}")
    
    print("\nフォワードパス実行中...")
    
    # テストフォワードパス（勾配なし）
    with torch.no_grad():
        try:
            outputs = model(**test_inputs)
            print(f"成功: 出力形状={outputs.shape}")
            if torch.isnan(outputs).any():
                print("ERROR: 出力にNaNが含まれています")
                print(f"NaN数: {torch.isnan(outputs).sum().item()}")
                return False
            else:
                print("OK: NaN値は検出されませんでした")
                print(f"出力統計: min={outputs.min().item():.6f}, max={outputs.max().item():.6f}, mean={outputs.mean().item():.6f}")
                return True
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_single_forward()
    if success:
        print("\n✅ 単一フォワードパステストが成功しました")
    else:
        print("\n❌ 単一フォワードパステストが失敗しました")