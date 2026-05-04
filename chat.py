"""
CLI chat interface for Mistral 3B model.
Provides interactive chat with conversation persistence.
"""
import sys
from conversation import Conversation
from model import generate_response
from database import init_db
from datetime import datetime


def print_welcome():
    """Print welcome message."""
    print("\n" + "=" * 60)
    print("  Mistral 3B Chat Application")
    print("=" * 60)
    print("\nCommands:")
    print("  /new         - Start a new conversation")
    print("  /list        - List all conversations")
    print("  /load <id>   - Load conversation by ID")
    print("  /title <t>   - Set conversation title")
    print("  /delete      - Delete current conversation")
    print("  /quit        - Exit the application")
    print("  /help        - Show this help")
    print("=" * 60 + "\n")


def print_conversation_info(conv: Conversation):
    """Print information about the current conversation."""
    print(f"\n[Conversation #{conv.conversation_id}: {conv.title}]")
    print(f"Created: {conv.created_at}")
    print(f"Messages: {len(conv.messages)}")
    print("-" * 60)


def print_message_history(conv: Conversation):
    """Print the message history."""
    if not conv.messages:
        print("  (No messages yet)")
        return
    
    for msg in conv.messages:
        role = msg.role.upper()
        timestamp = msg.timestamp[:19] if msg.timestamp else ""
        print(f"\n[{timestamp}] {role}:")
        print(f"  {msg.content}")


def list_conversations():
    """List all conversations."""
    conversations = Conversation.list_all()
    if not conversations:
        print("\nNo conversations found.")
        return
    
    print("\n" + "=" * 60)
    print("  Your Conversations")
    print("=" * 60)
    for conv in conversations:
        updated = conv.updated_at[:19] if conv.updated_at else ""
        print(f"  [{conv.conversation_id}] {conv.title}")
        print(f"    Updated: {updated} | Messages: {len(conv.messages) if hasattr(conv, 'messages') else '0'}")
    print("=" * 60 + "\n")


def handle_load(conversation_id: int) -> Conversation:
    """Load a conversation by ID."""
    try:
        conv = Conversation.load(conversation_id)
        print(f"\nLoaded conversation: {conv.title}")
        return conv
    except ValueError as e:
        print(f"\nError: {e}")
        return None


def interactive_chat():
    """Run the interactive chat CLI."""
    init_db()
    
    current_conversation: Conversation = None
    print_welcome()
    
    # Create a default conversation
    current_conversation = Conversation.create("New Chat")
    print_conversation_info(current_conversation)
    
    while True:
        try:
            if current_conversation:
                print_conversation_info(current_conversation)
                print_message_history(current_conversation)
            
            # Get user input
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input[1:].strip().split()
                cmd = command[0].lower() if command else ""
                args = command[1:] if len(command) > 1 else []
                
                if cmd == "new":
                    current_conversation = Conversation.create("New Chat")
                    print(f"\nStarted new conversation (ID: {current_conversation.conversation_id})")
                    continue
                
                elif cmd == "list":
                    list_conversations()
                    continue
                
                elif cmd == "load" and args:
                    try:
                        conv_id = int(args[0])
                        current_conversation = handle_load(conv_id)
                        if current_conversation:
                            # Reload messages
                            current_conversation = Conversation.load(conv_id)
                        continue
                    except ValueError:
                        print("Error: Conversation ID must be a number")
                        continue
                
                elif cmd == "title" and args:
                    if current_conversation:
                        new_title = " ".join(args)
                        current_conversation.set_title(new_title)
                        print(f"Conversation title updated to: {new_title}")
                    else:
                        print("Error: No active conversation")
                    continue
                
                elif cmd == "delete":
                    if current_conversation:
                        conv_id = current_conversation.conversation_id
                        current_conversation.delete()
                        print(f"Deleted conversation #{conv_id}")
                        current_conversation = None
                    else:
                        print("Error: No active conversation")
                    continue
                
                elif cmd in ["quit", "exit", "q"]:
                    print("\nGoodbye!")
                    sys.exit(0)
                
                elif cmd in ["help", "h"]:
                    print_welcome()
                    continue
                
                else:
                    print(f"Unknown command: /{cmd}")
                    continue
            
            # Process user message
            if current_conversation is None:
                current_conversation = Conversation.create("New Chat")
            
            # Add user message
            current_conversation.add_message("user", user_input)
            
            # Get model response
            print("\n[Thinking...]")
            history = current_conversation.get_history_for_model()
            response = generate_response(history)
            
            # Add assistant message
            current_conversation.add_message("assistant", response)
            
            # Reload conversation to get updated data
            if current_conversation.conversation_id > 0:
                current_conversation = Conversation.load(current_conversation.conversation_id)
            
        except KeyboardInterrupt:
            print("\n\nUse /quit to exit")
        except EOFError:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    interactive_chat()
