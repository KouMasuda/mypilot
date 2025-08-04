#!/usr/bin/env python3

# OSM Models Downloader for mypilot
# Downloads required AI models for OSM functionality

import os
import sys
from pathlib import Path

import requests

# Add openpilot to path
sys.path.append('/data/openpilot')

try:
    from openpilot.common.params import Params
except ImportError:
    print("Error: Could not import openpilot.common.params")
    print("Make sure mypilot is properly installed in /data/openpilot")
    sys.exit(1)

# Model download URLs (these are examples - actual URLs may vary)
MODELS_INFO = {
    'supercombo.onnx': {
        'url': 'https://github.com/commaai/openpilot/releases/download/v0.9.4/supercombo.onnx',
        'size_mb': 50,
        'description': 'Main driving model'
    },
    'dmonitoring_model.onnx': {
        'url': 'https://github.com/commaai/openpilot/releases/download/v0.9.4/dmonitoring_model.onnx',
        'size_mb': 5,
        'description': 'Driver monitoring model'
    }
}

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
    except:
        return False

def download_model(model_name, model_info, models_dir):
    """Download a single model file"""
    model_path = os.path.join(models_dir, model_name)
    
    # Check if model already exists
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024*1024)
        print(f"✓ {model_name} already exists ({size_mb:.1f} MB)")
        return True
    
    print(f"⬇️  Downloading {model_name} ({model_info['size_mb']} MB)...")
    print(f"   {model_info['description']}")
    
    try:
        response = requests.get(model_info['url'], stream=True, timeout=30)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(models_dir, exist_ok=True)
        
        # Download with progress
        with open(model_path, 'wb') as f:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
        
        print(f"✅ {model_name} downloaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {model_name}: {e}")
        # Clean up partial download
        if os.path.exists(model_path):
            os.remove(model_path)
        return False

def download_all_models():
    """Download all required models"""
    print("========================================")
    print("OSM Models Downloader")
    print("========================================")
    
    # Check internet connection
    if not check_internet_connection():
        print("❌ No internet connection available")
        print("💡 Connect to WiFi or cellular data and try again")
        return False
    
    print("✅ Internet connection available")
    
    models_dir = get_models_directory()
    print(f"📁 Models directory: {models_dir}")
    
    # Download each model
    success_count = 0
    total_count = len(MODELS_INFO)
    
    for model_name, model_info in MODELS_INFO.items():
        if download_model(model_name, model_info, models_dir):
            success_count += 1
    
    # Summary
    print("\n========================================")
    print("Download Summary")
    print("========================================")
    
    if success_count == total_count:
        print(f"🎉 All {total_count} models downloaded successfully!")
        print("✅ OSM models are ready for use")
        return True
    else:
        print(f"⚠️  Downloaded {success_count}/{total_count} models")
        print("❌ Some models failed to download")
        print("💡 Check internet connection and try again")
        return False

def show_models_info():
    """Show information about available models"""
    print("========================================")
    print("Available OSM Models")
    print("========================================")
    
    total_size = 0
    for model_name, model_info in MODELS_INFO.items():
        print(f"📦 {model_name}")
        print(f"   • Size: {model_info['size_mb']} MB")
        print(f"   • Description: {model_info['description']}")
        print(f"   • URL: {model_info['url']}")
        print()
        total_size += model_info['size_mb']
    
    print(f"📊 Total download size: {total_size} MB")
    print("💡 These models are required for OSM Local functionality")

def check_existing_models():
    """Check which models are already present"""
    print("========================================")
    print("Existing Models Check")
    print("========================================")
    
    models_dir = get_models_directory()
    
    if not os.path.exists(models_dir):
        print(f"❌ Models directory does not exist: {models_dir}")
        return
    
    print(f"📁 Checking: {models_dir}")
    
    existing_files = [f for f in os.listdir(models_dir) if f.endswith('.onnx')]
    
    if not existing_files:
        print("❌ No ONNX models found")
        return
    
    print(f"✅ Found {len(existing_files)} ONNX model(s):")
    
    for file in existing_files:
        file_path = os.path.join(models_dir, file)
        size_mb = os.path.getsize(file_path) / (1024*1024)
        
        # Check if it's a known model
        if file in MODELS_INFO:
            print(f"  ✅ {file} ({size_mb:.1f} MB) - {MODELS_INFO[file]['description']}")
        else:
            print(f"  📦 {file} ({size_mb:.1f} MB) - Unknown model")

if __name__ == "__main__":
    # Check if running on comma device or development environment
    if not (os.path.exists('/data/openpilot') or os.path.exists(os.path.expanduser('~/.comma'))):
        print("Error: This script should be run on a Comma device or development environment")
        sys.exit(1)
    
    print("OSM Models Manager")
    print("==================")
    print("1) Check existing models")
    print("2) Show available models info")
    print("3) Download all models")
    print("4) Exit")
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    if choice == '1':
        check_existing_models()
    elif choice == '2':
        show_models_info()
    elif choice == '3':
        success = download_all_models()
        if not success:
            sys.exit(1)
    elif choice == '4':
        print("Goodbye!")
    else:
        print("Invalid choice.")
        sys.exit(1)
