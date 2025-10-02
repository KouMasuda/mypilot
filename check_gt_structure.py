#!/usr/bin/env python3
"""
Ground truthデータの構造を確認するスクリプト
"""

import h5py
import numpy as np

def check_gt_structure():
    """Ground truthファイルの構造確認"""
    
    gt_path = "/home/kou/openpilot-pipeline/comma_data/2023-11-22--06-10-54--13/gt_distill.h5"
    
    with h5py.File(gt_path, 'r') as f:
        print("=== Ground Truth HDF5 Structure ===")
        def print_structure(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"{name}: {obj.shape} {obj.dtype}")
                if obj.shape[0] > 0:
                    print(f"  Sample: {obj[0]}")
            else:
                print(f"{name}: (group)")
        
        f.visititems(print_structure)

if __name__ == "__main__":
    check_gt_structure()