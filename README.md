# Mistral App - Chat Interface

A Python chat application with Mistral model support, Streamlit web interface, SQLite conversation persistence, and CLI chat mode.

## Features

- **Interactive CLI Chat** - Chat with Mistral model in your terminal
- **Streamlit Web Interface** - Modern web-based chat UI
- **Conversation Persistence** - All chats saved to SQLite database
- **Dry-run Mode** - Debug locally without loading the model
- **Multi-model Ready** - Architecture designed for model extensibility
- **Well-Tested** - Comprehensive unit, integration, and E2E tests

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

## Project Layout

```
.
├── src/
│   ├── __init__.py          # Package exports
│   ├── main.py              # CLI entry point and command routing
│   │
│   ├── core/
│   │   ├── __init__.py      # Core module exports
│   │   ├── database.py      # DatabaseManager class for SQLite operations
│   │   ├── model.py          # ModelManager class for model loading and inference
│   │   └── conversation.py   # Conversation and Message classes
│   │
│   ├── cli/
│   │   └── chat.py           # Interactive CLI chat logic
│   │
│   └── web/
│       └── frontend.py       # Streamlit web interface
│
└── tests/
    ├── __init__.py          # Test package
    ├── conftest.py           # Pytest fixtures and configuration
    │
    ├── unit/
    │   ├── __init__.py
    │   ├── test_database.py   # Unit tests for DatabaseManager
    │   ├── test_conversation.py  # Unit tests for Conversation/Message
    │   └── test_model.py      # Unit tests for ModelManager
    │
    ├── integration/
    │   ├── __init__.py
    │   └── test_integration.py  # Integration tests
    │
    └── e2e/
        ├── __init__.py
        └── test_cli_e2e.py   # End-to-end tests for CLI
```

## Architecture

### Core Components

#### DatabaseManager (`src/core/database.py`)
- Manages SQLite database connections
- Provides CRUD operations for conversations and messages
- Uses context managers for safe database access
- Supports transaction rollback on errors

#### ModelManager (`src/core/model.py`)
- Handles model loading with different quantization methods
- Provides response generation with configurable parameters
- Supports dry-run mode for testing without GPU
- Lazy loading of tokenizer and model

#### Conversation (`src/core/conversation.py`)
- Represents chat conversations with message history
- Manages database persistence
- Provides methods for message management and formatting

### Generation Parameters

The application supports the following generation parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_new_tokens | int | 512 | Maximum new tokens to generate |
| temperature | float | 0.7 | Randomness (0.0=deterministic, 1.0+=creative) |
| do_sample | bool | True | Enable sampling vs greedy decoding |
| top_k | int | 50 | Keep top-k tokens for sampling |
| top_p | float | 0.92 | Nucleus sampling threshold |
| repetition_penalty | float | 1.0 | Penalty for repeated tokens |
| num_return_sequences | int | 1 | Number of response sequences |

### Quantization Options

| Method | Description | VRAM Usage |
|--------|-------------|------------|
| none | No quantization (full precision) | ~15GB |
| 8bit | 8-bit quantization | ~6-8GB |
| 4bit | 4-bit quantization | ~3-4GB |
| fp8 | FP8 quantization (NVIDIA GPUs) | ~4GB |

## Testing

The project has comprehensive test coverage with three test categories:

### Unit Tests
Test individual classes and functions in isolation.
```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_database.py
```

### Integration Tests
Test interactions between multiple components.
```bash
# Run all integration tests
pytest tests/integration/
```

### End-to-End Tests
Test complete workflows from user input to database storage.
```bash
# Run all E2E tests
pytest tests/e2e/
```

### Running All Tests
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term

# Run specific test category
pytest -m unit
pytest -m integration
pytest -m e2e
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
- CUDA-enabled GPU (for model inference, optional for dry-run)
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

### Testing (No GPU Required)
```bash
# Test with dry-run mode (no model loading)
python -m src.main chat --dry-run

# Run unit tests
pytest tests/unit/ -v

# Run all tests
pytest -v
```

## Key Design Decisions

### 1. Class-Based Architecture
- **DatabaseManager**: Encapsulates all database operations with proper connection management
- **ModelManager**: Manages model lifecycle and provides clean interface for inference
- **Conversation**: Represents chat state with message history

### 2. Separation of Concerns
- **Core module**: Contains business logic (database, model, conversation)
- **CLI module**: Handles command-line interface
- **Web module**: Manages Streamlit frontend

### 3. Dependency Injection
- Components accept DatabaseManager instances for testability
- Allows easy mocking in tests
- Supports different database configurations

### 4. Backward Compatibility
- Old module-level functions are preserved as wrappers
- Existing code using `from database import init_db` still works
- Gradual migration path to new class-based API

### 5. Testability
- All classes are designed to be easily tested
- Fixtures provide clean test environments
- Mocking is minimal and focused

## Roadmap

### Step 1: Easy Deploy on RunPod ✅
- Model loading via `transformers` and `torch`
- Quantization with BitsAndBytes
- CUDA device support
- Streamlit web interface
- Setup script for automated deployment

### Step 2: Prometheus Metrics per User
- Track tokens generated per user
- Monitor request latency
- Count active conversations
- Measure model inference time
- Export metrics in Prometheus format

### Step 3: Multi-Model Support from Hugging Face
- Dynamic model loading from Hugging Face Hub
- Model caching and management
- Configuration per model (quantization, device)
- Seamless switching between models
- Model health checks

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include docstrings for public methods
- Write tests for all new functionality

### Testing
- Add unit tests for new classes
- Add integration tests for component interactions
- Add E2E tests for user workflows
- Ensure test coverage > 80%

### Pull Requests
- Include clear description of changes
- Reference any related issues
- Include test results
- Update documentation as needed

## License

MIT License
