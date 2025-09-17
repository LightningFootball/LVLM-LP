#!/bin/bash

# Quick Setup Script for LVLM-LP with LLaVA
# This script automates the environment setup process

set -e  # Exit on any error

echo "=== LVLM-LP Environment Setup Script ==="
echo "This script will set up the environment for running LLaVA with LVLM-LP"
echo ""

# Check if running as root (for apt-get)
if [[ $EUID -ne 0 ]]; then
   echo "This script needs to be run with sudo for system package installation"
   echo "Usage: sudo bash quick_setup.sh"
   exit 1
fi

# Step 1: Install system dependencies
echo "Step 1: Installing system dependencies..."
apt-get update
apt-get install -y libgl1-mesa-glx libglib2.0-0

# Step 2: Setup Miniconda (if not already installed)
echo "Step 2: Checking for Miniconda installation..."
if [ ! -d "$HOME/miniconda" ]; then
    echo "Miniconda not found. Please install Miniconda first:"
    echo "wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh"
    echo "bash miniconda.sh -b -p \$HOME/miniconda"
    echo 'echo "export PATH=\"\$HOME/miniconda/bin:\$PATH\"" >> ~/.bashrc'
    echo "source ~/.bashrc"
    exit 1
fi

# Step 3: Create conda environment
echo "Step 3: Creating conda environment from environment.yml..."
if [ -f "environment.yml" ]; then
    $HOME/miniconda/bin/conda env create -f environment.yml
else
    echo "environment.yml not found. Creating environment manually..."
    $HOME/miniconda/bin/conda create -n llava python=3.10 -y
    $HOME/miniconda/envs/llava/bin/pip install -r requirements.txt --root-user-action=ignore
fi

# Step 4: Download LLaVA model (if not already downloaded)
echo "Step 4: Checking for LLaVA model..."
if [ ! -d "$HOME/.cache/huggingface/hub/models--liuhaotian--llava-v1.5-7b" ]; then
    echo "Downloading LLaVA v1.5-7b model..."
    $HOME/miniconda/envs/llava/bin/huggingface-cli download liuhaotian/llava-v1.5-7b
else
    echo "LLaVA model already downloaded"
fi

# Step 5: Create output directories
echo "Step 5: Creating output directories..."
mkdir -p ./output/LLaVA-7B/tmp
mkdir -p ./output/tmp

# Step 6: Verify installation
echo "Step 6: Verifying installation..."
export PATH="$HOME/miniconda/envs/llava/bin:$PATH"

echo "Testing OpenCV import..."
$HOME/miniconda/envs/llava/bin/python -c "import cv2; print('✓ OpenCV works')"

echo "Testing run_model script..."
$HOME/miniconda/envs/llava/bin/python -m run_model --help > /dev/null 2>&1 && echo "✓ run_model script works"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To use the environment:"
echo "1. export PATH=\"\$HOME/miniconda/envs/llava/bin:\$PATH\""
echo "2. Or: conda activate llava"
echo ""
echo "To run experiments:"
echo "1. Configure dataset paths in dataset/__init__.py"
echo "2. Run: CUDA_VISIBLE_DEVICES=0 bash ./scripts/VizWiz/run_LLaVA_7B.sh"
echo ""
echo "Files created:"
echo "- requirements.txt: pip package list"
echo "- environment.yml: conda environment specification"
echo "- system_requirements.md: detailed setup documentation"
echo "- quick_setup.sh: this setup script"