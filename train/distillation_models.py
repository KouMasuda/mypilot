#!/usr/bin/env python3
"""蒸留学習用のモデル定義"""

import torch
import torch.nn as nn
import onnxruntime as ort
import numpy as np
import os

class DistillationTeacher(nn.Module):
    """Teacher model: 純粋なONNXモデル（学習不要）"""
    
    def __init__(self, onnx_model_path):
        super().__init__()
        
        # ONNXランタイムセッション（最適化設定）
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 2
        sess_options.inter_op_num_threads = 2
        sess_options.enable_mem_pattern = False
        sess_options.enable_cpu_mem_arena = False
        
        self.ort_session = ort.InferenceSession(
            onnx_model_path, 
            sess_options,
            providers=['CPUExecutionProvider']
        )
        
        # 入力仕様を取得
        self.input_specs = {spec.name: spec for spec in self.ort_session.get_inputs()}
        
        print("Distillation Teacher (ONNX):")
        print(f"  ONNX inputs: {list(self.input_specs.keys())}")
        print(f"  No trainable parameters")
    
    def forward(self, inputs):
        """ONNX推論実行"""
        try:
            # 入力を配列に変換（ONNXRuntimeが期待する形式）
            input_arrays = {}
            for name, tensor in inputs.items():
                if isinstance(tensor, torch.Tensor):
                    # GPUテンソルをCPU numpy配列に変換（float16へ変換）
                    numpy_array = tensor.detach().cpu().numpy().astype(np.float16)
                    
                    # 入力は既に正しい形状で渡されているはず（バッチ処理済み）
                    # 追加の次元処理は不要
                    input_arrays[name] = numpy_array
                else:
                    input_arrays[name] = tensor
            
            # ONNX推論実行
            output = self.ort_session.run(None, input_arrays)
            
            # 結果をテンソルに変換
            onnx_output = torch.from_numpy(output[0]).float()
            
        except Exception as e:
            print(f"ONNX inference error: {e}")
            # エラー時はダミー出力を返す
            batch_size = next(iter(inputs.values())).shape[0] if inputs else 1
            onnx_output = torch.zeros(batch_size, 6504)
        
        # NaN/Infチェック
        if torch.isnan(onnx_output).any():
            onnx_output = torch.nan_to_num(onnx_output, nan=0.0)
        if torch.isinf(onnx_output).any():
            onnx_output = torch.nan_to_num(onnx_output, posinf=1e6, neginf=-1e6)
        
        # デバイスを合わせる
        if inputs:
            device = next(iter(inputs.values())).device
            onnx_output = onnx_output.to(device)
        
        return onnx_output


class DistillationStudent(nn.Module):
    """Student model: 学習可能な軽量モデル"""
    
    def __init__(self, output_dim=6504, hidden_dim=1024):
        super().__init__()
        
        # 入力特徴抽出部（各入力を独立に処理）
        self.input_processors = nn.ModuleDict({
            'input_imgs': nn.Sequential(
                nn.Conv2d(12, 32, 3, stride=2, padding=1),  # (12,128,256) -> (32,64,128)
                nn.ReLU(),
                nn.Conv2d(32, 64, 3, stride=2, padding=1),  # (32,64,128) -> (64,32,64)
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((8, 16)),  # (64,32,64) -> (64,8,16)
                nn.Flatten()  # -> 8192
            ),
            'big_input_imgs': nn.Sequential(
                nn.Conv2d(12, 32, 3, stride=2, padding=1),
                nn.ReLU(),
                nn.Conv2d(32, 64, 3, stride=2, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((4, 8)),  # -> (64,4,8) -> 2048
                nn.Flatten()
            ),
            'desire': nn.Sequential(
                nn.Flatten(),  # (100,8) -> 800
                nn.Linear(800, 128),
                nn.ReLU()
            ),
            'traffic_convention': nn.Sequential(
                nn.Linear(2, 32),
                nn.ReLU()
            ),
            'lateral_control_params': nn.Sequential(
                nn.Linear(2, 32),
                nn.ReLU()
            ),
            'prev_desired_curv': nn.Sequential(
                nn.Flatten(),  # (100,1) -> 100
                nn.Linear(100, 64),
                nn.ReLU()
            ),
            'nav_features': nn.Sequential(
                nn.Linear(256, 128),
                nn.ReLU()
            ),
            'nav_instructions': nn.Sequential(
                nn.Linear(150, 64),
                nn.ReLU()
            ),
            'features_buffer': nn.Sequential(
                nn.Flatten(),  # (99,512) -> 50688
                nn.Linear(50688, 512),
                nn.ReLU()
            )
        })
        
        # 統合部
        total_features = 8192 + 2048 + 128 + 32 + 32 + 64 + 128 + 64 + 512  # = 11200
        
        self.fusion = nn.Sequential(
            nn.Linear(total_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, output_dim)
        )
        
        # 重みを適切に初期化
        self._init_weights()
        
        total_params = sum(p.numel() for p in self.parameters())
        print(f"Distillation Student:")
        print(f"  Trainable parameters: {total_params:,}")
    
    def _init_weights(self):
        """重みの初期化"""
        for module in self.modules():
            if isinstance(module, (nn.Linear, nn.Conv2d)):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, **inputs):
        """フォワードパス"""
        
        # 各入力を独立に処理
        features = []
        for name, processor in self.input_processors.items():
            if name in inputs:
                x = inputs[name]
                
                # 入力は既に正しいバッチ形状で渡される想定
                # input_imgs, big_input_imgs: (batch_size, 12, 128, 256)
                # その他の入力も適切なバッチ形状
                
                feature = processor(x)
                features.append(feature)
        
        # 特徴を統合
        combined_features = torch.cat(features, dim=1)
        output = self.fusion(combined_features)
        
        return output


def create_distillation_models(onnx_path, student_hidden_dim=1024):
    """蒸留学習用のteacherとstudentモデルを作成"""
    
    teacher = DistillationTeacher(onnx_path)
    student = DistillationStudent(hidden_dim=student_hidden_dim)
    
    return teacher, student