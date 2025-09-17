# System Requirements and Setup Instructions

## Overview
This document contains the system dependencies and setup instructions for the LVLM-LP project with LLaVA v1.5-7b.

## System Dependencies

### Required System Packages
```bash
# Update system packages
apt-get update

# Install OpenGL and graphics libraries for OpenCV
apt-get install -y libgl1-mesa-glx libglib2.0-0

# Additional libraries that were installed:
# libdrm-* libglapi-mesa libllvm12 libsensors* libvulkan1
# libgl1-mesa-dri libglvnd0 libx11-xcb1 libxcb-* libxshmfence1
# libxxf86vm1 mesa-vulkan-drivers
```

### CUDA Requirements
- CUDA 11.7 (detected system version)
- Note: There's a version mismatch with PyTorch's CUDA 12.1, but it works for basic operations
- flash-attn installation failed due to CUDA version mismatch (non-critical for basic usage)

## Python Environment Setup

### Option 1: Using Conda (Recommended)
```bash
# Create environment from exported file
conda env create -f environment.yml

# Activate environment
conda activate llava
```

### Option 2: Using pip with conda base
```bash
# Create conda environment with Python 3.10
conda create -n llava python=3.10 -y
conda activate llava

# Install packages from requirements file
pip install -r requirements.txt --root-user-action=ignore

# Install system packages
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
```

## Critical Package Versions

### Core Dependencies
- **Python**: 3.10.18
- **PyTorch**: 2.1.2+cu121
- **numpy**: 1.26.4 (downgraded from 2.2.6 for compatibility)
- **transformers**: 4.37.2
- **opencv-python**: 4.12.0.88

### Model-specific Dependencies
- **accelerate**: 0.21.0
- **deepspeed**: 0.12.6
- **bitsandbytes**: 0.45.5
- **peft**: 0.17.1
- **sentencepiece**: 0.1.99
- **tokenizers**: 0.15.1

### Vision and UI Dependencies
- **gradio**: 4.16.0
- **pillow**: 10.4.0
- **timm**: 0.6.13
- **einops**: 0.6.1

## Model Setup

### LLaVA Model Download
```bash
# The model is automatically downloaded from Hugging Face Hub
# Location: ~/.cache/huggingface/hub/models--liuhaotian--llava-v1.5-7b/
# Model path used in scripts: liuhaotian/llava-v1.5-7b
```

## Known Issues and Solutions

### 1. NumPy Compatibility
**Issue**: NumPy 2.x causes compatibility issues with some packages
**Solution**: Downgrade to numpy<2
```bash
pip install "numpy<2" --root-user-action=ignore
```

### 2. OpenCV Import Error
**Issue**: `ImportError: libGL.so.1: cannot open shared object file`
**Solution**: Install system GL libraries
```bash
apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### 3. flash-attn Installation Failure
**Issue**: CUDA version mismatch (11.7 vs 12.1)
**Status**: Non-critical, basic functionality works without flash-attn

### 4. Deprecation Warnings
- pynvml package deprecated (use nvidia-ml-py instead)
- Various NumPy and transformers deprecation warnings
- These are warnings only and don't affect functionality

## Dataset Configuration

### Required Setup
The project expects datasets in specific locations defined in `dataset/__init__.py`:

```python
dataset_roots = {
    "VizWiz": "/data/VizWiz/",
    "MMSafety": "/data/qinyu/data/MM-SafetyBench/",
    "MAD": "/data/coco/",
    "MathVista": "/data/MathVista/",
    "POPE": "/data/coco/",
    "ImageNet": "/data/ImageNet/"
}
```

**Note**: Update these paths to match your actual dataset locations.

## Verification Steps

### Test Environment Setup
```bash
# Activate environment
conda activate llava

# Test OpenCV
python -c "import cv2; print('OpenCV works')"

# Test model loading capability
export PATH="$HOME/miniconda/envs/llava/bin:$PATH"
cd /path/to/LVLM-LP
python -m run_model --help
```

### Expected Output
- OpenCV should import successfully
- run_model should show help text without errors
- Model loading should work (though will fail on missing datasets)

## Hardware Requirements

### Minimum Requirements
- GPU with CUDA support (tested with CUDA 11.7)
- 8GB+ GPU memory for LLaVA-7B model
- 16GB+ system RAM recommended

### Tested Configuration
- CUDA 11.7
- Python 3.10.18
- Ubuntu 20.04 (inferred from package versions)

## Installation Time Estimates
- System packages: 2-3 minutes
- Conda environment: 5-10 minutes
- Model download: 5-15 minutes (depending on internet speed)
- Total setup time: 15-30 minutes

## Troubleshooting

If you encounter issues:
1. Check CUDA compatibility
2. Verify system package installation
3. Ensure correct Python environment activation
4. Check dataset paths in `dataset/__init__.py`
5. Verify model download completed successfully

## Files Generated
- `requirements.txt`: pip package list
- `environment.yml`: conda environment specification
- `system_requirements.md`: this documentation file