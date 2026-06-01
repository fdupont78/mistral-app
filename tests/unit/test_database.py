"""
Unit tests for DatabaseManager class.
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))



@pytest.mark.unit
class TestDatabaseManager:
    """Test DatabaseManager class."""

    def test_init_db_creates_tables(self, db_manager):
        """Test that init_db creates the required tables."""
        # Connect to the database and check tables exist
        import sqlite3

        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()

        # Check conversations table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
        assert cursor.fetchone() is not None

        # Check messages table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        assert cursor.fetchone() is not None

        conn.close()

    def test_create_conversation(self, db_manager):
        """Test creating a new conversation."""
        conv_id = db_manager.create_conversation("Test Title")
        assert conv_id > 0

        # Verify it was created
        conv = db_manager.get_conversation(conv_id)
        assert conv is not None
        assert conv[1] == "Test Title"  # title is at index 1

    def test_create_conversation_default_title(self, db_manager):
        """Test creating a conversation with default title."""
        conv_id = db_manager.create_conversation()
        assert conv_id > 0

        conv = db_manager.get_conversation(conv_id)
        assert conv[1] == "New Chat"

    def test_update_conversation_title(self, db_manager):
        """Test updating a conversation title."""
        conv_id = db_manager.create_conversation("Original Title")
        db_manager.update_conversation_title(conv_id, "Updated Title")

        conv = db_manager.get_conversation(conv_id)
        assert conv[1] == "Updated Title"

    def test_add_message(self, db_manager):
        """Test adding a message to a conversation."""
        conv_id = db_manager.create_conversation("Test Conv")

        # Use a separate connection to avoid locking
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv_id, "user", "Hello world", timestamp),
            )
            msg_id = cursor.lastrowid

        assert msg_id > 0

        # Verify the message was added
        messages = db_manager.get_messages(conv_id)
        assert len(messages) == 1
        assert messages[0][2] == "user"  # role
        assert messages[0][3] == "Hello world"  # content

    def test_get_conversation_not_found(self, db_manager):
        """Test getting a non-existent conversation."""
        result = db_manager.get_conversation(99999)
        assert result is None

    def test_get_messages_empty(self, db_manager):
        """Test getting messages from a conversation with no messages."""
        conv_id = db_manager.create_conversation("Empty Conv")
        messages = db_manager.get_messages(conv_id)
        assert messages == []

    def test_list_conversations(self, db_manager):
        """Test listing conversations."""
        # Create some conversations
        conv1 = db_manager.create_conversation("First")
        conv2 = db_manager.create_conversation("Second")

        conversations = db_manager.list_conversations()
        assert len(conversations) >= 2

        # Check that our conversations are in the list
        ids = [c[0] for c in conversations]
        assert conv1 in ids
        assert conv2 in ids

    def test_delete_conversation(self, db_manager):
        """Test deleting a conversation."""
        conv_id = db_manager.create_conversation("To Delete")

        # Add a message using the same connection pattern
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv_id, "user", "Test message", timestamp),
            )
            # Also update the conversation timestamp to ensure consistency
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?", (timestamp, conv_id)
            )

        # Verify it exists
        assert db_manager.get_conversation(conv_id) is not None
        assert len(db_manager.get_messages(conv_id)) == 1

        # Delete it - this should cascade to messages
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))

        # Verify it's gone
        assert db_manager.get_conversation(conv_id) is None
        # Messages should be cascade deleted
        assert len(db_manager.get_messages(conv_id)) == 0

    def test_search_conversations(self, db_manager):
        """Test searching conversations by title."""
        db_manager.create_conversation("Test Conversation")
        db_manager.create_conversation("Another Chat")
        db_manager.create_conversation("Test Again")

        results = db_manager.search_conversations("Test")
        assert len(results) >= 2

        # Check that all results contain "Test" in title
        for conv in results:
            assert "Test" in conv[1]

    def test_conversation_exists(self, db_manager):
        """Test checking if a conversation exists."""
        conv_id = db_manager.create_conversation("Exists")

        assert db_manager.conversation_exists(conv_id) is True
        assert db_manager.conversation_exists(99999) is False

    def test_update_conversation_timestamp(self, db_manager):
        """Test updating conversation timestamp."""
        import time

        conv_id = db_manager.create_conversation("Timestamp Test")

        # Get initial timestamp
        conv = db_manager.get_conversation(conv_id)
        initial_updated_at = conv[3]

        # Wait a bit and update
        time.sleep(0.1)
        db_manager.update_conversation_timestamp(conv_id)

        # Get updated timestamp
        conv = db_manager.get_conversation(conv_id)
        updated_updated_at = conv[3]

        # Timestamps should be different
        assert initial_updated_at != updated_updated_at

    def test_get_connection_context_manager(self, db_manager):
        """Test the get_connection context manager."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1

        # Connection should be closed after context
        # (can't easily test this without mocking, but at least verify it doesn't crash)
