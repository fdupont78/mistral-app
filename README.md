# Mistral App - Chat Interface

A Python chat application with Mistral model support, Streamlit web interface, SQLite conversation persistence, and CLI chat mode.

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
