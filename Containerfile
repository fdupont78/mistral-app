# Containerfile for Mistral App Streamlit deployment
# Build with: podman build -t ghcr.io/fdupont78/mistral-app:latest .
# Or with Docker: docker build -t ghcr.io/fdupont78/mistral-app:latest .

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="$HOME/.local/bin:$PATH"

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies (without torch for base image - will be added in runtime)
RUN uv sync --extra streamlit

# Copy source code
COPY src/ ./src/
COPY README.md ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit in dry-run mode by default (no model loading)
# Set MISTRAL_DRY_RUN=0 to enable actual model loading (requires GPU)
CMD ["streamlit", "run", "src/web/frontend.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.enableXsrfProtection=false", \
     "--server.enableCORS=false"]
