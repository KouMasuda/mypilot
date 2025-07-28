#!/usr/bin/bash

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

# API Keys Configuration
# Set your API keys here for centralized management
# Run 'python3 setup_api_keys.py' to configure these automatically
# 
# MapTiler API Key (get from https://maptiler.com)
export MAPTILER_TOKEN=""
# Mapbox Secret Token (sk.xxx format, get from https://mapbox.com)
export MAPBOX_TOKEN=""

if [ -z "$AGNOS_VERSION" ]; then
  export AGNOS_VERSION="10.1"
fi

export STAGING_ROOT="/data/safe_staging"
