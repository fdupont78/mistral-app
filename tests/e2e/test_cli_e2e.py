"""
End-to-end tests for CLI functionality.
Tests the complete workflow from user input to database storage.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.database import DatabaseManager
from src.core.conversation import Conversation


@pytest.mark.e2e
class TestCLIE2E:
    """End-to-end tests for CLI functionality."""
    
    def test_conversation_listing_workflow(self, temp_db):
        """Test listing conversations workflow."""
        # Create some conversations
        temp_db.create_conversation("Test 1")
        temp_db.create_conversation("Test 2")
        
        # List them
        conversations = temp_db.list_conversations()
        
        # Verify we have our conversations
        assert len(conversations) >= 2
        titles = [c[1] for c in conversations]
        assert "Test 1" in titles
        assert "Test 2" in titles
    
    def test_conversation_load_workflow(self, temp_db):
        """Test loading a conversation workflow."""
        # Create a conversation with messages
        conv_id = temp_db.create_conversation("Load Test")
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv_id, "user", "Hello", timestamp)
            )
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conv_id)
            )
        
        # Load it
        conv = Conversation.load(conv_id, db_manager=temp_db)
        
        assert conv is not None
        assert conv.title == "Load Test"
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"
    
    def test_conversation_not_found(self, temp_db):
        """Test loading a non-existent conversation."""
        with pytest.raises(ValueError) as exc_info:
            Conversation.load(99999, db_manager=temp_db)
        
        assert "not found" in str(exc_info.value)


@pytest.mark.e2e
class TestDatabasePersistence:
    """Test database persistence across sessions."""
    
    @pytest.fixture
    def persistent_db(self):
        """Create a database file that persists for the test."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # First session - create data
        manager1 = DatabaseManager(db_path=db_path)
        conv_id = manager1.create_conversation("Persistent Test")
        with manager1.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = "2024-01-01T12:00:00"
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conv_id, "user", "Test message", timestamp)
            )
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conv_id)
            )
        
        yield db_path, conv_id
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_persistence_across_managers(self, persistent_db):
        """Test that data persists across different DatabaseManager instances."""
        db_path, conv_id = persistent_db
        
        # Create a new manager with the same path
        manager2 = DatabaseManager(db_path=db_path)
        
        # Verify data is still there
        conv = manager2.get_conversation(conv_id)
        assert conv is not None
        assert conv[1] == "Persistent Test"
        
        messages = manager2.get_messages(conv_id)
        assert len(messages) == 1
        assert messages[0][3] == "Test message"
    
    def test_conversation_listing(self, temp_db):
        """Test that conversations are listed correctly."""
        # Create conversations with different timestamps
        conv1 = temp_db.create_conversation("First")
        conv2 = temp_db.create_conversation("Second")
        conv3 = temp_db.create_conversation("Third")
        
        # List all
        conversations = temp_db.list_conversations()
        
        assert len(conversations) >= 3
        ids = [c[0] for c in conversations]
        assert conv1 in ids
        assert conv2 in ids
        assert conv3 in ids


@pytest.mark.e2e
class TestSearchFunctionality:
    """Test search functionality."""
    
    def test_search_by_title(self, temp_db):
        """Test searching conversations by title."""
        # Create conversations with different titles
        temp_db.create_conversation("Test Search")
        temp_db.create_conversation("Another Conversation")
        temp_db.create_conversation("Search Test")
        temp_db.create_conversation("Unrelated")
        
        # Search for "Test"
        results = temp_db.search_conversations("Test")
        
        assert len(results) >= 2
        for conv in results:
            assert "Test" in conv[1]
    
    def test_search_no_results(self, temp_db):
        """Test search with no results."""
        temp_db.create_conversation("Test")
        
        results = temp_db.search_conversations("NonExistent")
        assert len(results) == 0
    
    def test_search_case_insensitive(self, temp_db):
        """Test that search is case-insensitive."""
        temp_db.create_conversation("TEST Case")
        
        results_lower = temp_db.search_conversations("test")
        results_upper = temp_db.search_conversations("TEST")
        results_mixed = temp_db.search_conversations("Test")
        
        # All should find the conversation
        assert len(results_lower) >= 1
        assert len(results_upper) >= 1
        assert len(results_mixed) >= 1


@pytest.mark.e2e
class TestFullWorkflow:
    """Test complete application workflows."""
    
    def test_complete_chat_workflow(self, temp_db):
        """Test a complete chat workflow."""
        # 1. Create a conversation
        conv = Conversation.create(title="Workflow Test", db_manager=temp_db)
        conv_id = conv.conversation_id
        
        # 2. Add messages
        conv.add_message("user", "First message")
        conv.add_message("assistant", "First response")
        conv.add_message("user", "Second message")
        
        # 3. Verify in database
        conv_data = temp_db.get_conversation(conv_id)
        assert conv_data[1] == "Workflow Test"
        
        messages = temp_db.get_messages(conv_id)
        assert len(messages) == 3
        
        # 4. Reload conversation
        reloaded = Conversation.load(conv_id, db_manager=temp_db)
        assert len(reloaded.messages) == 3
        assert reloaded.messages[0].content == "First message"
        assert reloaded.messages[1].content == "First response"
        assert reloaded.messages[2].content == "Second message"
        
        # 5. Update title
        reloaded.set_title("Updated Title")
        conv_data = temp_db.get_conversation(conv_id)
        assert conv_data[1] == "Updated Title"
        
        # 6. Get history for model
        history = reloaded.get_history_for_model()
        assert len(history) == 3
        assert history[0] == {"role": "user", "content": "First message"}
        
        # 7. Get last user message
        last_user = reloaded.get_last_user_message()
        assert last_user == "Second message"
        
        # 8. Delete conversation
        reloaded.delete()
        assert temp_db.get_conversation(conv_id) is None
        assert len(temp_db.get_messages(conv_id)) == 0
