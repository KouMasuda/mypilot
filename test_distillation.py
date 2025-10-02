#!/usr/bin/env python3
"""純粋なONNX蒸留学習のテスト"""

import sys
import os
sys.path.append('/home/kou/openpilot-pipeline')

import torch
import torch.nn as nn
from train.simple_model import PureONNXModel

def test_pure_onnx():
    print("=== 純粋なONNX蒸留学習テスト ===")
    
    # 純粋なONNXモデル（学習不要）
    teacher_model = PureONNXModel('/home/kou/openpilot-pipeline/common/models/supercombo.onnx')
    
    # 簡単な学生モデル（学習対象）
    class SimpleStudentModel(nn.Module):
        def __init__(self, input_dim=6504, hidden_dim=1024, output_dim=6504):
            super().__init__()
            self.model = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(), 
                nn.Dropout(0.1),
                nn.Linear(hidden_dim // 2, output_dim)
            )
        
        def forward(self, **inputs):
            # 入力の1つを使って勾配を生成（簡単な例）
            input_tensor = inputs['desire']  # (batch_size, 100, 8)
            flattened = input_tensor.view(input_tensor.size(0), -1)  # (batch_size, 800)
            
            # パディングして6504次元に合わせる
            if flattened.size(1) < 6504:
                padding_size = 6504 - flattened.size(1)
                padding = torch.zeros(flattened.size(0), padding_size, device=flattened.device, dtype=flattened.dtype)
                flattened = torch.cat([flattened, padding], dim=1)
            elif flattened.size(1) > 6504:
                flattened = flattened[:, :6504]
            
            return self.model(flattened)
    
    student_model = SimpleStudentModel()
    
    print(f"Teacher (ONNX): 学習不要")
    print(f"Student: {sum(p.numel() for p in student_model.parameters()):,} trainable parameters")
    
    # テスト用入力データ
    batch_size = 1
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
    
    print("\n蒸留学習のシミュレーション...")
    
    # Teacher出力（勾配なし）
    with torch.no_grad():
        teacher_output = teacher_model(**test_inputs)
        print(f"Teacher output: {teacher_output.shape}, no NaN: {not torch.isnan(teacher_output).any()}")
    
    # Student出力（勾配あり）
    student_output = student_model(**test_inputs)
    print(f"Student output: {student_output.shape}, no NaN: {not torch.isnan(student_output).any()}")
    
    # 蒸留損失（MSE） - teacher_outputはすでにno_gradなので.detach()不要
    distill_loss = nn.MSELoss()(student_output, teacher_output)
    print(f"Distillation loss: {distill_loss.item():.6f}")
    
    # 勾配計算のテスト
    distill_loss.backward()
    
    # 勾配チェック
    has_nan_grad = False
    for param in student_model.parameters():
        if param.grad is not None and torch.isnan(param.grad).any():
            has_nan_grad = True
            break
    
    print(f"Student gradients: {'❌ contains NaN' if has_nan_grad else '✅ clean'}")
    
    return not has_nan_grad

if __name__ == "__main__":
    success = test_pure_onnx()
    if success:
        print("\n✅ 純粋なONNX蒸留学習テストが成功しました")
        print("   この方法でNaN問題を回避して学習を進められます")
    else:
        print("\n❌ 蒸留学習テストが失敗しました")