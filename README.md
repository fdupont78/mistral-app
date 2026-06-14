# Mistral App - Chat Interface

A Python chat application with Mistral model support, Streamlit web interface, SQLite conversation persistence, CLI chat mode, and **RunPod deployment**.

## Quick Start

### CLI Mode
```bash
# Start interactive chat
python -m src.main chat

# With dry-run (no model loading, for debugging)
python -m src.main chat --dry-run

# List conversations
python -m src.main list

# Load a conversation
python -m src.main load <id>
```

### Web Interface
```bash
# Normal mode (loads Mistral model)
uv run streamlit run src/web/frontend.py

# Dry-run mode (mock responses, no GPU needed)
MISTRAL_DRY_RUN=1 uv run streamlit run src/web/frontend.py
```

---

## 🚀 Deploy to RunPod

Deploy your own instance of Mistral App on RunPod with **one command**.
Each user deploys to **their own RunPod account** using their own API key.

### Prerequisites
1. A [RunPod](https://runpod.io) account with credits
2. A **RunPod API Key** (get it from [RunPod Console > API](https://console.runpod.io/user/api))
3. Optional: A **Template ID** (default: `hsrb8il0fj` for RTX 4090)

### Method 1: Environment Variables (Recommended)
```bash
# Set your RunPod credentials
export RUNPOD_API_KEY="v1_your_api_key_here"
export RUNPOD_TEMPLATE_ID="hsrb8il0fj"  # Optional (default: hsrb8il0fj)

# Deploy
python -m src.main deploy --branch main
```

### Method 2: CLI Arguments
```bash
python -m src.main deploy \
  --branch main \
  --api-key "v1_your_api_key_here" \
  --template-id "hsrb8il0fj"
```

### Method 3: GitHub Actions (Automated Deployment)
1. **Fork this repository** (if you're not the owner)
2. Go to **Settings > Secrets > Actions** in your repo/fork
3. Add these **Repository Secrets**:
   - `RUNPOD_API_KEY`: Your RunPod API key
   - `RUNPOD_TEMPLATE_ID`: Your template ID (optional, defaults to `hsrb8il0fj`)
4. Run the workflow:
   - Go to **Actions > Deploy to RunPod > Run workflow**
   - Enter the branch to deploy (e.g., `main`)
   - Type `DEPLOY` to confirm
5. Your pod will start, and the Streamlit URL will be displayed in the logs

> **⚠️ Note**: For the main repository (`fdupont78/mistral-app`), deployment requires approval via GitHub Environment protection.

---

## Project Structure
```
src/
├── cli/
│   ├── __init__.py
│   ├── chat.py      # CLI chat commands
│   └── deploy.py    # RunPod deployment
├── core/
│   ├── __init__.py
│   ├── database.py  # SQLite conversation storage
│   ├── model.py     # Model loading
│   ├── conversation.py
│   └── runpod.py    # RunPod API client
└── web/
    └── frontend.py  # Streamlit web interface

github/
└── workflows/
    └── deploy-runpod.yml  # GitHub Actions workflow
```
