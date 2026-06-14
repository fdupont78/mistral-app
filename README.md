# Mistral App - Chat Interface

A Python chat application with Mistral model support, **dual frontend** (Streamlit + React/TypeScript), SQLite conversation persistence, and CLI chat mode.

## 🚀 Quick Start

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

### Web Interface - Streamlit (Original)
```bash
# Normal mode (loads Mistral model)
uv run streamlit run src/web/streamlit/frontend.py

# Dry-run mode (mock responses, no GPU needed)
MISTRAL_DRY_RUN=1 uv run streamlit run src/web/streamlit/frontend.py
```

### Web Interface - React/TypeScript (New)

First, install dependencies:
```bash
# Install Python dependencies (FastAPI)
uv sync

# Install Node.js dependencies (React)
cd src/web/react && npm install
```

Then run the services:
```bash
# Option 1: Run all services (API + React + Streamlit)
npm run dev

# Option 2: Run services separately
# Terminal 1: Start FastAPI server
npm run dev:api

# Terminal 2: Start React dev server
npm run dev:react

# Terminal 3: Start Streamlit server (optional)
npm run dev:streamlit
```

Access the applications:
- **React Frontend**: http://localhost:5173
- **FastAPI Docs**: http://localhost:8000/api/docs
- **Streamlit Frontend**: http://localhost:8501

## 📁 Project Structure

```
mistral-app/
├── src/
│   ├── core/                  # Shared backend (Python)
│   │   ├── model.py          # Model loading & generation
│   │   ├── conversation.py    # Conversation management
│   │   ├── database.py        # SQLite persistence
│   │   └── validation.py      # Input validation
│   ├── web/
│   │   ├── streamlit/         # Original Streamlit frontend
│   │   │   └── frontend.py
│   │   ├── react/             # New React/TypeScript frontend
│   │   │   ├── src/
│   │   │   │   ├── components/  # React components
│   │   │   │   ├── hooks/       # Custom hooks
│   │   │   │   ├── types/       # TypeScript types
│   │   │   │   ├── api/         # API client
│   │   │   │   └── styles/      # CSS styles
│   │   │   ├── package.json
│   │   │   └── vite.config.ts
│   │   └── api/               # FastAPI backend
│   │       └── server.py
│   └── cli/                   # CLI interface
│       └── chat.py
├── docs/
│   └── FRONTEND_COMPARISON.md  # Detailed comparison
├── package.json              # Root package.json (workspaces)
└── pyproject.toml            # Python dependencies
```

## 🎯 Frontend Comparison

This project now supports **two frontend implementations** that share the same backend:

| Feature | Streamlit | React/TypeScript |
|---------|-----------|-----------------|
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **UI Customization** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Type Safety** | ❌ | ✅ |
| **Streaming** | ⚠️ Limited | ✅ WebSocket |
| **Deployment** | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Recommendation**: Use **Streamlit** for rapid prototyping and **React** for production applications.

See [docs/FRONTEND_COMPARISON.md](docs/FRONTEND_COMPARISON.md) for a detailed comparison.

## 🔧 Configuration

### Environment Variables

#### For React Development
Create a `.env` file in `src/web/react/`:
```env
VITE_API_URL=http://localhost:8000
VITE_API_PORT=8000
VITE_DRY_RUN=true  # Enable mock responses
```

#### For Streamlit
```bash
# Enable dry-run mode (no model loading)
export MISTRAL_DRY_RUN=1
```

## 📊 API Endpoints

The FastAPI server provides these endpoints:

- `GET /api/health` - Health check
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/{id}/messages` - Get messages
- `POST /api/conversations/{id}/generate` - Generate response
- `GET /api/model/status` - Model status
- `POST /api/model/load` - Load model
- `POST /api/model/unload` - Unload model
- `ws://localhost:8000/ws/chat/{id}` - WebSocket streaming

Full API documentation available at `http://localhost:8000/api/docs` when running.

## 🎨 Features

- **Dual Frontend**: Choose between Streamlit (fast development) or React (production quality)
- **Shared Backend**: Both frontends use the same Python backend via FastAPI
- **Conversation History**: SQLite database for persistent conversations
- **Model Management**: Load/unload Mistral models with different quantization methods
- **Generation Parameters**: Fine-tune model responses with 7 parameters
- **Dry-run Mode**: Test without loading models (mock responses)
- **WebSocket Streaming**: Real-time response streaming in React

## 📦 Dependencies

### Python
- Python 3.11+
- Streamlit
- FastAPI (for React frontend)
- Uvicorn (for FastAPI server)
- Pydantic (for API validation)
- SQLite3 (built-in)

### Node.js (for React)
- Node.js 18+
- React 18+
- TypeScript
- Vite (bundler)
- Tailwind CSS (styling)
- Zustand (state management)

## 🚀 Deployment

### Option 1: Local Development
```bash
# Install all dependencies
uv sync
cd src/web/react && npm install

# Run all services
npm run dev
```

### Option 2: Production Deployment
- **FastAPI**: Deploy to Render, Railway, or Fly.io
- **React**: Deploy to Vercel, Netlify, or GitHub Pages
- **Streamlit**: Deploy to Streamlit Cloud or Hugging Face Spaces

See [docs/FRONTEND_COMPARISON.md](docs/FRONTEND_COMPARISON.md) for deployment details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📄 License

MIT License
