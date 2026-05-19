#!/bin/bash

# RunPod Setup Script for Mistral App
# This script sets up the environment and launches the Streamlit application

set -e

echo "=== RunPod Setup for Mistral App ==="

# 1. Install uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Clone the repository
REPO_DIR="/workspace/mistral-app"
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning mistral-app repository..."
    git clone https://github.com/fdupont78/mistral-app.git "$REPO_DIR"
fi

cd "$REPO_DIR"

# 3. Install dependencies
echo "Installing Python dependencies..."
uv sync

# 4. Setup Mistral model (optional - comment out if model is already present)
MODEL_DIR="/workspace/Ministral-3-3B-Instruct-2512"
if [ ! -d "$MODEL_DIR" ]; then
    echo "Installing Git LFS..."
    apt-get update && apt-get install -y git git-lfs
    git lfs install
    echo "Downloading Mistral model (this may take a while)..."
    git clone https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512 "$MODEL_DIR"
fi

# 5. Launch Streamlit application
echo ""
echo "=== Starting Streamlit Application ==="
echo "Access the app at: https://$(echo $RUNPOD_ID)-8501.proxy.runpod.net"
echo ""

# Run Streamlit with proper configuration
# Use --server.headless=true and --server.enableXsrfProtection=false for RunPod
uv run streamlit run src/web/frontend.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    --server.headless true \
    --server.enableXsrfProtection false \
    --server.enableCORS false
