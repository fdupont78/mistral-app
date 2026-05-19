"""
Streamlit frontend for Mistral 3B Chat Application.

Run with: streamlit run frontend.py
"""
import streamlit as st
from datetime import datetime
from database import (
    init_db, list_conversations, get_conversation, get_messages,
    create_conversation, add_message, delete_conversation, update_conversation_title
)
import os
from model import generate_response, generate_response_dry_run, DEFAULT_GEN_PARAMS, GEN_PARAM_DESCRIPTIONS


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
    for param, default_val in DEFAULT_GEN_PARAMS.items():
        if param not in st.session_state:
            st.session_state[param] = default_val


def load_conversation(conv_id):
    """Load conversation messages."""
    messages = get_messages(conv_id)
    return [
        {"role": msg[2], "content": msg[3], "timestamp": msg[4]}
        for msg in messages
    ]


def format_timestamp(ts):
    """Format timestamp for display."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return ts


def main():
    init_db()
    init_session()
    
    st.set_page_config(
        page_title="Mistral 3B Chat",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 Mistral 3B Chat")
    
    # Sidebar: Conversation list
    st.sidebar.header("Conversations")
    
    # New conversation button
    if st.sidebar.button("🆕 New Chat", use_container_width=True):
        conv_id = create_conversation("New Chat")
        st.session_state.current_conv_id = conv_id
        st.session_state.new_conv_title = "New Chat"
        st.rerun()
    
    # List existing conversations
    conversations = list_conversations(limit=50)
    
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
                        delete_conversation(conv_id)
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
        help=GEN_PARAM_DESCRIPTIONS.get('max_new_tokens', '')
    )
    
    st.session_state.temperature = st.sidebar.slider(
        "temperature",
        min_value=0.0,
        max_value=2.0,
        value=float(st.session_state.temperature),
        step=0.05,
        format="%.2f",
        help=GEN_PARAM_DESCRIPTIONS.get('temperature', '')
    )
    
    st.session_state.top_p = st.sidebar.slider(
        "top_p",
        min_value=0.0,
        max_value=1.0,
        value=float(st.session_state.top_p),
        step=0.05,
        format="%.2f",
        help=GEN_PARAM_DESCRIPTIONS.get('top_p', '')
    )
    
    st.session_state.repetition_penalty = st.sidebar.slider(
        "repetition_penalty",
        min_value=0.5,
        max_value=2.0,
        value=float(st.session_state.repetition_penalty),
        step=0.1,
        format="%.2f",
        help=GEN_PARAM_DESCRIPTIONS.get('repetition_penalty', '')
    )
    
    # Integer parameters (sliders)
    st.session_state.top_k = st.sidebar.slider(
        "top_k",
        min_value=1,
        max_value=200,
        value=int(st.session_state.top_k),
        step=1,
        help=GEN_PARAM_DESCRIPTIONS.get('top_k', '')
    )
    
    st.session_state.num_return_sequences = st.sidebar.slider(
        "num_return_sequences",
        min_value=1,
        max_value=5,
        value=int(st.session_state.num_return_sequences),
        step=1,
        help=GEN_PARAM_DESCRIPTIONS.get('num_return_sequences', '')
    )
    
    # Boolean parameter (checkbox)
    st.session_state.do_sample = st.sidebar.checkbox(
        "do_sample",
        value=bool(st.session_state.do_sample),
        help=GEN_PARAM_DESCRIPTIONS.get('do_sample', '')
    )
    
    # Main chat area
    if st.session_state.current_conv_id:
        conv_data = get_conversation(st.session_state.current_conv_id)
        if conv_data:
            conv_id, title, created_at, updated_at = conv_data
            
            # Editable title
            new_title = st.text_input(
                "Conversation title",
                value=st.session_state.new_conv_title,
                key="title_input"
            )
            if new_title != st.session_state.new_conv_title:
                update_conversation_title(conv_id, new_title)
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
            user_input = st.chat_input(
                "Type your message here...",
                key="chat_input"
            )
            
            if user_input:
                # Add user message to DB
                add_message(conv_id, "user", user_input)
                
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
                        'max_new_tokens': int(st.session_state.max_new_tokens),
                        'temperature': float(st.session_state.temperature),
                        'do_sample': bool(st.session_state.do_sample),
                        'top_k': int(st.session_state.top_k),
                        'top_p': float(st.session_state.top_p),
                        'repetition_penalty': float(st.session_state.repetition_penalty),
                        'num_return_sequences': int(st.session_state.num_return_sequences),
                    }
                    
                    # Use dry-run mode if environment variable is set
                    if os.environ.get('MISTRAL_DRY_RUN', '').lower() in ('1', 'true', 'yes'):
                        response = generate_response_dry_run(history, **gen_kwargs)
                    else:
                        response = generate_response(history, **gen_kwargs)
                    
                    # Clear thinking, show response
                    thinking_placeholder.empty()
                    st.markdown(response)
                    
                    # Save assistant response to DB
                    add_message(conv_id, "assistant", response)
                    
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
