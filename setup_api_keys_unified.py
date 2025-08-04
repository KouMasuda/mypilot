#!/usr/bin/env python3

# Unified API Key Setup Script for mypilot
# This script manages API keys via launch_env.sh for centralized configuration

import os
import sys
import re

# Add openpilot to path
sys.path.append('/data/openpilot')

try:
    from openpilot.common.params import Params
except ImportError:
    print("Error: Could not import openpilot.common.params")
    print("Make sure mypilot is properly installed in /data/openpilot")
    sys.exit(1)

def update_launch_env(launch_env_path, maptiler_token, mapbox_token):
    """Update launch_env.sh with the provided API keys"""
    try:
        # Read current content
        with open(launch_env_path, 'r') as f:
            content = f.read()
        
        # Replace the token lines
        content = re.sub(
            r'export MAPTILER_TOKEN="[^"]*"',
            f'export MAPTILER_TOKEN="{maptiler_token}"',
            content
        )
        content = re.sub(
            r'export MAPBOX_TOKEN="[^"]*"',
            f'export MAPBOX_TOKEN="{mapbox_token}"',
            content
        )
        
        # Write back
        with open(launch_env_path, 'w') as f:
            f.write(content)
        
        print("✓ API keys updated in launch_env.sh")
        print("✓ Keys will be active after openpilot restart")
        
    except Exception as e:
        print(f"❌ Error updating launch_env.sh: {e}")
        print("Please edit the file manually")

def setup_via_launch_env(launch_env_path):
    """Interactive setup via launch_env.sh"""
    print("\n========================================")
    print("Setting up API keys in launch_env.sh")
    print("========================================")
    
    print("This will update your launch_env.sh file with API keys.")
    print("Get your API keys from:")
    print("• MapTiler: https://maptiler.com")
    print("• Mapbox: https://mapbox.com → Account → Access tokens (secret token starting with 'sk.')")
    
    maptiler_key = input("\nEnter your MapTiler API key: ").strip()
    if not maptiler_key:
        print("❌ MapTiler key is required!")
        return
        
    mapbox_key = input("Enter your Mapbox secret token (sk.xxx): ").strip()
    if not mapbox_key or not mapbox_key.startswith('sk.'):
        print("❌ Valid Mapbox secret token is required!")
        return
    
    update_launch_env(launch_env_path, maptiler_key, mapbox_key)

def show_manual_instructions(launch_env_path):
    """Show manual setup instructions for launch_env.sh"""
    print("\n========================================")
    print("Manual Setup Instructions")
    print("========================================")
    
    print(f"\n1. Edit the file: {launch_env_path}")
    print("2. Set your API keys in the following lines:")
    print('   export MAPTILER_TOKEN="your_maptiler_api_key_here"')
    print('   export MAPBOX_TOKEN="your_mapbox_secret_token_here"')
    print("\n3. Save the file and restart openpilot")
    
    print("\nTo edit the file now:")
    print(f"   nano {launch_env_path}")
    print("or")
    print(f"   vi {launch_env_path}")
    
    print("\nGet your API keys from:")
    print("• MapTiler: https://maptiler.com")
    print("• Mapbox: https://mapbox.com → Account → Access tokens")
    print("  (Use a secret token starting with 'sk.')")
    
    print("\n✓ Please restart openpilot after setting the keys")

def setup_minimal_keys():
    """Quick minimal setup using device params (bypasses public token requirement)"""
    params = Params()
    
    print("\n========================================")
    print("Quick Minimal Setup (Device Params)")
    print("========================================")
    print("This sets up minimal required keys in device storage")
    print("Note: Environment variables in launch_env.sh take priority")
    
    # MapTiler API Key
    print("\n1. MapTiler API Key (required for map display)")
    print("   Get your key from: https://maptiler.com")
    maptiler_key = input("   Enter your MapTiler API key: ").strip()
    
    if not maptiler_key:
        print("   ✗ MapTiler key is required!")
        return False

    # Mapbox Secret Token
    print("\n2. Mapbox Secret Token (required for navigation)")
    print("   Get your key from: https://mapbox.com → Account → Access tokens")
    print("   Create a secret token with appropriate scopes")
    mapbox_secret_key = input("   Enter your Mapbox SECRET token (sk.xxx): ").strip()
    
    if not mapbox_secret_key or not mapbox_secret_key.startswith('sk.'):
        print("   ✗ Valid Mapbox secret token (starting with 'sk.') is required!")
        return False

    # Save keys
    try:
        params.put('CustomMapTilerTokenSk', maptiler_key.encode('utf8'))
        print("   ✓ MapTiler API key saved!")
        
        params.put('CustomMapboxTokenSk', mapbox_secret_key.encode('utf8'))
        print("   ✓ Mapbox secret token saved!")
        
        # Set a dummy public token to bypass requirement
        dummy_public = "pk.eyJ1IjoiZHVtbXkiLCJhIjoiZHVtbXkifQ.dummy"
        params.put('CustomMapboxTokenPk', dummy_public.encode('utf8'))
        print("   ✓ Public token bypass configured!")
        
        print("\n✓ Minimal setup completed!")
        print("Your mypilot should now work with basic functionality.")
        return True
        
    except Exception as e:
        print(f"   ✗ Error saving keys: {e}")
        return False

def verify_settings():
    """Verify and display current API key settings"""
    print("\n========================================")
    print("Current API Key Status")
    print("========================================")
    
    # Check environment variables first
    env_maptiler = os.environ.get('MAPTILER_TOKEN', '')
    env_mapbox = os.environ.get('MAPBOX_TOKEN', '')
    
    print("\nEnvironment Variables (launch_env.sh):")
    print(f"   MAPTILER_TOKEN: {'✓ Set' if env_maptiler else '✗ Not set'}")
    if env_maptiler:
        print(f"      Value: {env_maptiler[:8]}...")
    print(f"   MAPBOX_TOKEN: {'✓ Set' if env_mapbox else '✗ Not set'}")
    if env_mapbox:
        print(f"      Value: {env_mapbox[:8]}...")
    
    # Check device parameters
    try:
        params = Params()
        
        print("\nDevice Parameters:")
        saved_maptiler = None
        saved_mapbox_public = None
        saved_mapbox_secret = None
        
        try:
            saved_maptiler = params.get('CustomMapTilerTokenSk')
            if saved_maptiler:
                saved_maptiler = saved_maptiler.decode('utf8') if isinstance(saved_maptiler, bytes) else saved_maptiler
        except Exception:
            saved_maptiler = None
            
        try:
            saved_mapbox_public = params.get('CustomMapboxTokenPk')
            if saved_mapbox_public:
                saved_mapbox_public = saved_mapbox_public.decode('utf8') if isinstance(saved_mapbox_public, bytes) else saved_mapbox_public
        except Exception:
            saved_mapbox_public = None
            
        try:
            saved_mapbox_secret = params.get('CustomMapboxTokenSk')
            if saved_mapbox_secret:
                saved_mapbox_secret = saved_mapbox_secret.decode('utf8') if isinstance(saved_mapbox_secret, bytes) else saved_mapbox_secret
        except Exception:
            saved_mapbox_secret = None
        
        print(f"   MapTiler key: {'✓ Set' if saved_maptiler else '✗ Not set'}")
        print(f"   Mapbox public token: {'✓ Set' if saved_mapbox_public else '✗ Not set'}")
        print(f"   Mapbox secret token: {'✓ Set' if saved_mapbox_secret else '✗ Not set'}")
        
        # Determine effective configuration
        print("\nEffective Configuration (Environment takes priority):")
        effective_maptiler = env_maptiler or saved_maptiler
        effective_mapbox = env_mapbox or saved_mapbox_secret
        
        print(f"   MapTiler: {'✓ Available' if effective_maptiler else '✗ Missing'}")
        print(f"   Mapbox: {'✓ Available' if effective_mapbox else '✗ Missing'}")
        
        if effective_maptiler and effective_mapbox:
            print("\n✓ All API keys configured successfully!")
            print("Your mypilot is ready to use.")
        else:
            print("\n⚠ Some API keys are missing.")
            print("For full functionality, you need:")
            print("  - MapTiler key (for map display)")
            print("  - Mapbox secret token (for navigation and geocoding)")
            
    except Exception as e:
        print(f"   Error checking device parameters: {e}")

def setup_api_keys():
    print("========================================")
    print("mypilot API Key Configuration")
    print("========================================")
    print("This script helps you configure API keys for mypilot.")
    print("API keys are managed in launch_env.sh for centralized configuration.")
    print("")
    
    # Check if launch_env.sh exists
    launch_env_path = "/data/openpilot/launch_env.sh"
    if not os.path.exists(launch_env_path):
        print(f"❌ Error: {launch_env_path} not found!")
        print("Make sure mypilot is properly installed.")
        return
    
    # Show current status
    verify_settings()
    
    print("\nChoose an option:")
    print("1. Set API keys in launch_env.sh (recommended)")
    print("2. Show manual setup instructions")
    print("3. Quick setup via device params (bypasses public token requirement)")
    print("4. Just verify current settings again")
    print("5. Exit")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == "1":
        setup_via_launch_env(launch_env_path)
    elif choice == "2":
        show_manual_instructions(launch_env_path)
    elif choice == "3":
        setup_minimal_keys()
    elif choice == "4":
        verify_settings()
    else:
        print("Exiting...")
        return
    
    print("\n========================================")

if __name__ == "__main__":
    # Check if running on comma device
    if not os.path.exists('/data/openpilot'):
        print("Error: This script should be run on a Comma device")
        print("Make sure /data/openpilot exists and mypilot is installed")
        sys.exit(1)
    
    setup_api_keys()
