#!/usr/bin/env python3
"""ONNX 入力データの形状とメモリ使用量を分析"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np
from train.dataloader import SuperComboDataset, BackgroundGenerator
import time

def analyze_inputs():
    print("=== ONNX 入力データ分析 ===")
    
    # データローダーを作成
    train_data = SuperComboDataset(
        cached_seg_data_path='/home/kou/openpilot-pipeline/comma_data/.cache/segment_data_train.npz', 
        seq_len=20,  # 短いシーケンス長
        dataset_purpose='train',
        recordings_basedir='/home/kou/openpilot-pipeline/comma_data'
    )
    
    # 1つのサンプルを取得
    sample = train_data[0]
    inputs_dict = sample['inputs_dict']
    
    print(f"データセットサイズ: {len(train_data)} samples")
    print(f"\n入力データの形状とメモリ使用量:")
    
    total_memory = 0
    
    for key, tensor in inputs_dict.items():
        if isinstance(tensor, torch.Tensor):
            # メモリ使用量計算 (bytes)
            memory_bytes = tensor.nelement() * tensor.element_size()
            memory_mb = memory_bytes / (1024 * 1024)
            total_memory += memory_bytes
            
            print(f"  {key}:")
            print(f"    - shape: {tensor.shape}")
            print(f"    - dtype: {tensor.dtype}")
            print(f"    - memory: {memory_mb:.2f} MB")
            print(f"    - size: {tensor.nelement():,} elements")
        else:
            print(f"  {key}: {type(tensor)} = {tensor}")
    
    print(f"\n合計メモリ使用量: {total_memory / (1024 * 1024):.2f} MB")
    
    # 最大の入力を特定
    print(f"\n最大入力:")
    max_size = 0
    max_key = ""
    for key, tensor in inputs_dict.items():
        if isinstance(tensor, torch.Tensor):
            size = tensor.nelement()
            if size > max_size:
                max_size = size
                max_key = key
    
    print(f"  最大: {max_key} ({max_size:,} elements)")
    
if __name__ == "__main__":
    analyze_inputs()