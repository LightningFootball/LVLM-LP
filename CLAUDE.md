# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research codebase for "The First to Know: How Token Distributions Reveal Hidden Knowledge in Large Vision-Language Models?" - a study that uses linear probing to analyze hidden knowledge in Large Vision-Language Models (LVLMs). The project evaluates token distributions from the first generated tokens to solve tasks like identifying unanswerable questions, defending against jailbreak attacks, and mitigating hallucination.

## Architecture

### Core Components

- **`run_model.py`**: Main execution script that runs LVLM models on datasets and extracts logits from the first tokens
- **`model/`**: Contains wrapper classes for different LVLMs (LLaVA, MiniGPT-4, InstructBLIP, mPLUG-Owl, LLaMA-Adapter, MMGPT)
- **`dataset/`**: Dataset loaders for 6 evaluation tasks (VizWiz, MM-SafetyBench, MAD-Bench, MathVista, POPE, ImageNet)
- **`utils/`**: Utilities for prompting, metrics, annotation, and helper functions
- **`scripts/`**: Shell scripts organized by task for running models on different datasets
- **`assignment/`**: Contains assignment guidance PDF files
- **`custom/`**: Custom scripts and utilities
- **`environment_setup/`**: Environment setup packages and configurations for reproducible deployments
- **Jupyter notebooks**: `Task{1-6}_*.ipynb` files for evaluating linear probing performance

### Data Flow

1. **Model Execution**: Use scripts in `scripts/` to run models on datasets via `run_model.py`
2. **Logit Extraction**: Models generate responses and extract first-token logits/probabilities
3. **Linear Probing**: Jupyter notebooks train linear classifiers on extracted logits
4. **Evaluation**: Performance metrics calculated for each task

## Common Commands

### Running Model Evaluation

```bash
# Run LLaVA-7B on VizWiz dataset (modify GPU count as needed)
CUDA_VISIBLE_DEVICES=0,1,2,3 bash ./scripts/VizWiz/run_LLaVA_7B.sh

# Run on other tasks - replace VizWiz with: Safety, MAD, MathV, POPE, ImageNet
CUDA_VISIBLE_DEVICES=0,1,2,3 bash ./scripts/Safety/run_LLaVA_7B.sh
```

### Direct Model Execution

```bash
# Run model manually with specific parameters
python -m run_model \
    --model_name LLaVA-7B \
    --model_path liuhaotian/llava-v1.5-7b \
    --split val \
    --dataset VizWiz \
    --prompt oe \
    --answers_file ./output/LLaVA-7B/results.jsonl \
    --temperature 0.0 \
    --top_p 0.9 \
    --num_beams 1
```

### Using Finetuned Models

```bash
# Run all tasks with finetuned model (modify model_path in script first)
bash ./scripts/finetune_all.sh

# Run all tasks with retrained model (modify model_path in script first)
bash ./scripts/retrain_all.sh
```

## Dataset Configuration

Before running experiments, modify dataset paths in `dataset/__init__.py`:

```python
dataset_roots = {
    "VizWiz": "/path/to/VizWiz/",
    "MMSafety": "/path/to/MM-SafetyBench/",
    "MAD": "/path/to/coco/",
    "MathVista": "/path/to/MathVista/",
    "POPE": "/path/to/coco/",
    "ImageNet": "/path/to/ImageNet/"
}
```

## Environment Setup

### Quick Setup (Recommended)
Use the automated setup package in `environment_setup/llava/`:

```bash
# Navigate to setup directory
cd environment_setup/llava/

# Run automated setup
sudo bash quick_setup.sh
```

### Manual Setup Options
```bash
# Option 1: Conda environment
conda env create -f environment_setup/llava/environment.yml
conda activate llava

# Option 2: Pip installation
conda create -n llava python=3.10 -y
conda activate llava
pip install -r environment_setup/llava/requirements.txt
```

See `environment_setup/llava/README_SETUP.md` for detailed instructions and troubleshooting.

## Model Setup

Each model in `model/` directory requires:
1. Cloning the original model repository
2. Downloading required checkpoints
3. Setting the correct model folder path in the respective model file

Supported models: LLaVA, MiniGPT-4, InstructBLIP, mPLUG-Owl, LLaMA-Adapter, MMGPT

## Key Tasks

1. **Task 1 (VizWiz)**: Identify unanswerable visual questions
2. **Task 2 (Safety)**: Defense against jailbreak attacks
3. **Task 3 (MAD)**: Identify deceptive questions
4. **Task 4 (MathV)**: Uncertainty in math solving
5. **Task 5 (POPE)**: Mitigate hallucination
6. **Task 6 (ImageNet)**: Image classification

## Output Structure

- Model outputs saved to `./output/{MODEL_NAME}/` directory
- Results stored as JSONL files with format: `{DATASET}_{SPLIT}_{PROMPT}.jsonl`
- Each line contains: image path, question, label, response, logits, probabilities

## Evaluation

After running models, use corresponding `Task{N}_*.ipynb` notebooks to:
1. Load extracted logits and labels
2. Train linear probing classifiers
3. Evaluate performance metrics
4. Compare against finetuning baselines

## Git Commit Guidelines

- Do NOT include AI-generated attribution lines in commit messages
- Keep commit messages clean and professional without mentioning Claude Code or Co-Authored-By lines