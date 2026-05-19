"""
Integration tests for Mistral App.
Tests interactions between database, conversation, and model components.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.database import DatabaseManager
from src.core.conversation import Conversation, Message
from src.core.model import GenerationParams


@pytest.mark.integration
class TestDatabaseConversationIntegration:
    """Test integration between DatabaseManager and Conversation."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager with temporary database."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        manager = DatabaseManager(db_path=db_path)
        yield manager
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_conversation_uses_database_manager(self, db_manager):
        """Test that Conversation properly uses DatabaseManager."""
        # Create conversation
        conv = Conversation.create(title="Integration Test", db_manager=db_manager)
        
        # Verify it was created in database
        conv_data = db_manager.get_conversation(conv.conversation_id)
        assert conv_data is not None
        assert conv_data[1] == "Integration Test"
    
    def test_conversation_message_persistence(self, db_manager):
        """Test that Conversation messages are persisted to database."""
        conv = Conversation.create(title="Message Test", db_manager=db_manager)
        
        # Add messages through Conversation
        conv.add_message("user", "User message")
        conv.add_message("assistant", "Assistant response")
        
        # Verify in database
        messages = db_manager.get_messages(conv.conversation_id)
        assert len(messages) == 2
        assert messages[0][2] == "user"
        assert messages[0][3] == "User message"
        assert messages[1][2] == "assistant"
        assert messages[1][3] == "Assistant response"
    
    def test_conversation_delete_removes_from_db(self, db_manager):
        """Test that deleting a Conversation removes it from database."""
        conv = Conversation.create(title="To Delete", db_manager=db_manager)
        conv_id = conv.conversation_id
        
        # Verify it exists
        assert db_manager.get_conversation(conv_id) is not None
        
        # Delete through Conversation
        conv.delete()
        
        # Verify it's gone from database
        assert db_manager.get_conversation(conv_id) is None
    
    def test_conversation_title_update_persistence(self, db_manager):
        """Test that updating Conversation title persists to database."""
        conv = Conversation.create(title="Original", db_manager=db_manager)
        conv_id = conv.conversation_id
        
        # Update title
        conv.set_title("Updated")
        
        # Verify in database
        conv_data = db_manager.get_conversation(conv_id)
        assert conv_data[1] == "Updated"
    
    def test_conversation_list_all_from_db(self, db_manager):
        """Test that Conversation.list_all retrieves from database."""
        # Create conversations directly in database
        conv1_id = db_manager.create_conversation("DB Conv 1")
        conv2_id = db_manager.create_conversation("DB Conv 2")
        
        # Also create through Conversation class
        conv3 = Conversation.create(title="Conversation Conv", db_manager=db_manager)
        
        # List all
        conversations = Conversation.list_all(db_manager=db_manager)
        
        # Should have all three
        assert len(conversations) >= 3
        ids = [c.conversation_id for c in conversations]
        assert conv1_id in ids
        assert conv2_id in ids
        assert conv3.conversation_id in ids


@pytest.mark.integration
class TestConversationMessageIntegration:
    """Test integration between Conversation and Message."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager with temporary database."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        manager = DatabaseManager(db_path=db_path)
        yield manager
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_message_from_tuple_in_conversation(self, db_manager):
        """Test that Message.from_tuple works with database tuples."""
        # Create a conversation with messages
        conv_id = db_manager.create_conversation("Test")
        db_manager.add_message(conv_id, "user", "Test message")
        
        # Get messages as tuples
        msg_tuples = db_manager.get_messages(conv_id)
        
        # Convert to Message objects
        messages = [Message.from_tuple(t) for t in msg_tuples]
        
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Test message"
    
    def test_conversation_get_history_for_model(self, db_manager):
        """Test that Conversation.get_history_for_model returns correct format."""
        conv = Conversation.create(title="History Test", db_manager=db_manager)
        conv.add_message("user", "Question")
        conv.add_message("assistant", "Answer")
        
        history = conv.get_history_for_model()
        
        # Should be list of dicts with role and content
        assert isinstance(history, list)
        assert len(history) == 2
        assert all(isinstance(h, dict) for h in history)
        assert all('role' in h and 'content' in h for h in history)
        
        # Check content
        assert history[0]['role'] == 'user'
        assert history[0]['content'] == 'Question'
        assert history[1]['role'] == 'assistant'
        assert history[1]['content'] == 'Answer'


@pytest.mark.integration
class TestGenerationParamsIntegration:
    """Test integration of GenerationParams with other components."""
    
    def test_gen_params_to_dict_for_model(self):
        """Test that GenerationParams.to_dict provides correct format for model."""
        params = GenerationParams(
            max_new_tokens=256,
            temperature=0.5,
            do_sample=False
        )
        
        params_dict = params.to_dict()
        
        # Should have all expected keys
        expected_keys = [
            'max_new_tokens', 'temperature', 'do_sample', 'top_k',
            'top_p', 'repetition_penalty', 'num_return_sequences'
        ]
        for key in expected_keys:
            assert key in params_dict
        
        # Check values
        assert params_dict['max_new_tokens'] == 256
        assert params_dict['temperature'] == 0.5
        assert params_dict['do_sample'] is False


@pytest.mark.integration
class TestDatabaseManagerContextManager:
    """Test DatabaseManager context manager functionality."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager with temporary database."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        manager = DatabaseManager(db_path=db_path)
        yield manager
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_transaction_rollback_on_error(self, db_manager):
        """Test that transactions are rolled back on error."""
        import sqlite3
        
        # Manually execute a transaction that will fail
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
                               ("Test", "now", "now"))
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify the insert was rolled back
        conversations = db_manager.list_conversations()
        assert not any(c[1] == "Test" for c in conversations)
    
    def test_transaction_commit_on_success(self, db_manager):
        """Test that transactions are committed on success."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
                           ("Committed", "now", "now"))
        
        # Verify the insert was committed
        conversations = db_manager.list_conversations()
        assert any(c[1] == "Committed" for c in conversations)
