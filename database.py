import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")


def init_db():
    """Initialize the SQLite database with tables for conversations and messages."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def create_conversation(title: str = "New Chat") -> int:
    """Create a new conversation and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
        (title, now, now)
    )
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id


def update_conversation_title(conversation_id: int, title: str):
    """Update the title of a conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
        (title, datetime.now().isoformat(), conversation_id)
    )
    conn.commit()
    conn.close()


def update_conversation_timestamp(conversation_id: int):
    """Update the updated_at timestamp of a conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), conversation_id)
    )
    conn.commit()
    conn.close()


def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages (cascade)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()


def add_message(conversation_id: int, role: str, content: str) -> int:
    """Add a message to a conversation and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, timestamp)
    )
    message_id = cursor.lastrowid
    conn.commit()
    update_conversation_timestamp(conversation_id)
    conn.close()
    return message_id


def get_conversation(conversation_id: int) -> Optional[Tuple]:
    """Get conversation details by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?", (conversation_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_messages(conversation_id: int) -> List[Tuple]:
    """Get all messages for a conversation, ordered by timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, conversation_id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
        (conversation_id,)
    )
    results = cursor.fetchall()
    conn.close()
    return results


def list_conversations(limit: int = 50) -> List[Tuple]:
    """List all conversations, ordered by updated_at descending."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
        (limit,)
    )
    results = cursor.fetchall()
    conn.close()
    return results


def search_conversations(query: str, limit: int = 20) -> List[Tuple]:
    """Search conversations by title."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM conversations WHERE title LIKE ? ORDER BY updated_at DESC LIMIT ?",
        (f"%{query}%", limit)
    )
    results = cursor.fetchall()
    conn.close()
    return results
