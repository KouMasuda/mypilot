#!/usr/bin/env python3

# Quick API Key Setup Script for mypilot (MapTiler + Mapbox Secret only)
# This version bypasses the public token requirement

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

def setup_minimal_keys():
    params = Params()
    
    print("========================================")
    print("mypilot Minimal API Key Configuration")
    print("========================================")
    print("This script sets up minimal required keys only")
    
    # MapTiler API Key
    print("\n1. MapTiler API Key Setup (for map display)")
    print("   Get your key from: https://maptiler.com")
    maptiler_key = input("   Enter your MapTiler API key: ").strip()
    
    if maptiler_key:
        try:
            params.put('CustomMapTilerTokenSk', maptiler_key)
            print("   ✓ MapTiler API key saved successfully!")
        except Exception as e:
            print(f"   ✗ Error saving MapTiler key: {e}")
            return False
    else:
        print("   ✗ MapTiler key is required!")
        return False

    # Mapbox Secret Token (sk.)  
    print("\n2. Mapbox Secret Token Setup (starts with 'sk.')")
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
                return False
        else:
            print("   ✗ Error: Mapbox secret token must start with 'sk.'")
            return False
    else:
        print("   ✗ Mapbox secret token is required!")
        return False
    
    # Set a dummy public token to bypass the check
    print("\n3. Setting bypass for public token requirement...")
    try:
        # Use the secret token as public token (not ideal but works for bypass)
        dummy_public = "pk.eyJ1IjoiZHVtbXkiLCJhIjoiZHVtbXkifQ.dummy"
        params.put('CustomMapboxTokenPk', dummy_public)
        print("   ✓ Public token bypass configured!")
    except Exception as e:
        print(f"   ✗ Error setting bypass: {e}")
        return False
    
    # Enable OsmLocal to always use offline OSM maps (always set to 1)
    print("\n4. Enabling OSM Local mode (automatic)...")
    try:
        params.put('OsmLocal', '1')
        print("   ✓ OsmLocal automatically enabled permanently!")
        print("   ℹ This ensures offline OSM maps are always available")
    except Exception as e:
        print(f"   ✗ Error enabling OsmLocal: {e}")
        # Don't return False here since this is not critical for basic functionality
        print("   ⚠ Continuing without OsmLocal (navigation will still work)")
    
    print("\n✓ Minimal API key configuration completed!")
    print("Your mypilot should now work with MapTiler and Mapbox navigation.")
    print("OSM Local mode is enabled for offline map functionality.")
    
    return True

if __name__ == "__main__":
    # Check if running on comma device
    if not os.path.exists('/data/openpilot'):
        print("Error: This script should be run on a Comma device")
        print("Make sure /data/openpilot exists and mypilot is installed")
        sys.exit(1)
    
    success = setup_minimal_keys()
    if success:
        print("\n========================================")
        print("Setup completed! Try accessing the navigation interface.")
        print("If you get a valid Mapbox public token later, run the full setup_api_keys.py")
    else:
        print("\n========================================")
        print("Setup failed. Please check your API keys and try again.")
