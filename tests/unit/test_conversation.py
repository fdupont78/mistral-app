"""
Unit tests for Conversation and Message classes.
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core.conversation import Conversation, Message


@pytest.mark.unit
class TestMessage:
    """Test Message class."""

    def test_message_creation(self, sample_message):
        """Test creating a Message instance."""
        assert sample_message.role == "user"
        assert sample_message.content == "Test message"
        assert sample_message.timestamp == "2024-01-01T12:00:00"
        assert sample_message.message_id == 1

    def test_message_to_dict(self, sample_message):
        """Test converting Message to dictionary."""
        msg_dict = sample_message.to_dict()
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Test message"
        assert msg_dict["timestamp"] == "2024-01-01T12:00:00"
        assert msg_dict["message_id"] == 1

    def test_message_from_tuple(self):
        """Test creating Message from database tuple."""
        msg_tuple = (1, 1, "user", "Hello", "2024-01-01T12:00:00")
        message = Message.from_tuple(msg_tuple)

        assert message.role == "user"
        assert message.content == "Hello"
        assert message.timestamp == "2024-01-01T12:00:00"
        assert message.message_id == 1


@pytest.mark.unit
class TestConversation:
    """Test Conversation class."""

    def test_conversation_creation(self, db_manager):
        """Test creating a new Conversation."""
        conv = Conversation.create(title="Test Conv", db_manager=db_manager)

        assert conv.conversation_id > 0
        assert conv.title == "Test Conv"
        assert len(conv.messages) == 0

    def test_conversation_load(self, db_manager):
        """Test loading a conversation from database."""
        # Create a conversation with messages using direct SQL to avoid locking
        conv_id = db_manager.create_conversation("Load Test")
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv_id, "user", "First message", timestamp),
            )
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv_id, "assistant", "Response", timestamp),
            )

        # Load it
        conv = Conversation.load(conv_id, db_manager=db_manager)

        assert conv.conversation_id == conv_id
        assert conv.title == "Load Test"
        assert len(conv.messages) == 2
        assert conv.messages[0].role == "user"
        assert conv.messages[1].role == "assistant"

    def test_conversation_load_not_found(self, db_manager):
        """Test loading a non-existent conversation."""
        with pytest.raises(ValueError) as exc_info:
            Conversation.load(99999, db_manager=db_manager)

        assert "not found" in str(exc_info.value)

    def test_add_message(self, db_manager):
        """Test adding a message to a conversation."""
        conv = Conversation.create(title="Add Message Test", db_manager=db_manager)

        # Ensure we have a clean state
        with db_manager.get_connection():
            pass

        # Add message through Conversation
        msg = conv.add_message("user", "Test message")

        assert isinstance(msg, Message)
        assert msg.role == "user"
        assert msg.content == "Test message"
        assert msg.message_id > 0

        # Verify in database
        messages = db_manager.get_messages(conv.conversation_id)
        assert len(messages) == 1
        assert messages[0][2] == "user"
        assert messages[0][3] == "Test message"

    def test_set_title(self, db_manager):
        """Test setting conversation title."""
        conv = Conversation.create(title="Original", db_manager=db_manager)
        conv.set_title("Updated")

        assert conv.title == "Updated"

        # Verify in database
        conv_data = db_manager.get_conversation(conv.conversation_id)
        assert conv_data[1] == "Updated"

    def test_delete(self, db_manager):
        """Test deleting a conversation."""
        conv = Conversation.create(title="To Delete", db_manager=db_manager)
        conv_id = conv.conversation_id

        conv.delete()

        assert conv.conversation_id == 0
        assert len(conv.messages) == 0

        # Verify in database
        assert db_manager.get_conversation(conv_id) is None

    def test_get_history_for_model(self, db_manager):
        """Test getting message history formatted for the model."""
        conv = Conversation.create(title="History Test", db_manager=db_manager)

        # Use direct SQL to add messages
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "user", "Question", timestamp),
            )
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "assistant", "Answer", timestamp),
            )

        # Reload to get messages
        conv = Conversation.load(conv.conversation_id, db_manager=db_manager)
        history = conv.get_history_for_model()

        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "Question"}
        assert history[1] == {"role": "assistant", "content": "Answer"}

    def test_get_last_user_message(self, db_manager):
        """Test getting the last user message."""
        conv = Conversation.create(title="Last User Test", db_manager=db_manager)

        # Use direct SQL to add messages
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "user", "First", timestamp),
            )
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "assistant", "Response", timestamp),
            )
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "user", "Second", timestamp),
            )

        # Reload to get messages
        conv = Conversation.load(conv.conversation_id, db_manager=db_manager)
        last_user = conv.get_last_user_message()
        assert last_user == "Second"

    def test_get_last_user_message_none(self, db_manager):
        """Test getting last user message when there are none."""
        conv = Conversation.create(title="No User", db_manager=db_manager)

        # Use direct SQL to add message
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "assistant", "Only assistant", timestamp),
            )

        # Reload to get messages
        conv = Conversation.load(conv.conversation_id, db_manager=db_manager)
        last_user = conv.get_last_user_message()
        assert last_user == ""

    def test_list_all(self, db_manager):
        """Test listing all conversations."""
        # Create some conversations
        conv1 = Conversation.create(title="First", db_manager=db_manager)
        conv2 = Conversation.create(title="Second", db_manager=db_manager)

        conversations = Conversation.list_all(db_manager=db_manager)

        assert len(conversations) >= 2
        ids = [c.conversation_id for c in conversations]
        assert conv1.conversation_id in ids
        assert conv2.conversation_id in ids

    def test_str_representation(self, db_manager):
        """Test string representation of Conversation."""
        conv = Conversation.create(title="Str Test", db_manager=db_manager)

        # Use direct SQL to add message
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "user", "Test", timestamp),
            )

        # Reload to get messages
        conv = Conversation.load(conv.conversation_id, db_manager=db_manager)
        conv_str = str(conv)
        assert "Str Test" in conv_str
        assert "messages=1" in conv_str

    def test_reload(self, db_manager):
        """Test reloading a conversation from database."""
        conv = Conversation.create(title="Reload Test", db_manager=db_manager)

        # Use direct SQL to add message
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv.conversation_id, "user", "Message", timestamp),
            )

        # Modify in-memory state
        conv.title = "Modified In Memory"

        # Reload from database
        reloaded = conv.reload()

        # Title should be reverted to database value
        assert reloaded.title == "Reload Test"
