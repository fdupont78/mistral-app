from dataclasses import dataclass, field
from typing import List, Dict, Any
from database import (
    create_conversation, add_message, get_conversation, get_messages,
    update_conversation_title, delete_conversation, list_conversations
)


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = ""
    message_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }


@dataclass
class Conversation:
    """Represents a chat conversation with message history."""
    conversation_id: int = 0
    title: str = "New Chat"
    created_at: str = ""
    updated_at: str = ""
    messages: List[Message] = field(default_factory=list)

    def __post_init__(self):
        if self.conversation_id == 0:
            # New conversation - will be saved on first message
            pass

    @classmethod
    def create(cls, title: str = "New Chat") -> 'Conversation':
        """Create a new conversation in the database."""
        conversation_id = create_conversation(title)
        return cls(conversation_id=conversation_id, title=title)

    @classmethod
    def load(cls, conversation_id: int) -> 'Conversation':
        """Load a conversation from the database."""
        conv_data = get_conversation(conversation_id)
        if not conv_data:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conv_id, title, created_at, updated_at = conv_data
        messages = get_messages(conv_id)
        
        message_objects = []
        for msg in messages:
            msg_id, conv_id, role, content, timestamp = msg
            message_objects.append(Message(
                role=role,
                content=content,
                timestamp=timestamp,
                message_id=msg_id
            ))
        
        return cls(
            conversation_id=conv_id,
            title=title,
            created_at=created_at,
            updated_at=updated_at,
            messages=message_objects
        )

    def add_message(self, role: str, content: str) -> Message:
        """Add a message to the conversation and save to database."""
        if self.conversation_id == 0:
            # This is a new unsaved conversation, save it first
            self.conversation_id = create_conversation(self.title)
        
        message_id = add_message(self.conversation_id, role, content)
        message = Message(
            role=role,
            content=content,
            message_id=message_id
        )
        self.messages.append(message)
        return message

    def set_title(self, title: str):
        """Update the conversation title."""
        self.title = title
        if self.conversation_id > 0:
            update_conversation_title(self.conversation_id, title)

    def delete(self):
        """Delete the conversation from the database."""
        if self.conversation_id > 0:
            delete_conversation(self.conversation_id)
            self.conversation_id = 0

    def get_history_for_model(self) -> List[Dict[str, str]]:
        """Get message history formatted for the LLM."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def get_last_user_message(self) -> str:
        """Get the content of the last user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return ""

    @staticmethod
    def list_all() -> List['Conversation']:
        """List all conversations from the database."""
        conversations = []
        conv_data_list = list_conversations()
        for conv_data in conv_data_list:
            conv_id, title, created_at, updated_at = conv_data
            conversations.append(Conversation(
                conversation_id=conv_id,
                title=title,
                created_at=created_at,
                updated_at=updated_at
            ))
        return conversations

    def __str__(self) -> str:
        return f"Conversation(id={self.conversation_id}, title='{self.title}', messages={len(self.messages)})"
