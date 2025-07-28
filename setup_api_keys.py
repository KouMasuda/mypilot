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
    
    # Mapbox Public Token (pk.)
    print("\n2. Mapbox Public Token Setup (starts with 'pk.')")
    print("   Get your key from: https://mapbox.com → Account → Access tokens")
    print("   Use the 'Default public token' or create a new public token")
    mapbox_public_key = input("   Enter your Mapbox PUBLIC token (pk.xxx): ").strip()
    
    if mapbox_public_key:
        if mapbox_public_key.startswith('pk.'):
            try:
                params.put('CustomMapboxTokenPk', mapbox_public_key)
                print("   ✓ Mapbox public token saved successfully!")
            except Exception as e:
                print(f"   ✗ Error saving Mapbox public token: {e}")
        else:
            print("   ✗ Error: Mapbox public token must start with 'pk.'")
    else:
        print("   - Mapbox public token skipped")

    # Mapbox Secret Token (sk.)  
    print("\n3. Mapbox Secret Token Setup (starts with 'sk.')")
    print("   Get your key from: https://mapbox.com → Account → Access tokens")
    print("   Create a secret token with appropriate scopes")
    mapbox_secret_key = input("   Enter your Mapbox SECRET token (sk.xxx): ").strip()
    
    if mapbox_secret_key:
        if mapbox_secret_key.startswith('sk.'):
            try:
                params.put('CustomMapboxTokenSk', mapbox_secret_key)
                print("   ✓ Mapbox secret token saved successfully!")
            except Exception as e:
                print(f"   ✗ Error saving Mapbox secret token: {e}")
        else:
            print("   ✗ Error: Mapbox secret token must start with 'sk.'")
    else:
        print("   - Mapbox secret token skipped")
    
    # Verify settings
    print("\n4. Verification:")
    try:
        saved_maptiler = params.get('CustomMapTilerTokenSk', encoding='utf8')
        saved_mapbox_public = params.get('CustomMapboxTokenPk', encoding='utf8')
        saved_mapbox_secret = params.get('CustomMapboxTokenSk', encoding='utf8')
        
        print(f"   MapTiler key: {'✓ Set' if saved_maptiler else '✗ Not set'}")
        print(f"   Mapbox public token: {'✓ Set' if saved_mapbox_public else '✗ Not set'}")
        print(f"   Mapbox secret token: {'✓ Set' if saved_mapbox_secret else '✗ Not set'}")
        
        if saved_maptiler and saved_mapbox_public and saved_mapbox_secret:
            print("\n✓ All API keys configured successfully!")
            print("Your mypilot is now ready to use.")
        elif saved_maptiler or saved_mapbox_public or saved_mapbox_secret:
            print("\n⚠ Some API keys are missing.")
            print("For full functionality, you need:")
            print("  - MapTiler key (for map display)")
            print("  - Mapbox public token (for basic map features)")
            print("  - Mapbox secret token (for navigation and geocoding)")
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
