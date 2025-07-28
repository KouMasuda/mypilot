#!/bin/bash

# sunnypilot installation for Comma devices
# This script sets up sunnypilot as the default openpilot installation

echo "Setting up sunnypilot as default openpilot installation..."

# Method 1: Using official sunnypilot installer (recommended)
echo "Option 1: Official sunnypilot installer"
echo "curl -fsSL https://smiskol.com/fork/sunnypilot | bash"
echo ""

# Method 2: Manual installation
echo "Option 2: Manual installation"
echo "Run the following commands on your Comma device:"
echo ""
echo "# Backup current openpilot"
echo "cd /data"
echo "sudo mv openpilot openpilot_backup"
echo ""
echo "# Clone sunnypilot"
echo "git clone https://github.com/sunnypilot/sunnypilot.git openpilot"
echo "cd openpilot"
echo "git checkout master"
echo "git submodule update --init --recursive"
echo ""
echo "# Set permissions"
echo "sudo chown -R comma:comma /data/openpilot"
echo "chmod +x /data/openpilot/launch_openpilot.sh"
echo ""
echo "# Reboot"
echo "sudo reboot"
echo ""

# Method 3: Set params for sunnypilot (if using param-based approach)
read -p "Do you want to configure sunnypilot via params? (y/n): " configure_params

if [ "$configure_params" = "y" ] || [ "$configure_params" = "Y" ]; then
    echo "Configuring sunnypilot parameters..."
    
    python3 -c "
import os
import sys
sys.path.append('/data/openpilot')
from openpilot.common.params import Params

params = Params()

# Set sunnypilot git remote
params.put('GitRemote', 'https://github.com/sunnypilot/sunnypilot.git')
params.put('GitBranch', 'master')

# Enable custom fork
params.put('GitCommitRemote', 'https://github.com/sunnypilot/sunnypilot.git')

print('sunnypilot configuration applied successfully')
"

    echo "Configuration completed. The device will use sunnypilot on next update."
    echo "To force an immediate update, run:"
    echo "sudo systemctl restart manager"
else
    echo "Parameters not configured. Use manual installation method above."
fi
