#!/bin/bash

# mypilot Installation Script for Comma Devices
# Author: KouMasuda
# Repository: https://github.com/KouMasuda/mypilot
# Usage: curl -fsSL https://raw.githubusercontent.com/KouMasuda/mypilot/release-c3/install.sh | bash

set -e

echo "=========================================="
echo "mypilot Installation for Comma Devices"
echo "=========================================="
echo "Author: KouMasuda"
echo "Repository: https://github.com/KouMasuda/mypilot"
echo "Branch: release-c3"
echo "Features: sunnypilot + MapTiler + Mapbox integration"
echo "=========================================="

# Check if running on Comma device
if [ ! -d "/data" ]; then
    echo "Error: This script should be run on a Comma device"
    echo "Make sure /data directory exists"
    exit 1
fi

# Show current installation info if openpilot exists
if [ -d "/data/openpilot" ]; then
    echo ""
    echo "Current installation information:"
    cd /data/openpilot
    echo "Git remote: $(git remote get-url origin 2>/dev/null || echo 'Unknown')"
    echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'Unknown')"
    echo "Last commit: $(git log --oneline -1 2>/dev/null || echo 'Unknown')"
    echo ""
    
    # Ask for confirmation
    echo "This will replace your current openpilot installation."
    read -p "Do you want to continue? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Create backup
    echo ""
    echo "Creating backup of current installation..."
    if [ -d "/data/openpilot_backup" ]; then
        echo "Removing old backup..."
        sudo rm -rf /data/openpilot_backup
    fi
    sudo cp -r /data/openpilot /data/openpilot_backup
    echo "Backup created at /data/openpilot_backup"
fi

echo ""
echo "Installing mypilot release-c3..."

# Navigate to /data
cd /data

# Remove current openpilot if it exists
if [ -d "openpilot" ]; then
    echo "Removing current openpilot installation..."
    sudo rm -rf openpilot
fi

# Clone mypilot repository
echo "Cloning mypilot repository..."
if ! git clone -b release-c3 --recurse-submodules https://github.com/KouMasuda/mypilot.git openpilot; then
    echo "Error: Failed to clone mypilot repository"
    echo "Please check your internet connection and try again"
    exit 1
fi

cd openpilot

# Set proper ownership and permissions
echo "Setting permissions..."
sudo chown -R comma:comma /data/openpilot
chmod +x /data/openpilot/launch_openpilot.sh 2>/dev/null || true
chmod +x /data/openpilot/launch_chffrplus.sh 2>/dev/null || true

echo ""
echo "=========================================="
echo "mypilot installation completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reboot your device: sudo reboot"
echo "2. After reboot, configure your API keys:"
echo ""
echo "   For MapTiler (map display):"
echo "   cd /data/openpilot && python -c \"from openpilot.common.params import Params; Params().put('CustomMapTilerTokenSk', 'YOUR_MAPTILER_API_KEY')\""
echo ""
echo "   For Mapbox (navigation and geocoding):"
echo "   cd /data/openpilot && python -c \"from openpilot.common.params import Params; Params().put('CustomMapboxTokenSk', 'YOUR_MAPBOX_API_KEY')\""
echo ""
echo "   To verify your settings:"
echo "   cd /data/openpilot && python -c \"from openpilot.common.params import Params; p = Params(); print('MapTiler:', p.get('CustomMapTilerTokenSk', encoding='utf8')); print('Mapbox:', p.get('CustomMapboxTokenSk', encoding='utf8'))\""
echo ""
echo "3. Configure other settings via the UI"
echo ""
echo "Features included:"
echo "• sunnypilot base functionality"
echo "• MapTiler integration for map display"
echo "• Mapbox integration for navigation and geocoding"
echo "• Enhanced navigation interface"
echo ""
echo "Alternative API key setup:"
echo "   Run the interactive setup script: cd /data/openpilot && python setup_api_keys.py"
echo ""
echo "Enjoy mypilot!"
echo ""
echo "For support, visit: https://github.com/KouMasuda/mypilot"
