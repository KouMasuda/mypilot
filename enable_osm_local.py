#!/usr/bin/env python3

# OSM Local Manager for mypilot
# Comprehensive script to manage offline OSM maps functionality
# Supports enable, disable, and complete removal of OsmLocal settings

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

def enable_osm_local():
    params = Params()
    
    print("========================================")
    print("OSM Local Mode - Enabler")
    print("========================================")
    
    try:
        # Set OsmLocal to 1
        params.put('OsmLocal', '1')
        print("✓ OsmLocal enabled!")
        print("✓ Offline OSM maps will be available")
        
        # Verify the setting
        current_value = params.get('OsmLocal', encoding='utf8')
        if current_value == '1':
            print("✓ Setting verified successfully")
            return True
        else:
            print(f"⚠ Warning: Expected '1' but got '{current_value}'")
            return False
            
    except Exception as e:
        print(f"✗ Error enabling OsmLocal: {e}")
        return False

def disable_osm_local():
    params = Params()
    
    print("========================================")
    print("OSM Local Mode - Disabler")
    print("========================================")
    
    try:
        # Set OsmLocal to 0
        params.put('OsmLocal', '0')
        print("✓ OsmLocal disabled!")
        print("✓ Offline OSM maps functionality is turned off")
        
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

def check_osm_local_status():
    params = Params()
    
    print("========================================")
    print("OSM Local Mode - Current Status")
    print("========================================")
    
    try:
        current_value = params.get('OsmLocal', encoding='utf8')
        if current_value is None or current_value == '':
            print("✓ OsmLocal: Not set (using system default)")
            return "default"
        elif current_value == '1':
            print("✓ OsmLocal: ENABLED (offline OSM maps active)")
            return "enabled"
        elif current_value == '0':
            print("✓ OsmLocal: DISABLED (offline OSM maps inactive)")
            return "disabled"
        else:
            print(f"⚠ OsmLocal: Unknown value '{current_value}'")
            return "unknown"
            
    except Exception as e:
        print(f"✗ Error checking OsmLocal status: {e}")
        return "error"

if __name__ == "__main__":
    # Check if running on comma device
    if not os.path.exists('/data/openpilot'):
        print("Error: This script should be run on a Comma device")
        print("Make sure /data/openpilot exists and mypilot is installed")
        sys.exit(1)
    
    print("Choose an option:")
    print("1) Enable OSM Local (set to 1)")
    print("2) Disable OSM Local (set to 0)")
    print("3) Remove OSM Local setting completely")
    print("4) Check current OSM Local status")
    print("5) Exit")
    
    try:
        choice = input("Enter your choice (1-5): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    success = False
    
    if choice == '1':
        success = enable_osm_local()
    elif choice == '2':
        success = disable_osm_local()
    elif choice == '3':
        print("\n⚠ Warning: This will completely remove the OsmLocal setting.")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            success = remove_osm_local()
        else:
            print("Operation cancelled.")
            sys.exit(0)
    elif choice == '4':
        status = check_osm_local_status()
        print(f"\nCurrent status: {status}")
        sys.exit(0)
    elif choice == '5':
        print("Operation cancelled.")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)
    
    if success:
        print("\n========================================")
        print("OSM Local mode changes applied successfully!")
        print("No restart required - changes take effect immediately.")
    else:
        print("\n========================================")
        print("Failed to modify OSM Local mode.")
        print("Please check the error messages above.")
        sys.exit(1)
