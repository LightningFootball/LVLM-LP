# LVLM-LP Environment Setup Package

## Package Contents

This folder contains all necessary files to reproduce the working LVLM-LP environment with LLaVA v1.5-7b.

### Files Included:
- `requirements.txt` - Python package requirements
- `environment.yml` - Complete conda environment specification
- `system_requirements.md` - Detailed setup documentation
- `quick_setup.sh` - Automated installation script

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
sudo bash quick_setup.sh
```

### Option 2: Manual Setup
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

# Create conda environment
conda env create -f environment.yml
conda activate llava

# Download LLaVA model
huggingface-cli download liuhaotian/llava-v1.5-7b
```

### Option 3: Pip Installation
```bash
conda create -n llava python=3.10 -y
conda activate llava
pip install -r requirements.txt --root-user-action=ignore
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

## Verification

Test the installation:
```bash
# Activate environment
conda activate llava

# Test imports
python -c "import cv2; print('OpenCV works')"
python -c "import torch; print('PyTorch works')"

# Test model script
python -m run_model --help
```

## Key Versions
- Python: 3.10.18
- PyTorch: 2.1.2+cu121
- NumPy: 1.26.4 (compatibility version)
- Transformers: 4.37.2
- OpenCV: 4.12.0.88

## Documentation

See `system_requirements.md` for:
- Detailed setup instructions
- Troubleshooting guide
- Known issues and solutions
- Hardware requirements

## Archive Info
- **Created**: September 17, 2025
- **Size**: 5.2KB
- **Environment**: Ubuntu 20.04, CUDA 11.7
- **Model**: LLaVA v1.5-7b ready