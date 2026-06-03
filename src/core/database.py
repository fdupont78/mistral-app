"""
Database module for conversation persistence.
Uses SQLite for storing conversations and messages.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime


class DatabaseManager:
    """
    Manages SQLite database operations for conversations and messages.

    Provides a context manager for database connections and methods for
    CRUD operations on conversations and messages.
    """

    def __init__(self, db_path: str | None = None):
        """
        Initialize the DatabaseManager.

        Args:
            db_path: Path to the SQLite database file.
                     If None, uses default path 'conversations.db' in the package directory.
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "conversations.db"
            )
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Ensure the database file exists and has required tables."""
        self.init_db()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: A database connection object.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_db(self):
        """Initialize the SQLite database with tables for conversations and messages."""
        with self.get_connection() as conn:
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

            # Add indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)"
            )

            # Add trigger to auto-update conversation timestamp on new message
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_conversation_on_message
                AFTER INSERT ON messages
                FOR EACH ROW
                BEGIN
                    UPDATE conversations 
                    SET updated_at = datetime('now') 
                    WHERE id = NEW.conversation_id;
                END
            """)

    def create_conversation(self, title: str = "New Chat") -> int:
        """
        Create a new conversation and return its ID.

        Args:
            title: Title for the new conversation.

        Returns:
            int: The ID of the newly created conversation.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
                (title, now, now),
            )
            conversation_id = cursor.lastrowid
            return conversation_id

    def update_conversation_title(self, conversation_id: int, title: str):
        """
        Update the title of a conversation.

        Args:
            conversation_id: ID of the conversation to update.
            title: New title for the conversation.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, datetime.now().isoformat(), conversation_id),
            )

    def update_conversation_timestamp(self, conversation_id: int):
        """
        Update the updated_at timestamp of a conversation.

        Args:
            conversation_id: ID of the conversation to update.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), conversation_id),
            )

    def delete_conversation(self, conversation_id: int):
        """
        Delete a conversation and all its messages (cascade).

        Args:
            conversation_id: ID of the conversation to delete.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

    def add_message(self, conversation_id: int, role: str, content: str) -> int:
        """
        Add a message to a conversation and return its ID.

        Args:
            conversation_id: ID of the conversation to add the message to.
            role: Role of the message (e.g., 'user', 'assistant').
            content: Content of the message.

        Returns:
            int: The ID of the newly created message.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, timestamp),
            )
            message_id = cursor.lastrowid
            # Note: conversation timestamp is auto-updated by trigger
            return message_id

    def get_conversation(self, conversation_id: int) -> tuple | None:
        """
        Get conversation details by ID.

        Args:
            conversation_id: ID of the conversation to retrieve.

        Returns:
            Optional[Tuple]: Conversation data as a tuple (id, title, created_at, updated_at) or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
                (conversation_id,),
            )
            result = cursor.fetchone()
            return tuple(result) if result else None

    def get_messages(self, conversation_id: int) -> list[tuple]:
        """
        Get all messages for a conversation, ordered by timestamp.

        Args:
            conversation_id: ID of the conversation to get messages from.

        Returns:
            List[Tuple]: List of message tuples (id, conversation_id, role, content, timestamp).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, conversation_id, role, content, timestamp FROM messages "
                "WHERE conversation_id = ? ORDER BY timestamp ASC",
                (conversation_id,),
            )
            results = cursor.fetchall()
            return [tuple(row) for row in results]

    def list_conversations(self, limit: int = 50) -> list[tuple]:
        """
        List all conversations, ordered by updated_at descending.

        Args:
            limit: Maximum number of conversations to return.

        Returns:
            List[Tuple]: List of conversation tuples (id, title, created_at, updated_at).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations "
                "ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
            results = cursor.fetchall()
            return [tuple(row) for row in results]

    def search_conversations(self, query: str, limit: int = 20) -> list[tuple]:
        """
        Search conversations by title.

        Args:
            query: Search query string.
            limit: Maximum number of conversations to return.

        Returns:
            List[Tuple]: List of matching conversation tuples.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations "
                "WHERE title LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (f"%{query}%", limit),
            )
            results = cursor.fetchall()
            return [tuple(row) for row in results]

    def conversation_exists(self, conversation_id: int) -> bool:
        """
        Check if a conversation exists.

        Args:
            conversation_id: ID of the conversation to check.

        Returns:
            bool: True if the conversation exists, False otherwise.
        """
        return self.get_conversation(conversation_id) is not None


# Global instance for backward compatibility
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global DatabaseManager instance.

    Returns:
        DatabaseManager: The global database manager instance.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# Backward compatibility functions (deprecated, use DatabaseManager directly)
def init_db():
    """Initialize the database (backward compatibility)."""
    get_database_manager().init_db()


def create_conversation(title: str = "New Chat") -> int:
    """Create a new conversation (backward compatibility)."""
    return get_database_manager().create_conversation(title)


def update_conversation_title(conversation_id: int, title: str):
    """Update conversation title (backward compatibility)."""
    get_database_manager().update_conversation_title(conversation_id, title)


def update_conversation_timestamp(conversation_id: int):
    """Update conversation timestamp (backward compatibility)."""
    get_database_manager().update_conversation_timestamp(conversation_id)


def delete_conversation(conversation_id: int):
    """Delete a conversation (backward compatibility)."""
    get_database_manager().delete_conversation(conversation_id)


def add_message(conversation_id: int, role: str, content: str) -> int:
    """Add a message (backward compatibility)."""
    return get_database_manager().add_message(conversation_id, role, content)


def get_conversation(conversation_id: int) -> tuple | None:
    """Get conversation (backward compatibility)."""
    return get_database_manager().get_conversation(conversation_id)


def get_messages(conversation_id: int) -> list[tuple]:
    """Get messages (backward compatibility)."""
    return get_database_manager().get_messages(conversation_id)


def list_conversations(limit: int = 50) -> list[tuple]:
    """List conversations (backward compatibility)."""
    return get_database_manager().list_conversations(limit)


def search_conversations(query: str, limit: int = 20) -> list[tuple]:
    """Search conversations (backward compatibility)."""
    return get_database_manager().search_conversations(query, limit)
