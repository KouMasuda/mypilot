#!/usr/bin/env python3

# API Key Setup Script for mypilot
# Usage: Run this script after mypilot installation to configure API keys

import os
import sys

# Add openpilot to path
sys.path.append('/data/openpilot')

try:
    from openpilot.common.params import Params
except ImportError:
    print("Error: Could not import openpilot.common.params")
    print("Make sure mypilot is properly installed in /data/openpilot")
    sys.exit(1)

def setup_api_keys():
    params = Params()
    
    print("========================================")
    print("mypilot API Key Configuration")
    print("========================================")
    
    # MapTiler API Key
    print("\n1. MapTiler API Key Setup (for map display)")
    print("   Get your key from: https://maptiler.com")
    maptiler_key = input("   Enter your MapTiler API key (or press Enter to skip): ").strip()
    
    if maptiler_key:
        try:
            params.put('CustomMapTilerTokenSk', maptiler_key)
            print("   ✓ MapTiler API key saved successfully!")
        except Exception as e:
            print(f"   ✗ Error saving MapTiler key: {e}")
    else:
        print("   - MapTiler key skipped")
    
    # Mapbox API Key  
    print("\n2. Mapbox API Key Setup (for navigation and geocoding)")
    print("   Get your key from: https://mapbox.com")
    mapbox_key = input("   Enter your Mapbox API key (or press Enter to skip): ").strip()
    
    if mapbox_key:
        try:
            params.put('CustomMapboxTokenSk', mapbox_key)
            print("   ✓ Mapbox API key saved successfully!")
        except Exception as e:
            print(f"   ✗ Error saving Mapbox key: {e}")
    else:
        print("   - Mapbox key skipped")
    
    # Verify settings
    print("\n3. Verification:")
    try:
        saved_maptiler = params.get('CustomMapTilerTokenSk', encoding='utf8')
        saved_mapbox = params.get('CustomMapboxTokenSk', encoding='utf8')
        
        print(f"   MapTiler key: {'✓ Set' if saved_maptiler else '✗ Not set'}")
        print(f"   Mapbox key: {'✓ Set' if saved_mapbox else '✗ Not set'}")
        
        if saved_maptiler or saved_mapbox:
            print("\n✓ API key configuration completed!")
            print("Your mypilot is now ready to use.")
        else:
            print("\n⚠ No API keys were configured.")
            print("You can run this script again anytime to set them up.")
            
    except Exception as e:
        print(f"   Error verifying settings: {e}")
    
    print("\n========================================")

if __name__ == "__main__":
    # Check if running on comma device
    if not os.path.exists('/data/openpilot'):
        print("Error: This script should be run on a Comma device")
        print("Make sure /data/openpilot exists and mypilot is installed")
        sys.exit(1)
    
    setup_api_keys()
