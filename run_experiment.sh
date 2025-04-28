#!/bin/bash

# Create and activate a virtual environment (recommended)
python3 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r /home/alaouar/Phd_work/orbac.owl/requirements.txt

# Run your Python script
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
python /home/alaouar/Phd_work/orbac.owl/web-demo/run_exps.py

# Deactivate the virtual environment (optional)
deactivate

# Clean cache (deletes models loaded in cache)
rm -rf ~/.cache/*
