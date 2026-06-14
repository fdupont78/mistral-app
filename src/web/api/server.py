"""
FastAPI server for Mistral Chat Application.
Provides REST API and WebSocket endpoints for React frontend.

Run with: uv run uvicorn src.web.api.server:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, Field

from src.core.model import get_model_manager, ModelManager, QUANTIZATION_METHODS
from src.core.database import get_database_manager, DatabaseManager

# Global instances
_model_manager: ModelManager | None = None
_db_manager: DatabaseManager | None = None


# ============================================================================
# Pydantic Models
# ============================================================================

class MessageBase(BaseModel):
    """Base message model."""
    role: str = Field(..., description="Role of the message (user/assistant)")
    content: str = Field(..., description="Content of the message")


class MessageCreate(MessageBase):
    """Message creation model."""
    pass


class MessageResponse(MessageBase):
    """Message response model."""
    id: int
    conversation_id: int
    timestamp: str


class ConversationBase(BaseModel):
    """Base conversation model."""
    title: str = Field(default="New Chat", description="Title of the conversation")


class ConversationResponse(ConversationBase):
    """Conversation response model."""
    id: int
    created_at: str
    updated_at: str


class ConversationUpdate(BaseModel):
    """Conversation update model."""
    title: str = Field(..., description="New title for the conversation")


class GenerationParams(BaseModel):
    """Generation parameters model."""
    max_new_tokens: int = Field(default=512, ge=16, le=2048, description="Maximum new tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    do_sample: bool = Field(default=True, description="Enable sampling")
    top_k: int = Field(default=50, ge=1, le=200, description="Number of top tokens for sampling")
    top_p: float = Field(default=0.92, ge=0.0, le=1.0, description="Nucleus sampling probability")
    repetition_penalty: float = Field(default=1.0, ge=0.5, le=2.0, description="Repetition penalty")
    num_return_sequences: int = Field(default=1, ge=1, le=5, description="Number of sequences to generate")


class GenerateRequest(BaseModel):
    """Request model for generation."""
    params: GenerationParams = Field(default_factory=GenerationParams)
    dry_run: bool = Field(default=False, description="Use dry-run mode (mock responses)")


class ModelStatusResponse(BaseModel):
    """Model status response model."""
    loaded: bool
    loading: bool
    status: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


# ============================================================================
# Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global _model_manager, _db_manager
    
    # Initialize database
    _db_manager = get_database_manager()
    _db_manager.init_db()
    
    # Initialize model manager
    _model_manager = get_model_manager()
    
    yield
    
    # Cleanup on shutdown
    if _model_manager:
        _model_manager.unload_model()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Mistral Chat API",
    description="REST API for Mistral Chat Application",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware - Allow React dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": _db_manager is not None,
        "model_manager": _model_manager is not None,
    }


# ============================================================================
# Conversations Endpoints
# ============================================================================

@app.get("/api/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of conversations to return")
):
    """List all conversations, ordered by updated_at descending."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    conversations = _db_manager.list_conversations(limit=limit)
    return [
        {
            "id": conv[0],
            "title": conv[1],
            "created_at": conv[2],
            "updated_at": conv[3],
        }
        for conv in conversations
    ]


@app.post("/api/conversations", response_model=dict, status_code=201)
async def create_conversation(conversation: ConversationBase):
    """Create a new conversation."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    conv_id = _db_manager.create_conversation(conversation.title)
    return {"id": conv_id}


@app.get("/api/conversations/{conv_id}", response_model=ConversationResponse)
async def get_conversation(conv_id: int):
    """Get a specific conversation by ID."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")
    
    return {
        "id": conv_data[0],
        "title": conv_data[1],
        "created_at": conv_data[2],
        "updated_at": conv_data[3],
    }


@app.put("/api/conversations/{conv_id}", response_model=ConversationResponse)
async def update_conversation(conv_id: int, conversation: ConversationUpdate):
    """Update a conversation title."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Check if conversation exists
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")
    
    _db_manager.update_conversation_title(conv_id, conversation.title)
    
    # Return updated conversation
    updated_conv = _db_manager.get_conversation(conv_id)
    return {
        "id": updated_conv[0],
        "title": updated_conv[1],
        "created_at": updated_conv[2],
        "updated_at": updated_conv[3],
    }


@app.delete("/api/conversations/{conv_id}", response_model=dict)
async def delete_conversation(conv_id: int):
    """Delete a conversation and all its messages."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Check if conversation exists
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")
    
    _db_manager.delete_conversation(conv_id)
    return {"success": True, "message": f"Conversation {conv_id} deleted"}


# ============================================================================
# Messages Endpoints
# ============================================================================

@app.get("/api/conversations/{conv_id}/messages", response_model=List[MessageResponse])
async def get_messages(conv_id: int):
    """Get all messages for a conversation, ordered by timestamp ascending."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Check if conversation exists
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")
    
    messages = _db_manager.get_messages(conv_id)
    return [
        {
            "id": msg[0],
            "conversation_id": msg[1],
            "role": msg[2],
            "content": msg[3],
            "timestamp": msg[4],
        }
        for msg in messages
    ]


@app.post("/api/conversations/{conv_id}/messages", response_model=dict, status_code=201)
async def add_message(conv_id: int, message: MessageCreate):
    """Add a message to a conversation."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Check if conversation exists
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")
    
    msg_id = _db_manager.add_message(conv_id, message.role, message.content)
    return {"id": msg_id}


@app.delete("/api/messages/{msg_id}", response_model=dict)
async def delete_message(msg_id: int):
    """Delete a specific message."""
    if not _db_manager:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Note: Current database schema doesn't support individual message deletion
    # This would require adding a delete_message method to DatabaseManager
    raise HTTPException(
        status_code=501,
        detail="Message deletion not implemented. Delete conversation instead."
    )


# ============================================================================
# Model Endpoints
# ============================================================================

@app.get("/api/model/status", response_model=ModelStatusResponse)
async def get_model_status():
    """Get model loading status."""
    if not _model_manager:
        return ModelStatusResponse(loaded=False, loading=False, status="Not initialized")
    
    return ModelStatusResponse(
        loaded=_model_manager.is_loaded(),
        loading=_model_manager.is_loading(),
        status=_model_manager.get_status(),
    )


@app.post("/api/model/load", response_model=dict)
async def load_model(
    quant_method: str = Query(
        default="fp8",
        description="Quantization method: none, 8bit, 4bit, fp8"
    )
):
    """Load the model with specified quantization method."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")
    
    if _model_manager.is_loaded():
        raise HTTPException(status_code=400, detail="Model already loaded")
    
    if _model_manager.is_loading():
        raise HTTPException(status_code=400, detail="Model is already loading")
    
    # Validate quantization method
    if quant_method not in QUANTIZATION_METHODS:
        valid_methods = list(QUANTIZATION_METHODS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid quantization method. Valid options: {valid_methods}"
        )
    
    # Load model in background (non-blocking)
    # Note: This is a simple implementation. For production, consider using background tasks
    _model_manager.load_model(quant_method=quant_method)
    
    return {
        "status": "Loading started",
        "quant_method": quant_method,
    }


@app.post("/api/model/unload", response_model=dict)
async def unload_model():
    """Unload the model to free memory."""
    if not _model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")
    
    if not _model_manager.is_loaded():
        raise HTTPException(status_code=400, detail="Model is not loaded")
    
    _model_manager.unload_model()
    
    return {
        "status": "Model unloaded",
    }


# ============================================================================
# Generation Endpoint
# ============================================================================

@app.post("/api/conversations/{conv_id}/generate", response_model=dict)
async def generate_response(
    conv_id: int,
    request: GenerateRequest,
):
    """
    Generate a response for a conversation.
    
    This endpoint:
    1. Gets the conversation history
    2. Generates a response using the model
    3. Saves the assistant response to the database
    4. Returns the generated response
    """
    if not _db_manager or not _model_manager:
        raise HTTPException(status_code=500, detail="Backend not initialized")
    
    # Check if conversation exists
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")
    
    # Check model status
    if not request.dry_run and not _model_manager.is_loaded():
        raise HTTPException(status_code=400, detail="Model not loaded. Load model first or use dry_run=true")
    
    # Get conversation messages
    messages = _db_manager.get_messages(conv_id)
    history = [{"role": msg[2], "content": msg[3]} for msg in messages]
    
    # Generate response
    try:
        if request.dry_run:
            response = _model_manager.generate_response_dry_run(
                history, **request.params.model_dump()
            )
        else:
            response = _model_manager.generate_response(
                history, **request.params.model_dump()
            )
        
        # Save assistant response
        _db_manager.add_message(conv_id, "assistant", response)
        
        return {
            "response": response,
            "conversation_id": conv_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


# ============================================================================
# WebSocket Endpoint for Streaming
# ============================================================================

@app.websocket("/ws/chat/{conv_id}")
async def websocket_chat(websocket: WebSocket, conv_id: int):
    """
    WebSocket endpoint for streaming chat responses.
    
    This provides real-time streaming of model responses.
    The client sends a message with generation parameters, and receives
    the response as it's being generated.
    """
    if not _db_manager or not _model_manager:
        await websocket.close(code=1011, reason="Backend not initialized")
        return
    
    # Check if conversation exists
    conv_data = _db_manager.get_conversation(conv_id)
    if not conv_data:
        await websocket.close(code=1008, reason=f"Conversation {conv_id} not found")
        return
    
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Get conversation history
            messages = _db_manager.get_messages(conv_id)
            history = [{"role": msg[2], "content": msg[3]} for msg in messages]
            
            # Add user message to history if provided
            if "message" in data and "role" in data:
                history.append({"role": data["role"], "content": data["message"]})
            
            # Get generation parameters
            params = data.get("params", {})
            dry_run = data.get("dry_run", False)
            
            # Check model status
            if not dry_run and not _model_manager.is_loaded():
                await websocket.send_json({
                    "error": "Model not loaded. Load model first or use dry_run=true"
                })
                continue
            
            try:
                # For now, send complete response
                # In a production implementation, you would stream tokens one by one
                if dry_run:
                    response = _model_manager.generate_response_dry_run(
                        history, **params
                    )
                else:
                    response = _model_manager.generate_response(
                        history, **params
                    )
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "response": response,
                    "conversation_id": conv_id,
                })
                
                # Save assistant response to database
                _db_manager.add_message(conv_id, "assistant", response)
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "error": str(e),
                })
                
    except Exception as e:
        # Handle disconnection
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))


# ============================================================================
# Quantization Options Endpoint
# ============================================================================

@app.get("/api/model/quantization-options")
async def get_quantization_options():
    """Get available quantization options."""
    return {
        "options": list(QUANTIZATION_METHODS.keys()),
        "descriptions": {
            "none": "No quantization (full precision, ~15GB VRAM for 3B)",
            "8bit": "8-bit quantization (~6-8GB VRAM)",
            "4bit": "4-bit quantization (~3-4GB VRAM)",
            "fp8": "FP8 quantization (NVIDIA GPUs, ~4GB VRAM)",
        },
    }


# ============================================================================
# Default Generation Parameters Endpoint
# ============================================================================

@app.get("/api/model/default-params", response_model=GenerationParams)
async def get_default_params():
    """Get default generation parameters."""
    from src.core.model import DEFAULT_GEN_PARAMS
    return GenerationParams(**DEFAULT_GEN_PARAMS.to_dict())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
