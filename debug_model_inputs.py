#!/usr/bin/env python3

import onnx
import numpy as np

def debug_model_inputs(model_path):
    """ONNXモデルの入力仕様を詳細に調査"""
    
    # ONNXモデルを読み込み
    model = onnx.load(model_path)
    
    print("=== ONNX Model Input Details ===")
    
    for i, input_info in enumerate(model.graph.input):
        name = input_info.name
        shape = [dim.dim_value if dim.dim_value != 0 else 'dynamic' for dim in input_info.type.tensor_type.shape.dim]
        dtype = input_info.type.tensor_type.elem_type
        
        print(f"Input {i+1}: '{name}'")
        print(f"  Shape: {shape}")
        print(f"  Data type: {dtype}")
        print()

if __name__ == "__main__":
    print("Checking v0.8.11 model:")
    model_path_v8 = "/home/kou/openpilot-pipeline/common/models/supercombo_v0.8.11.onnx"
    debug_model_inputs(model_path_v8)
    
    print("\n" + "="*50 + "\n")
    
    print("Checking latest model (supercombo.onnx):")
    model_path_latest = "/home/kou/openpilot-pipeline/common/models/supercombo.onnx"
    debug_model_inputs(model_path_latest)