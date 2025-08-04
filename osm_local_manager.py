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

def check_models_status():
    print("========================================")
    print("OSM Models Status Check")
    print("========================================")
    
    # Check models directory
    models_paths = [
        '/data/media/0/models/',
        os.path.expanduser('~/.comma/media/0/models/')
    ]
    
    models_found = False
    total_models = 0
    
    for path in models_paths:
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if not f.startswith('.')]
            if files:
                print(f"✓ Models directory found: {path}")
                print(f"  📁 Models count: {len(files)}")
                for file in files[:5]:  # Show first 5 files
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path) / (1024*1024)  # MB
                        print(f"    - {file} ({size:.1f} MB)")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more files")
                models_found = True
                total_models = len(files)
                break
            else:
                print(f"⚠️  Models directory exists but empty: {path}")
    
    if not models_found:
        print("❌ No models found")
        print("💡 Models are required for OSM functionality")
        print("💡 Download models through Settings → Device → OSM Settings")
        return False, 0
    
    # Check critical models
    critical_models = ['supercombo.onnx', 'dmonitoring_model.onnx']
    missing_critical = []
    
    for path in models_paths:
        if os.path.exists(path):
            for model in critical_models:
                model_path = os.path.join(path, model)
                if not os.path.exists(model_path):
                    missing_critical.append(model)
            break
    
    if missing_critical:
        print(f"⚠️  Missing critical models: {', '.join(missing_critical)}")
        return False, total_models
    else:
        print("✅ Critical models present")
        return True, total_models

def check_osm_data_status():
    print("========================================")
    print("OSM Data Status Check")
    print("========================================")
    
    # Check OSM offline data
    osm_paths = [
        '/data/media/0/osm/offline/',
        os.path.expanduser('~/.comma/media/0/osm/offline/')
    ]
    
    osm_found = False
    total_size = 0
    
    for path in osm_paths:
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if not f.startswith('.')]
            if files:
                # Calculate total size
                for file in files:
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
                
                size_mb = total_size / (1024*1024)
                size_gb = size_mb / 1024
                
                print(f"✓ OSM data found: {path}")
                print(f"  📁 Files: {len(files)}")
                if size_gb > 1:
                    print(f"  💾 Total size: {size_gb:.1f} GB")
                else:
                    print(f"  💾 Total size: {size_mb:.1f} MB")
                
                osm_found = True
                break
            else:
                print(f"⚠️  OSM directory exists but empty: {path}")
    
    if not osm_found:
        print("❌ No OSM offline data found")
        print("💡 Download OSM data through Settings → Device → OSM Settings")
        print("💡 Select your country/region and download maps")
        return False
    
    return True

def comprehensive_osm_check():
    print("========================================")
    print("Comprehensive OSM System Check")
    print("========================================")
    
    # Check OsmLocal setting
    params = Params()
    osm_local = params.get('OsmLocal', encoding='utf8')
    print(f"1. OsmLocal setting: {osm_local or 'Not set'}")
    
    # Check location settings
    location_name = params.get('OsmLocationName', encoding='utf8')
    location_title = params.get('OsmLocationTitle', encoding='utf8')
    print(f"2. Location: {location_title or 'Not configured'} ({location_name or 'N/A'})")
    
    # Check models
    models_ok, models_count = check_models_status()
    
    # Check OSM data
    osm_data_ok = check_osm_data_status()
    
    # Check mapd binary
    mapd_paths = [
        '/data/openpilot/third_party/pfeiferj-mapd/mapd',
        '/data/openpilot/third_party/mapd_pfeiferj/mapd'
    ]
    
    mapd_found = False
    for path in mapd_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            print(f"✓ Mapd binary found: {path}")
            mapd_found = True
            break
    
    if not mapd_found:
        print("❌ Mapd binary not found or not executable")
    
    # Summary
    print("\n========================================")
    print("Summary & Recommendations")
    print("========================================")
    
    if osm_local == '1' and models_ok and osm_data_ok and mapd_found:
        print("🎉 OSM Local system appears fully functional!")
    else:
        print("⚠️  OSM Local system has issues:")
        if osm_local != '1':
            print("  • Enable OSM Local (option 1)")
        if not models_ok:
            print("  • Download required models")
        if not osm_data_ok:
            print("  • Download OSM map data for your region")
        if not mapd_found:
            print("  • Install mapd binary")
        
        print("\n💡 Next steps:")
        print("1. Open Settings → Device → OSM Settings")
        print("2. Select your country/region")
        print("3. Download maps and models")
        print("4. Enable OSM Local with this script")
    
    return osm_local == '1' and models_ok and osm_data_ok and mapd_found

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
    print("5) Check Models status")
    print("6) Check OSM Data status")
    print("7) Comprehensive system check")
    print("8) Exit")
    
    try:
        choice = input("Enter your choice (1-8): ").strip()
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
        models_ok, count = check_models_status()
        print(f"\nModels status: {'OK' if models_ok else 'Issues found'} ({count} files)")
        sys.exit(0)
    elif choice == '6':
        osm_ok = check_osm_data_status()
        print(f"\nOSM Data status: {'OK' if osm_ok else 'Issues found'}")
        sys.exit(0)
    elif choice == '7':
        comprehensive_osm_check()
        sys.exit(0)
    elif choice == '8':
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
