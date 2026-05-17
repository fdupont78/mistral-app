# Mistral App - Chat Interface

A Python chat application with Mistral 3B model support, Streamlit web interface, SQLite conversation persistence, and CLI chat mode.

## Features

- **Interactive CLI Chat** - Chat with Mistral 3B model in your terminal
- **Streamlit Web Interface** - Modern web-based chat UI
- **Conversation Persistence** - All chats saved to SQLite database
- **Dry-run Mode** - Debug locally without loading the model
- **Multi-model Ready** - Architecture designed for model extensibility

## Quick Start

### CLI Mode
```bash
# Start interactive chat
python main.py chat

# With dry-run (no model loading, for debugging)
python main.py chat --dry-run

# List conversations
python main.py list

# Load a conversation
python main.py load <id>
```

### Web Interface
```bash
# Normal mode (loads Mistral model)
uv run streamlit run frontend.py

# Dry-run mode (mock responses, no GPU needed)
MISTRAL_DRY_RUN=1 uv run streamlit run frontend.py
```

## Project Layout

```
.
├── main.py           # CLI entry point and command routing
├── chat.py           # Interactive chat logic
├── conversation.py   # Conversation state management
├── model.py          # Model loading and response generation
├── database.py       # SQLite conversation persistence
├── frontend.py       # Streamlit web interface
├── request.py        # Example model request
├── setup.sh          # Deployment setup script
└── .skill/           # Vibe skills for automation
    └── create-pr/    # PR creation skill
```

## Roadmap

### Step 1: Easy Deploy on RunPod ✅
Deploy a chat interface with open-weights model Ministral-3-3B-Instruct-2512 on RunPod.

**Status:** Implemented
- Model loading via `transformers` and `torch`
- Quantization with BitsAndBytes (8-bit)
- CUDA device support
- Streamlit web interface for easy access
- Setup script for automated deployment

**RunPod Deployment:**
```bash
# Install dependencies
./setup.sh

# Run the app (exposed on port 8501)
uv run streamlit run frontend.py --server.address 0.0.0.0 --server.port 8501
```

### Step 2: Prometheus Metrics per User
Add Prometheus metrics to monitor model consumption and usage per user.

**Planned Features:**
- Track tokens generated per user
- Monitor request latency
- Count active conversations
- Measure model inference time
- Export metrics in Prometheus format

**Implementation:**
```python
# Example metric integration
from prometheus_client import Counter, Histogram

TOKENS_GENERATED = Counter('mistral_tokens_generated_total', 'Total tokens generated', ['user_id', 'model'])
INFERENCE_TIME = Histogram('mistral_inference_seconds', 'Inference time', ['model'])
```

### Step 3: Multi-Model Support from Hugging Face
Enable switching between multiple Hugging Face models.

**Planned Features:**
- Dynamic model loading from Hugging Face Hub
- Model caching and management
- Configuration per model (quantization, device)
- Seamless switching between models
- Model health checks

**Architecture:**
```python
class ModelRegistry:
    def __init__(self):
        self.models = {}
        
    def load_model(self, model_name: str, config: ModelConfig):
        """Load and cache a model with specific configuration"""
        
    def get_model(self, model_name: str) -> Model:
        """Retrieve a loaded model"""
        
    def list_models(self) -> List[str]:
        """List available models"""
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MISTRAL_DRY_RUN` | Enable dry-run mode (mock responses) | `false` |
| `MODEL_NAME` | Hugging Face model path | `/workspace/Ministral-3-3B-Instruct-2512` |

## Development

### Prerequisites
- Python 3.11+
- UV package manager
- CUDA-enabled GPU (for model inference)
- Git LFS (for model weights)

### Setup
```bash
# Clone the repository
git clone https://github.com/fdupont78/mistral-app.git
cd mistral-app

# Install dependencies
uv sync

# Setup model (requires Git LFS)
git lfs install
git clone https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512 /workspace/Ministral-3-3B-Instruct-2512
```

### Testing
```bash
# Test CLI in dry-run mode
python main.py chat --dry-run

# Test web interface in dry-run mode
MISTRAL_DRY_RUN=1 uv run streamlit run frontend.py
```

## Skills

This project uses Vibe skills for automation:

- **create-pr**: Create GitHub Pull Requests with a single commit

## License

MIT License
