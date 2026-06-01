"""
Conversation module for managing chat conversations.
Provides Conversation and Message classes for state management.
"""

from dataclasses import dataclass, field
from typing import Any

from .database import DatabaseManager, get_database_manager


@dataclass
class Message:
    """Represents a single message in a conversation."""

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = ""
    message_id: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
        }

    @classmethod
    def from_tuple(cls, msg_tuple: tuple) -> "Message":
        """
        Create a Message from a database tuple.

        Args:
            msg_tuple: Tuple from database (id, conversation_id, role, content, timestamp)

        Returns:
            Message: A new Message instance.
        """
        msg_id, conv_id, role, content, timestamp = msg_tuple
        return cls(role=role, content=content, timestamp=timestamp, message_id=msg_id)


@dataclass
class Conversation:
    """
    Represents a chat conversation with message history.

    Manages conversation state, message history, and database persistence.
    """

    conversation_id: int = 0
    title: str = "New Chat"
    created_at: str = ""
    updated_at: str = ""
    messages: list[Message] = field(default_factory=list)
    _db_manager: DatabaseManager | None = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize the database manager if not provided."""
        if self._db_manager is None:
            self._db_manager = get_database_manager()
        if self.conversation_id == 0:
            # New conversation - will be saved on first message
            pass

    @classmethod
    def create(
        cls, title: str = "New Chat", db_manager: DatabaseManager | None = None
    ) -> "Conversation":
        """
        Create a new conversation in the database.

        Args:
            title: Title for the new conversation.
            db_manager: Optional DatabaseManager instance.

        Returns:
            Conversation: A new Conversation instance.
        """
        manager = db_manager or get_database_manager()
        conversation_id = manager.create_conversation(title)
        return cls(conversation_id=conversation_id, title=title, _db_manager=manager)

    @classmethod
    def load(
        cls, conversation_id: int, db_manager: DatabaseManager | None = None
    ) -> "Conversation":
        """
        Load a conversation from the database.

        Args:
            conversation_id: ID of the conversation to load.
            db_manager: Optional DatabaseManager instance.

        Returns:
            Conversation: The loaded Conversation instance.

        Raises:
            ValueError: If conversation is not found.
        """
        manager = db_manager or get_database_manager()
        conv_data = manager.get_conversation(conversation_id)
        if not conv_data:
            raise ValueError(f"Conversation {conversation_id} not found")

        conv_id, title, created_at, updated_at = conv_data
        messages_data = manager.get_messages(conv_id)

        message_objects = [Message.from_tuple(msg) for msg in messages_data]

        return cls(
            conversation_id=conv_id,
            title=title,
            created_at=created_at,
            updated_at=updated_at,
            messages=message_objects,
            _db_manager=manager,
        )

    def add_message(self, role: str, content: str) -> Message:
        """
        Add a message to the conversation and save to database.

        Args:
            role: Role of the message ('user' or 'assistant').
            content: Content of the message.

        Returns:
            Message: The newly created Message instance.
        """
        if self.conversation_id == 0:
            # This is a new unsaved conversation, save it first
            self.conversation_id = self._db_manager.create_conversation(self.title)

        message_id = self._db_manager.add_message(self.conversation_id, role, content)
        message = Message(role=role, content=content, message_id=message_id)
        self.messages.append(message)
        return message

    def set_title(self, title: str):
        """
        Update the conversation title.

        Args:
            title: New title for the conversation.
        """
        self.title = title
        if self.conversation_id > 0:
            self._db_manager.update_conversation_title(self.conversation_id, title)

    def delete(self):
        """Delete the conversation from the database."""
        if self.conversation_id > 0:
            self._db_manager.delete_conversation(self.conversation_id)
            self.conversation_id = 0
            self.messages = []

    def get_history_for_model(self) -> list[dict[str, str]]:
        """
        Get message history formatted for the LLM.

        Returns:
            List[Dict[str, str]]: List of message dictionaries with 'role' and 'content'.
        """
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def get_last_user_message(self) -> str:
        """
        Get the content of the last user message.

        Returns:
            str: Content of the last user message, or empty string if none found.
        """
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return ""

    @staticmethod
    def list_all(db_manager: DatabaseManager | None = None) -> list["Conversation"]:
        """
        List all conversations from the database.

        Args:
            db_manager: Optional DatabaseManager instance.

        Returns:
            List[Conversation]: List of all Conversation instances (without messages).
        """
        manager = db_manager or get_database_manager()
        conversations = []
        conv_data_list = manager.list_conversations()
        for conv_data in conv_data_list:
            conv_id, title, created_at, updated_at = conv_data
            conversations.append(
                Conversation(
                    conversation_id=conv_id,
                    title=title,
                    created_at=created_at,
                    updated_at=updated_at,
                    _db_manager=manager,
                )
            )
        return conversations

    def reload(self) -> "Conversation":
        """
        Reload the conversation from the database.

        Returns:
            Conversation: A fresh instance loaded from the database.
        """
        if self.conversation_id > 0:
            return Conversation.load(self.conversation_id, self._db_manager)
        return self

    def __str__(self) -> str:
        return f"Conversation(id={self.conversation_id}, title='{self.title}', messages={len(self.messages)})"

    def __repr__(self) -> str:
        return f"Conversation(id={self.conversation_id}, title='{self.title}', messages={len(self.messages)})"
