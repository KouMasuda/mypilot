#!/bin/bash

# sunnypilot Installation Script for Comma Devices
# Usage: curl -fsSL https://raw.githubusercontent.com/KouMasuda/mypilot/release-c3/install_sunnypilot.sh | bash

set -e

echo "=========================================="
echo "sunnypilot Installation for Comma Devices"
echo "=========================================="
echo "Author: KouMasuda"
echo "Repository: https://github.com/KouMasuda/mypilot"
echo "=========================================="

# Check if running on Comma device
if [ ! -d "/data/openpilot" ]; then
    echo "Error: This script should be run on a Comma device"
    echo "Make sure /data/openpilot exists"
    exit 1
fi

# Show current installation info
echo "Current installation information:"
if [ -d "/data/openpilot" ]; then
    cd /data/openpilot
    echo "Git remote: $(git remote get-url origin 2>/dev/null || echo 'Unknown')"
    echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'Unknown')"
    echo "Last commit: $(git log --oneline -1 2>/dev/null || echo 'Unknown')"
fi
echo ""

# Function to backup current installation
backup_current() {
    echo "Creating backup of current installation..."
    if [ -d "/data/openpilot_backup" ]; then
        echo "Removing old backup..."
        sudo rm -rf /data/openpilot_backup
    fi
    sudo cp -r /data/openpilot /data/openpilot_backup
    echo "Backup created at /data/openpilot_backup"
}

# Function to install via official installer (Method 1)
install_official() {
    echo "Using official sunnypilot installer..."
    curl -fsSL https://smiskol.com/fork/sunnypilot | bash
}

# Function to install mypilot release-c3 (Method 2)
install_mypilot() {
    echo "Installing mypilot release-c3..."
    
    # Backup current installation
    backup_current
    
    # Navigate to /data
    cd /data
    
    # Remove current openpilot
    sudo rm -rf openpilot
    
    # Clone mypilot repository
    echo "Cloning mypilot repository..."
    git clone -b release-c3 --recurse-submodules https://github.com/KouMasuda/mypilot.git openpilot
    
    cd openpilot
    
    # Set proper ownership and permissions
    echo "Setting permissions..."
    sudo chown -R comma:comma /data/openpilot
    chmod +x /data/openpilot/launch_openpilot.sh
    chmod +x /data/openpilot/launch_chffrplus.sh
    
    echo "mypilot installation completed!"
}

# Function to install manually from sunnypilot (Method 3)
install_manual() {
    echo "Manual installation of sunnypilot..."
    
    # Backup current installation
    backup_current
    
    # Navigate to /data
    cd /data
    
    # Remove current openpilot
    sudo rm -rf openpilot
    
    # Clone sunnypilot
    echo "Cloning sunnypilot repository..."
    git clone https://github.com/sunnypilot/sunnypilot.git openpilot
    
    cd openpilot
    
    # Checkout master branch
    echo "Switching to master branch..."
    git checkout master
    
    # Initialize submodules
    echo "Initializing submodules..."
    git submodule update --init --recursive
    
    # Set proper ownership and permissions
    echo "Setting permissions..."
    sudo chown -R comma:comma /data/openpilot
    chmod +x /data/openpilot/launch_openpilot.sh
    chmod +x /data/openpilot/launch_chffrplus.sh
    
    echo "Manual installation completed!"
}

# Main installation menu
echo ""
echo "Choose installation method:"
echo "1) Official sunnypilot installer (recommended)"
echo "2) mypilot release-c3 (KouMasuda/mypilot)"
echo "3) Manual sunnypilot git installation"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        install_official
        ;;
    2)
        install_mypilot
        ;;
    3)
        install_manual
        ;;
    4)
        echo "Installation cancelled."
        exit 0
        ;;
    *)
        echo "Invalid choice. Using mypilot installer..."
        install_mypilot
        ;;
esac

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reboot your device: sudo reboot"
echo "2. Configure sunnypilot settings via the UI"
echo "3. For MapTiler integration, set your API key:"
echo "   python -c \"from openpilot.common.params import Params; Params().put('CustomMapTilerTokenSk', 'YOUR_API_KEY')\""
echo "4. For Mapbox API key (if needed):"
echo "   python -c \"from openpilot.common.params import Params; Params().put('CustomMapboxTokenSk', 'YOUR_MAPBOX_API_KEY')\""
echo ""
echo "Enjoy mypilot with MapTiler integration!"
