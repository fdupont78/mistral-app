#!/usr/bin/env python3
"""
Mistral Chat Application

Entry point for the chat application.
Run with: python -m src.main or uv run python src/main.py

Commands:
  python src/main.py chat    - Start interactive chat
  python src/main.py list   - List all conversations
  python src/main.py load <id> - Load a conversation
  python src/main.py deploy --branch <branch> - Deploy to RunPod
"""

import argparse
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.cli.chat import handle_load, interactive_chat, list_conversations
from src.cli.deploy import deploy_to_runpod
from src.core.database import get_database_manager


def main():
    # Initialize database
    get_database_manager().init_db()

    # Remove --dry-run from argv for argparse
    dry_run = "--dry-run" in sys.argv
    argv = [arg for arg in sys.argv if arg != "--dry-run"]

    parser = argparse.ArgumentParser(description="Mistral App CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat command
    subparsers.add_parser("chat", help="Start interactive chat")

    # List command
    subparsers.add_parser("list", help="List all conversations")

    # Load command
    load_parser = subparsers.add_parser("load", help="Load a conversation")
    load_parser.add_argument("id", type=int, help="Conversation ID")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to RunPod")
    deploy_parser.add_argument(
        "--branch", default="master", help="Branch to deploy (default: master)"
    )
    deploy_parser.add_argument(
        "--api-key", help="RunPod API key (overrides RUNPOD_API_KEY env var)"
    )
    deploy_parser.add_argument(
        "--template-id", default="hsrb8il0fj", help="RunPod template ID (default: hsrb8il0fj)"
    )

    args = parser.parse_args(argv[1:])

    if not args.command:
        # Default: start interactive chat
        interactive_chat(dry_run=dry_run)

    elif args.command == "chat":
        interactive_chat(dry_run=dry_run)

    elif args.command == "list":
        list_conversations()

    elif args.command == "load":
        conv = handle_load(args.id)
        if conv:
            print(f"Loaded: {conv}")
            for msg in conv.messages:
                print(f"{msg.role.upper()}: {msg.content}")

    elif args.command == "deploy":
        deploy_to_runpod(
            branch=args.branch,
            api_key=args.api_key,
            template_id=args.template_id,
        )

    elif args.command in ["help", "--help", "-h"]:
        parser.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
