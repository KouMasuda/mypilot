#!/usr/bin/env python3

# OSM Local Diagnostic Script for mypilot
# Checks all requirements for OSM Local functionality

import json
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

def check_osm_local_status():
    params = Params()
    
    print("========================================")
    print("OSM Local Diagnostic Report")
    print("========================================")
    
    # Check OsmLocal parameter
    osm_local = params.get('OsmLocal', encoding='utf8')
    print(f"1. OsmLocal parameter: {osm_local or 'Not set'}")
    
    if osm_local != '1':
        print("   ❌ OSM Local is not enabled")
        print("   💡 Run: osm_local_manager.py and select option 1")
        return False
    else:
        print("   ✅ OSM Local is enabled")
    
    # Check location settings
    location_name = params.get('OsmLocationName', encoding='utf8')
    location_title = params.get('OsmLocationTitle', encoding='utf8')
    print(f"\n2. Location settings:")
    print(f"   - Location Name: {location_name or 'Not set'}")
    print(f"   - Location Title: {location_title or 'Not set'}")
    
    if not location_name or not location_title:
        print("   ❌ Location not configured")
        print("   💡 Use the Settings app to select a country/region")
        return False
    else:
        print("   ✅ Location configured")
    
    # Check mapd binary
    mapd_paths = [
        '/data/openpilot/third_party/pfeiferj-mapd/mapd',
        '/data/openpilot/third_party/mapd_pfeiferj/mapd'
    ]
    
    mapd_exists = False
    print(f"\n3. Mapd binary check:")
    for path in mapd_paths:
        if os.path.exists(path):
            print(f"   ✅ Found mapd at: {path}")
            mapd_exists = True
            break
    
    if not mapd_exists:
        print("   ❌ Mapd binary not found")
        print("   💡 mapd binary needs to be installed")
        return False
    
    # Check OSM data directory
    osm_data_paths = [
        '/data/media/0/osm/offline/',
        os.path.expanduser('~/.comma/media/0/osm/offline/')
    ]
    
    osm_data_exists = False
    print(f"\n4. OSM data directory check:")
    for path in osm_data_paths:
        if os.path.exists(path):
            files = os.listdir(path)
            if files:
                print(f"   ✅ OSM data found at: {path}")
                print(f"   📁 Files: {len(files)} items")
                osm_data_exists = True
                break
            else:
                print(f"   ⚠️  OSM directory exists but empty: {path}")
    
    if not osm_data_exists:
        print("   ❌ No OSM data found")
        print("   💡 Download maps through Settings app")
        return False
    
    # Check mapd database
    mapd_data_paths = [
        '/data/mapd_data/',
        '/data/mapd_data/db/'
    ]
    
    mapd_data_exists = False
    print(f"\n5. Mapd database check:")
    for path in mapd_data_paths:
        if os.path.exists(path):
            files = os.listdir(path)
            if files:
                print(f"   ✅ Mapd database found at: {path}")
                print(f"   📁 Files: {len(files)} items")
                mapd_data_exists = True
                break
    
    if not mapd_data_exists:
        print("   ❌ No mapd database found")
        print("   💡 Database will be created when maps are downloaded")
        return False
    
    # Check download status
    print(f"\n6. Download status check:")
    osm_db_updates = params.get_bool("OsmDbUpdatesCheck")
    osm_download_locations = params.get("OSMDownloadLocations", encoding='utf8')
    
    print(f"   - Updates check: {osm_db_updates}")
    print(f"   - Download locations: {osm_download_locations or 'None'}")
    
    if osm_db_updates:
        print("   ⚠️  Download in progress")
        return False
    elif osm_download_locations:
        print("   ⚠️  Download queue not empty")
        return False
    else:
        print("   ✅ No active downloads")
    
    # Summary
    print(f"\n========================================")
    print("✅ OSM Local appears to be properly configured!")
    print("If maps still don't display, check:")
    print("1. Network connectivity for initial setup")
    print("2. Storage space for map data")
    print("3. Try restarting the device")
    print("========================================")
    
    return True

def show_solution_steps():
    print("\n========================================")
    print("🔧 Steps to fix OSM Local issues:")
    print("========================================")
    print("1. Enable OSM Local:")
    print("   python3 osm_local_manager.py")
    print("   Select option 1")
    print("")
    print("2. Select country/region:")
    print("   Open Settings app → Device → Developer")
    print("   Find OSM settings and select your country")
    print("")
    print("3. Download maps:")
    print("   In OSM settings, tap 'UPDATE' to download")
    print("   Wait for download to complete")
    print("")
    print("4. Verify installation:")
    print("   python3 osm_diagnostic.py")
    print("")
    print("5. If still not working:")
    print("   - Check storage space (need several GB)")
    print("   - Check network connection")
    print("   - Try downloading a smaller region first")
    print("   - Restart the device after download")

if __name__ == "__main__":
    # Check if running on comma device
    if not os.path.exists('/data/openpilot'):
        print("Error: This script should be run on a Comma device")
        print("Make sure /data/openpilot exists and mypilot is installed")
        sys.exit(1)
    
    success = check_osm_local_status()
    
    if not success:
        show_solution_steps()
    
    sys.exit(0 if success else 1)
