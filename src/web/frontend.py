"""
Streamlit frontend for Mistral Chat Application.

Run with: streamlit run src/web/frontend.py
"""

import os
import sys
from datetime import datetime

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.database import get_database_manager
from src.core.model import (
    DEFAULT_GEN_PARAMS,
    GEN_PARAM_DESCRIPTIONS,
    QUANTIZATION_DESCRIPTIONS,
    QUANTIZATION_METHODS,
    get_model_manager,
)


def init_session():
    """Initialize session state."""
    if "current_conv_id" not in st.session_state:
        st.session_state.current_conv_id = None
    if "new_conv_title" not in st.session_state:
        st.session_state.new_conv_title = "New Chat"
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "generating" not in st.session_state:
        st.session_state.generating = False
    # Initialize generation parameters with defaults
    for param, default_val in DEFAULT_GEN_PARAMS.to_dict().items():
        if param not in st.session_state:
            st.session_state[param] = default_val


def load_conversation(conv_id: int) -> list:
    """Load conversation messages."""
    manager = get_database_manager()
    messages = manager.get_messages(conv_id)
    return [{"role": msg[2], "content": msg[3], "timestamp": msg[4]} for msg in messages]


def format_timestamp(ts: str) -> str:
    """Format timestamp for display."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def main():
    # Initialize database and session
    get_database_manager().init_db()
    init_session()

    st.set_page_config(page_title="Mistral Chat", page_icon="💬", layout="wide")

    st.title("💬 Mistral Chat")

    # Sidebar: Model Loading
    st.sidebar.header("🤖 Model")

    # Quantization selection
    quant_options = list(QUANTIZATION_METHODS.keys())

    if "quant_method" not in st.session_state:
        st.session_state.quant_method = "fp8"

    if "auto_load_model" not in st.session_state:
        st.session_state.auto_load_model = False

    st.session_state.quant_method = st.sidebar.selectbox(
        "Quantization",
        options=quant_options,
        index=quant_options.index(st.session_state.quant_method),
        help="\n".join(f"{opt}: {QUANTIZATION_DESCRIPTIONS.get(opt, '')}" for opt in quant_options),
    )

    st.session_state.auto_load_model = st.sidebar.checkbox(
        "Auto-load model on startup",
        value=st.session_state.auto_load_model,
        help="Automatically load the model when the app starts",
    )

    # Check if in dry-run mode
    dry_run_enabled = os.environ.get("MISTRAL_DRY_RUN", "").lower() in ("1", "true", "yes")

    # Show dry-run notice if enabled
    if dry_run_enabled:
        st.sidebar.success("🎭 Dry-run mode: Mock responses only (no model loading)")

    # Auto-load model if enabled and not already loaded (skip in dry-run)
    model_manager = get_model_manager()
    if (
        st.session_state.auto_load_model
        and not dry_run_enabled
        and not model_manager.is_loaded()
        and not model_manager.is_loading()
    ):
        with st.spinner("Loading model automatically... This may take a few minutes."):
            model_manager.load_model(quant_method=st.session_state.quant_method)
        st.rerun()

    # Model loading controls
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button(
            "🚀 Load Model",
            use_container_width=True,
            disabled=model_manager.is_loaded() or model_manager.is_loading() or dry_run_enabled,
        ):
            with st.spinner("Loading model... This may take a few minutes."):
                model_manager.load_model(quant_method=st.session_state.quant_method)
            st.rerun()

    with col2:
        model_status = model_manager.get_status()
        st.sidebar.info(model_status)

    st.sidebar.markdown("---")

    # Sidebar: Conversation list
    st.sidebar.header("Conversations")

    # New conversation button
    if st.sidebar.button("🆕 New Chat", use_container_width=True):
        manager = get_database_manager()
        conv_id = manager.create_conversation("New Chat")
        st.session_state.current_conv_id = conv_id
        st.session_state.new_conv_title = "New Chat"
        st.rerun()

    # List existing conversations
    manager = get_database_manager()
    conversations = manager.list_conversations(limit=50)

    if conversations:
        st.sidebar.markdown("---")
        for conv in conversations:
            conv_id, title, created_at, updated_at = conv
            with st.sidebar.expander(f"📝 {title}"):
                st.write(f"Updated: {format_timestamp(updated_at)}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Open", key=f"open_{conv_id}"):
                        st.session_state.current_conv_id = conv_id
                        st.session_state.new_conv_title = title
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{conv_id}"):
                        manager.delete_conversation(conv_id)
                        if st.session_state.current_conv_id == conv_id:
                            st.session_state.current_conv_id = None
                        st.rerun()
    else:
        st.sidebar.info("No conversations yet. Start a new one!")

    # Sidebar: Generation Parameters
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Generation Parameters")

    # Float parameters (sliders)
    st.session_state.max_new_tokens = st.sidebar.slider(
        "max_new_tokens",
        min_value=16,
        max_value=2048,
        value=int(st.session_state.max_new_tokens),
        step=16,
        help=GEN_PARAM_DESCRIPTIONS.get("max_new_tokens", ""),
    )

    st.session_state.temperature = st.sidebar.slider(
        "temperature",
        min_value=0.0,
        max_value=2.0,
        value=float(st.session_state.temperature),
        step=0.05,
        format="%.2f",
        help=GEN_PARAM_DESCRIPTIONS.get("temperature", ""),
    )

    st.session_state.top_p = st.sidebar.slider(
        "top_p",
        min_value=0.0,
        max_value=1.0,
        value=float(st.session_state.top_p),
        step=0.05,
        format="%.2f",
        help=GEN_PARAM_DESCRIPTIONS.get("top_p", ""),
    )

    st.session_state.repetition_penalty = st.sidebar.slider(
        "repetition_penalty",
        min_value=0.5,
        max_value=2.0,
        value=float(st.session_state.repetition_penalty),
        step=0.1,
        format="%.2f",
        help=GEN_PARAM_DESCRIPTIONS.get("repetition_penalty", ""),
    )

    # Integer parameters (sliders)
    st.session_state.top_k = st.sidebar.slider(
        "top_k",
        min_value=1,
        max_value=200,
        value=int(st.session_state.top_k),
        step=1,
        help=GEN_PARAM_DESCRIPTIONS.get("top_k", ""),
    )

    st.session_state.num_return_sequences = st.sidebar.slider(
        "num_return_sequences",
        min_value=1,
        max_value=5,
        value=int(st.session_state.num_return_sequences),
        step=1,
        help=GEN_PARAM_DESCRIPTIONS.get("num_return_sequences", ""),
    )

    # Boolean parameter (checkbox)
    st.session_state.do_sample = st.sidebar.checkbox(
        "do_sample",
        value=bool(st.session_state.do_sample),
        help=GEN_PARAM_DESCRIPTIONS.get("do_sample", ""),
    )

    # Main chat area
    if st.session_state.current_conv_id:
        conv_data = manager.get_conversation(st.session_state.current_conv_id)
        if conv_data:
            conv_id, title, created_at, updated_at = conv_data

            # Editable title
            new_title = st.text_input(
                "Conversation title", value=st.session_state.new_conv_title, key="title_input"
            )
            if new_title != st.session_state.new_conv_title:
                manager.update_conversation_title(conv_id, new_title)
                st.session_state.new_conv_title = new_title
                st.rerun()

            # Display messages
            messages = load_conversation(conv_id)

            if messages:
                for msg in messages:
                    timestamp = format_timestamp(msg["timestamp"])
                    if msg["role"] == "user":
                        with st.chat_message("user"):
                            st.markdown(f"**{timestamp}**")
                            st.markdown(msg["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(f"**{timestamp}**")
                            st.markdown(msg["content"])
            else:
                st.info("Start the conversation by sending a message below.")

            # Input area
            st.markdown("---")

            # Check if model is ready
            model_ready = model_manager.is_loaded() or dry_run_enabled

            if not model_ready:
                st.warning(
                    "⚠️ Please load the model first using the 'Load Model' button in the sidebar."
                )

            user_input = st.chat_input(
                "Type your message here...", key="chat_input", disabled=not model_ready
            )

            if user_input:
                # Add user message to DB
                manager.add_message(conv_id, "user", user_input)

                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_input)

                # Get history for model
                messages = load_conversation(conv_id)
                history = [{"role": m["role"], "content": m["content"]} for m in messages]

                # Show thinking indicator
                with st.chat_message("assistant"):
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("Thinking...")

                # Generate response
                try:
                    # Build generation kwargs from session state
                    gen_kwargs = {
                        "max_new_tokens": int(st.session_state.max_new_tokens),
                        "temperature": float(st.session_state.temperature),
                        "do_sample": bool(st.session_state.do_sample),
                        "top_k": int(st.session_state.top_k),
                        "top_p": float(st.session_state.top_p),
                        "repetition_penalty": float(st.session_state.repetition_penalty),
                        "num_return_sequences": int(st.session_state.num_return_sequences),
                    }

                    # Use dry-run mode if environment variable is set
                    if dry_run_enabled:
                        response = model_manager.generate_response_dry_run(history, **gen_kwargs)
                    else:
                        response = model_manager.generate_response(history, **gen_kwargs)

                    # Clear thinking, show response
                    thinking_placeholder.empty()
                    st.markdown(response)

                    # Save assistant response to DB
                    manager.add_message(conv_id, "assistant", response)

                    # Rerun to update message display
                    st.rerun()
                except Exception as e:
                    thinking_placeholder.error(f"Error: {e}")
        else:
            st.error("Conversation not found.")
            st.session_state.current_conv_id = None
            st.rerun()
    else:
        st.info("👈 Select or create a conversation from the sidebar to start chatting.")


if __name__ == "__main__":
    main()
