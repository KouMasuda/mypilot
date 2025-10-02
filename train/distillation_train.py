#!/usr/bin/env python3
"""蒸留学習用の訓練スクリプト"""

import warnings
warnings.filterwarnings("ignore")

import argparse
import time
import numpy as np
from tqdm import tqdm
import torch
import torch.optim as optim
import torch.nn as nn
from dataloader import CommaDataset, BackgroundGenerator
import wandb
import os
import sys

# カスタムモデルをインポート
from distillation_models import create_distillation_models

def parse_args():
    parser = argparse.ArgumentParser(description='Openpilot Distillation Training')
    
    # データ関連
    parser.add_argument('--recordings_basedir', type=str, required=True,
                        help='Path to comma data directory')
    parser.add_argument('--batch_size', type=int, default=4,
                        help='Batch size for training')
    parser.add_argument('--seq_len', type=int, default=20,
                        help='Sequence length')
    parser.add_argument('--split', type=float, default=0.9,
                        help='Train/validation split ratio')
    
    # モデル関連
    parser.add_argument('--onnx_model', type=str, 
                        default='/home/kou/openpilot-pipeline/common/models/supercombo.onnx',
                        help='Path to ONNX teacher model')
    parser.add_argument('--student_hidden_dim', type=int, default=512,
                        help='Hidden dimension for student model')
    
    # 訓練関連
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=1e-4,
                        help='Weight decay')
    parser.add_argument('--grad_clip', type=float, default=1.0,
                        help='Gradient clipping threshold')
    
    # その他
    parser.add_argument('--device', type=str, default='auto',
                        help='Device to use (cpu/cuda/auto)')
    parser.add_argument('--save_dir', type=str, default='./checkpoints',
                        help='Directory to save checkpoints')
    parser.add_argument('--log_interval', type=int, default=10,
                        help='Logging interval')
    parser.add_argument('--no_wandb', action='store_true',
                        help='Disable wandb logging')
    
    return parser.parse_args()

def setup_device(device_arg):
    """デバイス設定"""
    if device_arg == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device_arg)
    
    print(f"Using device: {device}")
    return device

def create_data_loaders(args):
    """データローダーを作成"""
    
    # 訓練データセット
    train_dataset = CommaDataset(
        recordings_basedir=args.recordings_basedir,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        validation=False,
        shuffle=True,
        train_split=args.split
    )
    
    # 検証データセット
    val_dataset = CommaDataset(
        recordings_basedir=args.recordings_basedir,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        validation=True,
        shuffle=False,
        train_split=args.split
    )
    
    # バックグラウンドジェネレーター
    train_loader = BackgroundGenerator(train_dataset)
    val_loader = BackgroundGenerator(val_dataset)
    
    return train_loader, val_loader

def distillation_loss(student_output, teacher_output, temperature=4.0):
    """蒸留損失（温度付きKLダイバージェンス）"""
    
    # 温度スケーリング
    student_logits = student_output / temperature
    teacher_logits = teacher_output / temperature
    
    # ソフトマックスで確率分布に変換
    student_probs = torch.softmax(student_logits, dim=-1)
    teacher_probs = torch.softmax(teacher_logits, dim=-1)
    
    # KLダイバージェンス損失
    kl_loss = nn.KLDivLoss(reduction='batchmean')(
        torch.log_softmax(student_logits, dim=-1),
        teacher_probs
    )
    
    # 温度の二乗でスケール
    kl_loss = kl_loss * (temperature ** 2)
    
    # MSE損失も追加（特徴マッチング）
    mse_loss = nn.MSELoss()(student_output, teacher_output)
    
    # 組み合わせ
    total_loss = 0.7 * kl_loss + 0.3 * mse_loss
    
    return total_loss, kl_loss, mse_loss

def train_epoch(teacher, student, train_loader, optimizer, device, args):
    """1エポックの訓練"""
    
    student.train()
    teacher.eval()
    
    total_loss = 0.0
    total_kl_loss = 0.0
    total_mse_loss = 0.0
    num_batches = 0
    
    progress_bar = tqdm(enumerate(train_loader), desc="Training")
    
    for batch_idx, batch_data in progress_bar:
        try:
            # バッチデータの展開
            stacked_frames, gt_plans, gt_plans_probs, segment_finished, worker_id = batch_data
            
            # 入力データの準備（numpy -> PyTorchテンソル変換）
            stacked_frames_tensor = torch.from_numpy(stacked_frames).float().to(device)
            
            # データ構造: stacked_frames = (seq_len=5, channels=12, height=128, width=256)
            # 最新フレームを取得: (12, 128, 256)
            latest_frame = stacked_frames_tensor[-1]
            
            # バッチ次元を追加: (1, 12, 128, 256)
            latest_frame_batch = latest_frame.unsqueeze(0)
            
            # 正しい形状でONNX入力を準備
            inputs = {
                'input_imgs': latest_frame_batch,      # (1, 12, 128, 256)
                'big_input_imgs': latest_frame_batch,   # (1, 12, 128, 256) 
                'desire': torch.zeros(1, 100, 8, device=device),
                'traffic_convention': torch.ones(1, 2, device=device),
                'lateral_control_params': torch.zeros(1, 2, device=device), 
                'prev_desired_curv': torch.zeros(1, 100, 1, device=device),
                'nav_features': torch.zeros(1, 256, device=device),
                'nav_instructions': torch.zeros(1, 150, device=device),
                'features_buffer': torch.zeros(1, 99, 512, device=device),
            }
            
            # Teacher推論（勾配なし）
            with torch.no_grad():
                teacher_output = teacher(inputs)
            
            # Student推論（勾配あり）
            student_output = student(**inputs)
            
            # 損失計算
            loss, kl_loss, mse_loss = distillation_loss(student_output, teacher_output)
            
            # 勾配更新
            optimizer.zero_grad()
            loss.backward()
            
            # 勾配クリッピング
            torch.nn.utils.clip_grad_norm_(student.parameters(), args.grad_clip)
            
            optimizer.step()
            
            # 統計更新
            total_loss += loss.item()
            total_kl_loss += kl_loss.item()
            total_mse_loss += mse_loss.item()
            num_batches += 1
            
            # プログレスバー更新
            if batch_idx % args.log_interval == 0:
                progress_bar.set_postfix({
                    'Loss': f'{loss.item():.4f}',
                    'KL': f'{kl_loss.item():.4f}',
                    'MSE': f'{mse_loss.item():.4f}'
                })
                
        except Exception as e:
            print(f"Error in batch {batch_idx}: {e}")
            continue
    
    # エポック統計
    avg_loss = total_loss / max(num_batches, 1)
    avg_kl_loss = total_kl_loss / max(num_batches, 1)
    avg_mse_loss = total_mse_loss / max(num_batches, 1)
    
    return avg_loss, avg_kl_loss, avg_mse_loss

def validate_epoch(teacher, student, val_loader, device):
    """検証"""
    
    student.eval()
    teacher.eval()
    
    total_loss = 0.0
    num_batches = 0
    
    with torch.no_grad():
        for batch_idx, batch_data in enumerate(val_loader):
            try:
                # バッチデータの展開（訓練と同様）
                stacked_frames, gt_plans, gt_plans_probs, segment_finished, worker_id = batch_data
                
                # 入力データの準備（numpy -> PyTorchテンソル変換）
                stacked_frames_tensor = torch.from_numpy(stacked_frames).float().to(device)
                
                # 最新フレームを取得してバッチ次元追加
                latest_frame = stacked_frames_tensor[-1]
                latest_frame_batch = latest_frame.unsqueeze(0)
                
                inputs = {
                    'input_imgs': latest_frame_batch,
                    'big_input_imgs': latest_frame_batch,
                    'desire': torch.zeros(1, 100, 8, device=device),
                    'traffic_convention': torch.ones(1, 2, device=device),
                    'lateral_control_params': torch.zeros(1, 2, device=device),
                    'prev_desired_curv': torch.zeros(1, 100, 1, device=device),
                    'nav_features': torch.zeros(1, 256, device=device),
                    'nav_instructions': torch.zeros(1, 150, device=device),
                    'features_buffer': torch.zeros(1, 99, 512, device=device),
                }
                
                # 推論
                teacher_output = teacher(inputs)
                student_output = student(**inputs)
                
                # 損失計算
                loss, _, _ = distillation_loss(student_output, teacher_output)
                
                total_loss += loss.item()
                num_batches += 1
                
                # 数バッチで十分
                if batch_idx >= 20:
                    break
                    
            except Exception as e:
                print(f"Validation error in batch {batch_idx}: {e}")
                continue
    
    avg_loss = total_loss / max(num_batches, 1)
    return avg_loss

def main():
    args = parse_args()
    device = setup_device(args.device)
    
    # ディレクトリ作成
    os.makedirs(args.save_dir, exist_ok=True)
    
    # wandb初期化
    if not args.no_wandb:
        wandb.init(project="openpilot-distillation", config=vars(args))
    
    print("Creating models...")
    teacher, student = create_distillation_models(args.onnx_model, args.student_hidden_dim)
    student = student.to(device)
    
    print("Creating data loaders...")
    train_loader, val_loader = create_data_loaders(args)
    
    # オプティマイザー
    optimizer = optim.AdamW(
        student.parameters(), 
        lr=args.lr, 
        weight_decay=args.weight_decay
    )
    
    # スケジューラー
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.8, patience=2, verbose=True
    )
    
    print("Starting training...")
    
    best_val_loss = float('inf')
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        
        # 訓練
        train_loss, train_kl_loss, train_mse_loss = train_epoch(
            teacher, student, train_loader, optimizer, device, args
        )
        
        # 検証
        val_loss = validate_epoch(teacher, student, val_loader, device)
        
        # スケジューラー更新
        scheduler.step(val_loss)
        
        # ログ出力
        print(f"Train Loss: {train_loss:.4f} (KL: {train_kl_loss:.4f}, MSE: {train_mse_loss:.4f})")
        print(f"Val Loss: {val_loss:.4f}")
        
        # wandbログ
        if not args.no_wandb:
            wandb.log({
                'epoch': epoch,
                'train/loss': train_loss,
                'train/kl_loss': train_kl_loss,
                'train/mse_loss': train_mse_loss,
                'val/loss': val_loss,
                'lr': optimizer.param_groups[0]['lr']
            })
        
        # チェックポイント保存
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint_path = os.path.join(args.save_dir, f'best_student_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': student.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
            }, checkpoint_path)
            print(f"Saved best model to {checkpoint_path}")
    
    print(f"\nTraining completed! Best validation loss: {best_val_loss:.4f}")

if __name__ == '__main__':
    main()