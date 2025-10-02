#!/usr/bin/env python3
"""データローダーの出力形状を詳しく調査"""

import sys
sys.path.append('/home/kou/openpilot-pipeline')

import torch
import numpy as np
from train.dataloader import CommaDataset

def debug_dataloader_output():
    """データローダーの出力形状を詳しく調査"""
    
    print("=== CommaDataset出力調査 ===")
    
    dataset = CommaDataset(
        recordings_basedir="/home/kou/openpilot-pipeline/comma_data",
        batch_size=1,  # バッチサイズ1で確認
        seq_len=5,     # シーケンス長5で確認
        validation=False
    )
    
    # 最初のアイテムを取得
    for i, item in enumerate(dataset):
        print(f"\n--- バッチ {i} ---")
        print(f"Item type: {type(item)}")
        
        if isinstance(item, tuple):
            print(f"Tuple length: {len(item)}")
            
            for j, element in enumerate(item):
                print(f"  Element {j}:")
                print(f"    Type: {type(element)}")
                
                if isinstance(element, np.ndarray):
                    print(f"    Shape: {element.shape}")
                    print(f"    Dtype: {element.dtype}")
                    if len(element.shape) >= 2:
                        print(f"    Sample shape at [0]: {element[0].shape if element.ndim > 1 else 'scalar'}")
                else:
                    print(f"    Value: {element}")
        
        # 1つだけ調査
        if i >= 0:
            break
            
    print("\n=== 詳細分析 ===")
    
    # stacked_frames, gt_plans, gt_plans_probs, segment_finished, worker_id の想定
    item = next(iter(dataset))
    if isinstance(item, tuple) and len(item) >= 3:
        stacked_frames = item[0]
        gt_plans = item[1] 
        gt_plans_probs = item[2]
        
        print(f"stacked_frames shape: {stacked_frames.shape}")
        print(f"gt_plans shape: {gt_plans.shape}")
        print(f"gt_plans_probs shape: {gt_plans_probs.shape}")
        
        # tensor変換テスト
        stacked_frames_tensor = torch.from_numpy(stacked_frames).float()
        print(f"Tensor shape: {stacked_frames_tensor.shape}")
        
        # 各次元の意味を推定
        print(f"\n--- 次元解析 ---")
        print(f"stacked_frames.shape = {stacked_frames.shape}")
        if len(stacked_frames.shape) == 4:
            print("  推定: (seq_len, channels, height, width)")
            print(f"    seq_len={stacked_frames.shape[0]}")
            print(f"    channels={stacked_frames.shape[1]}")
            print(f"    height={stacked_frames.shape[2]}")  
            print(f"    width={stacked_frames.shape[3]}")
            
            # 最新フレーム取得テスト
            latest_frame = stacked_frames_tensor[-1]  # (channels, height, width)
            print(f"  Latest frame shape: {latest_frame.shape}")
            
            # バッチ次元追加
            batched_frame = latest_frame.unsqueeze(0)  # (1, channels, height, width)
            print(f"  Batched frame shape: {batched_frame.shape}")

if __name__ == "__main__":
    debug_dataloader_output()