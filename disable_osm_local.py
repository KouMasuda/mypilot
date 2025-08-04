#!/usr/bin/env python3

# Script to disable OsmLocal for mypilot
# This disables offline OSM maps functionality

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

def disable_osm_local():
    params = Params()
    
    print("========================================")
    print("OSM Local Mode - Disabler")
    print("========================================")
    
    try:
        # Set OsmLocal to 0 (disable)
        params.put('OsmLocal', '0')
        print("✓ OsmLocal disabled!")
        print("✓ Offline OSM maps functionality is now turned off")
        
        # Verify the setting
        current_value = params.get('OsmLocal', encoding='utf8')
        if current_value == '0':
            print("✓ Setting verified successfully")
            return True
        else:
            print(f"⚠ Warning: Expected '0' but got '{current_value}'")
            return False
            
    except Exception as e:
        print(f"✗ Error disabling OsmLocal: {e}")
        return False

def remove_osm_local():
    params = Params()
    
    print("========================================")
    print("OSM Local Mode - Complete Removal")
    print("========================================")
    
    try:
        # Completely remove OsmLocal parameter
        params.remove('OsmLocal')
        print("✓ OsmLocal parameter completely removed!")
        print("✓ System will use default OSM behavior")
        
        # Verify the removal
        current_value = params.get('OsmLocal', encoding='utf8')
        if current_value is None or current_value == '':
            print("✓ Removal verified successfully")
            return True
        else:
            print(f"⚠ Warning: Parameter still exists with value '{current_value}'")
            return False
            
    except Exception as e:
        print(f"✗ Error removing OsmLocal: {e}")
        return False

if __name__ == "__main__":
    # Check if running on comma device
    if not os.path.exists('/data/openpilot'):
        print("Error: This script should be run on a Comma device")
        print("Make sure /data/openpilot exists and mypilot is installed")
        sys.exit(1)
    
    print("Choose an option:")
    print("1) Disable OSM Local (set to 0)")
    print("2) Completely remove OSM Local setting")
    print("3) Exit")
    
    try:
        choice = input("Enter your choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    success = False
    
    if choice == '1':
        success = disable_osm_local()
    elif choice == '2':
        success = remove_osm_local()
    elif choice == '3':
        print("Operation cancelled.")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)
    
    if success:
        print("\n========================================")
        print("OSM Local mode changes applied successfully!")
        print("Your device will no longer use offline OSM functionality.")
        print("No restart required - changes take effect immediately.")
    else:
        print("\n========================================")
        print("Failed to modify OSM Local mode.")
        print("Please check the error messages above.")
        sys.exit(1)
