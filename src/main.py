#!/usr/bin/env python3
"""
Mistral Chat Application

Entry point for the chat application.
Run with: python -m src.main or uv run python src/main.py

Commands:
  python src/main.py chat    - Start interactive chat
  python src/main.py list   - List all conversations
  python src/main.py load <id> - Load a conversation
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.cli.chat import handle_load, interactive_chat, list_conversations
from src.core.database import get_database_manager


def main():
    # Initialize database
    get_database_manager().init_db()

    # Check for --dry-run flag in arguments
    dry_run = "--dry-run" in sys.argv
    # Remove --dry-run from argv for command parsing
    argv = [arg for arg in sys.argv if arg != "--dry-run"]

    if len(argv) < 2:
        # Default: start interactive chat
        interactive_chat(dry_run=dry_run)
    else:
        command = argv[1].lower()

        if command == "chat":
            interactive_chat(dry_run=dry_run)

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
            print("Usage: python -m src.main [command] [--dry-run]")
            print("\nCommands:")
            print("  chat       - Start interactive chat")
            print("  list       - List all conversations")
            print("  load <id>  - Load and display a conversation")
            print("\nOptions:")
            print("  --dry-run  - Use mock responses instead of loading the model (for debugging)")
            print("\nIn interactive mode:")
            print("  /new      - Start new conversation")
            print("  /list     - List conversations")
            print("  /load <id>- Load conversation")
            print("  /title <t>- Set title")
            print("  /delete   - Delete current conversation")
            print("  /quit     - Exit")

        else:
            print(f"Unknown command: {command}")
            print("Use 'python -m src.main help' for usage")


if __name__ == "__main__":
    main()
