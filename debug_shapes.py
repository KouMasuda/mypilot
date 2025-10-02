#!/usr/bin/env python3
"""
データの形状をデバッグするスクリプト
"""

import sys
sys.path.append('/home/kou/openpilot-pipeline')

import torch
import numpy as np
from train.dataloader import CommaDataset
from train.distillation_models import create_distillation_models

def debug_data_shapes():
    """データの形状を確認"""
    
    # CommaDatasetを作成
    dataset = CommaDataset(
        recordings_basedir="/home/kou/openpilot-pipeline/comma_data",
        batch_size=1,
        seq_len=5,
        validation=False
    )
    
    # 1バッチ取得
    for batch_data in dataset:
        print("=== データローダー出力の形状 ===")
        print(f"Batch data type: {type(batch_data)}")
        
        if isinstance(batch_data, tuple):
            print(f"Tuple length: {len(batch_data)}")
            for i, item in enumerate(batch_data):
                print(f"Item {i}: type={type(item)}, shape={getattr(item, 'shape', 'no shape')}")
            
            # CommaDatasetは通常辞書を最初の要素として返す
            if len(batch_data) > 0 and isinstance(batch_data[0], dict):
                batch_dict = batch_data[0]
            else:
                print("Expected dict in first element, skipping...")
                break
        else:
            batch_dict = batch_data
        
        for key, value in batch_dict.items():
            if isinstance(value, (np.ndarray, torch.Tensor)):
                print(f"{key}: {value.shape} (type: {type(value)})")
        
        # テンソルに変換
        batch_tensors = {}
        for key, value in batch_dict.items():
            if isinstance(value, np.ndarray):
                tensor = torch.from_numpy(value).float()
                batch_tensors[key] = tensor
                print(f"{key} tensor: {tensor.shape}")
        
        # モデル作成
        teacher, student = create_distillation_models('/home/kou/openpilot-pipeline/common/models/supercombo.onnx')
        
        print("\n=== Teacher入力準備 ===")
        try:
            # 各入力をONNX用に準備
            teacher_inputs = {}
            for name, tensor in batch_tensors.items():
                numpy_array = tensor.detach().cpu().numpy()
                
                print(f"Original {name}: {numpy_array.shape}")
                
                # シーケンスデータの場合は最新フレーム（最後のタイムステップ）のみ使用
                if len(numpy_array.shape) > 2 and numpy_array.shape[1] > 1:
                    # (batch_size, seq_len, ...) -> (batch_size, ...)の最後を取る
                    if name in ['desire', 'prev_desired_curv']:
                        # これらは(batch_size, 100, dim)形式なので最後の次元を維持
                        numpy_array = numpy_array[:, -1, :]  # 最新タイムステップ
                        print(f"  After seq reduction {name}: {numpy_array.shape}")
                    elif name in ['traffic_convention', 'lateral_control_params']:
                        # これらは(batch_size, seq_len, 1) -> (batch_size, 1)
                        numpy_array = numpy_array[:, -1]  # 最新タイムステップ
                        print(f"  After seq reduction {name}: {numpy_array.shape}")
                    else:
                        # 画像などは最新フレームを使用
                        numpy_array = numpy_array[:, -1]
                        print(f"  After seq reduction {name}: {numpy_array.shape}")
                
                teacher_inputs[name] = torch.from_numpy(numpy_array).float()
            
            print(f"\n=== Teacher推論テスト ===")
            teacher_output = teacher(teacher_inputs)
            print(f"Teacher output: {teacher_output.shape}")
            
            print(f"\n=== Student推論テスト ===")
            student_output = student(**batch_tensors)
            print(f"Student output: {student_output.shape}")
            
        except Exception as e:
            print(f"Error during model inference: {e}")
            import traceback
            traceback.print_exc()
        
        break  # 1バッチだけテスト

if __name__ == "__main__":
    debug_data_shapes()