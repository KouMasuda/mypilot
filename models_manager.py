#!/usr/bin/env python3

# OSM Models Downloader for mypilot
# DEPRECATED: Use sunnypilot's UI instead for model downloads
# This script is kept for reference and emergency use only

import os
import sys
import json
from pathlib import Path

import requests

def get_models_directory():
    """Get the appropriate models directory for current platform"""
    if os.path.exists('/data/media/0/'):
        return '/data/media/0/models/'
    else:
        return os.path.expanduser('~/.comma/media/0/models/')

def check_internet_connection():
    """Check if internet connection is available"""
    try:
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def fetch_latest_models_info():
    """Fetch latest models information from sunnypilot API"""
    try:
        response = requests.get("https://docs.sunnypilot.ai/models_v5.json", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to fetch latest models info: {e}")
        return None

def show_recommended_method():
    """Show the recommended way to download models"""
    print("========================================")
    print("🔄 MODEL DOWNLOAD - RECOMMENDED METHOD")
    print("========================================")
    print("📱 Use the sunnypilot UI instead:")
    print("   1. Go to Settings → Device → Models")
    print("   2. Press 'SELECT' next to 'Current Model'")
    print("   3. Choose from available model bundles")
    print("   4. Download will start automatically")
    print()
    print("🌐 Models are now sourced from:")
    print("   https://docs.sunnypilot.ai/models_v5.json")
    print()
    print("✅ Benefits of using UI:")
    print("   • Latest model versions")
    print("   • Hash verification")
    print("   • Progress tracking")
    print("   • Automatic metadata download")
    print("   • Model bundle management")

def check_existing_models():
    """Check which models are already present"""
    print("========================================")
    print("📦 EXISTING MODELS CHECK")
    print("========================================")
    
    models_dir = get_models_directory()
    
    if not os.path.exists(models_dir):
        print(f"❌ Models directory does not exist: {models_dir}")
        print("💡 Create it by downloading models through the UI")
        return
    
    print(f"📁 Checking: {models_dir}")
    
    all_files = [f for f in os.listdir(models_dir) if os.path.isfile(os.path.join(models_dir, f))]
    onnx_files = [f for f in all_files if f.endswith('.onnx')]
    
    if not all_files:
        print("❌ No model files found")
        return
    
    print(f"✅ Found {len(all_files)} file(s) total:")
    print(f"   📊 ONNX models: {len(onnx_files)}")
    print(f"   📄 Other files: {len(all_files) - len(onnx_files)}")
    print()
    
    for file in all_files:
        file_path = os.path.join(models_dir, file)
        size_mb = os.path.getsize(file_path) / (1024*1024)
        
        if file.endswith('.onnx'):
            print(f"  🧠 {file} ({size_mb:.1f} MB)")
        elif file.endswith('.pkl'):
            print(f"  📋 {file} ({size_mb:.1f} MB) - Metadata")
        elif file.endswith('.thneed'):
            print(f"  ⚡ {file} ({size_mb:.1f} MB) - GPU optimized")
        elif file.endswith('.dlc'):
            print(f"  � {file} ({size_mb:.1f} MB) - DSP optimized")
        else:
            print(f"  📄 {file} ({size_mb:.1f} MB)")

def show_api_info():
    """Show information about the sunnypilot models API"""
    print("========================================")
    print("🌐 SUNNYPILOT MODELS API INFO")
    print("========================================")
    
    if not check_internet_connection():
        print("❌ No internet connection - cannot fetch API info")
        return
    
    print("🔍 Fetching latest model information...")
    models_data = fetch_latest_models_info()
    
    if not models_data:
        print("❌ Failed to fetch models information")
        return
    
    print("✅ Successfully connected to sunnypilot API")
    print()
    print("📊 Available model bundles:")
    
    if isinstance(models_data, dict):
        for bundle_name, bundle_info in models_data.items():
            print(f"   📦 {bundle_name}")
            if isinstance(bundle_info, dict) and 'models' in bundle_info:
                models = bundle_info['models']
                print(f"      • Models: {len(models)}")
                for model in models[:3]:  # Show first 3 models
                    if isinstance(model, dict):
                        model_type = model.get('type', 'unknown')
                        print(f"        - {model_type}")
                if len(models) > 3:
                    print(f"        - ... and {len(models) - 3} more")
            print()

def emergency_download_notice():
    """Show emergency download information"""
    print("========================================")
    print("🚨 EMERGENCY DOWNLOAD INFO")
    print("========================================")
    print("⚠️  This script no longer downloads models directly")
    print("🔄 For emergency model download:")
    print()
    print("1. Use SSH/ADB to access device")
    print("2. Navigate to: /data/media/0/models/")
    print("3. Download manually with curl/wget:")
    print()
    print("   Example commands:")
    print("   cd /data/media/0/models/")
    print("   curl -O [model_url_from_api]")
    print()
    print("🌐 Get URLs from: https://docs.sunnypilot.ai/models_v5.json")
    print("� But seriously, use the UI instead! 😊")

if __name__ == "__main__":
    print("🌞 SUNNYPILOT MODELS MANAGER")
    print("============================")
    print()
    print("📢 IMPORTANT: This script is deprecated!")
    print("   Use the sunnypilot UI for model downloads")
    print()
    print("Available options:")
    print("1) 📱 Show recommended download method")
    print("2) 📦 Check existing models")
    print("3) 🌐 Show API information")
    print("4) 🚨 Emergency download info")
    print("5) ❌ Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-5): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    print()
    
    if choice == '1':
        show_recommended_method()
    elif choice == '2':
        check_existing_models()
    elif choice == '3':
        show_api_info()
    elif choice == '4':
        emergency_download_notice()
    elif choice == '5':
        print("👋 Goodbye! Use the UI for model downloads!")
    else:
        print("❌ Invalid choice.")
        show_recommended_method()
