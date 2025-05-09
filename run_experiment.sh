#!/bin/bash

# Set working directory to the directory containing this script
WORKDIR=$(dirname "$(realpath "$0")")
cd "$WORKDIR"

# Create and activate a virtual environment (recommended)
python3 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r "$WORKDIR/LLM_experiments/requirements.txt"

# Set environment variable to avoid CUDA memory issues (optional)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# List of models
models=(
  "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
  "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
  "meta-llama/Llama-3.2-3B"
  "meta-llama/Llama-3.2-3B-Instruct"
  "google/gemma-2-9b"
  "google/gemma-2-9b-it"
)

# Run parameters_tuning for each model
for model in "${models[@]}"; do
  echo "Running parameters_tuning for $model"
  python LLM_experiments/run_exps.py parameters_tuning "$model"
done

# Run interactive experiments for each model
for model in "${models[@]}"; do
  echo "Running interactive for $model"
  python LLM_experiments/run_exps.py interactive "$model"
done

# Run few_shot experiments for each model
for model in "${models[@]}"; do
  echo "Running few_shot for $model"
  python LLM_experiments/run_exps.py few_shot "$model"
done

# Deactivate the virtual environment (optional)
deactivate

# Clean cache (deletes models loaded in cache)
rm -rf ~/.cache/*
