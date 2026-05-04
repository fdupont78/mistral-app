#!/usr/bin/env python3
"""
Mistral 3B Chat Application

Entry point for the chat application.
Run with: python main.py or uv run python main.py

Commands:
  python main.py chat    - Start interactive chat
  python main.py list   - List all conversations
  python main.py load <id> - Load a conversation
"""
import sys
from database import init_db
from chat import interactive_chat, list_conversations, handle_load
from conversation import Conversation


def main():
    init_db()
    
    if len(sys.argv) < 2:
        # Default: start interactive chat
        interactive_chat()
    else:
        command = sys.argv[1].lower()
        
        if command == "chat":
            interactive_chat()
        
        elif command == "list":
            list_conversations()
        
        elif command == "load" and len(sys.argv) > 2:
            try:
                conv_id = int(sys.argv[2])
                conv = handle_load(conv_id)
                if conv:
                    print(f"Loaded: {conv}")
                    # Print messages
                    for msg in conv.messages:
                        print(f"{msg.role.upper()}: {msg.content}")
            except ValueError:
                print("Error: Conversation ID must be a number")
        
        elif command in ["help", "--help", "-h"]:
            print("Usage: python main.py [command]")
            print("\nCommands:")
            print("  chat       - Start interactive chat")
            print("  list       - List all conversations")
            print("  load <id>  - Load and display a conversation")
            print("\nIn interactive mode:")
            print("  /new      - Start new conversation")
            print("  /list     - List conversations")
            print("  /load <id>- Load conversation")
            print("  /title <t>- Set title")
            print("  /delete   - Delete current conversation")
            print("  /quit     - Exit")
        
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main.py help' for usage")


if __name__ == "__main__":
    main()
