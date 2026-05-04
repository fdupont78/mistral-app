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
from model import generate_response


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
                    response = generate_response(history)
                    
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
