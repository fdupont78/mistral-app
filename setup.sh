#!/bin/bash

# 1. Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Setup github
export KEY_PATH="$HOME/.ssh/id_ed25519_github"
export EMAIL=flo78.dupont@gmail.com
ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEY_PATH" -N ""
echo "=== COPY THIS PUBLIC KEY TO YOUR LOCAL MACHINE ==="
cat "$KEY_PATH.pub"
echo "==================================================="
echo -n "Paste the above public key to your local machine and press [Enter] to continue..."
read -r
eval "$(ssh-agent -s)"
ssh-add $KEY_PATH

# Setup Mistral model
apt update && apt install -y git git-lfs
git lfs install
git clone https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512 /workspace/Ministral-3-3B-Instruct-2512

# 2. Créer le projet et installer les dépendances
cd /workspace
git clone git@github.com:fdupont78/mistral-app.git

cd mistral_app
uv sync
uv run python main.py



