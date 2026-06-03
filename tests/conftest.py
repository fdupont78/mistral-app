"""
Pytest configuration and fixtures for Mistral App tests.
"""

import os
import sys
import tempfile

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.conversation import Conversation, Message
from src.core.database import DatabaseManager
from src.core.model import GenerationParams, ModelManager


@pytest.fixture
def db_manager():
    """Create a DatabaseManager with a temporary database.
    
    This fixture creates a fresh database for each test function,
    ensuring test isolation. The database is automatically cleaned up after the test.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    manager = DatabaseManager(db_path=db_path)
    yield manager
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing (E2E tests).
    
    Alias for db_manager for backward compatibility.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    manager = DatabaseManager(db_path=db_path)
    yield manager

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path for testing.
    
    Use this when you need just the path, not the manager.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_conversation(db_manager):
    """Create a sample conversation for testing.
    
    Creates a conversation with two messages (user and assistant) for use in tests.
    Uses the db_manager fixture to ensure proper cleanup.
    """
    conv = Conversation.create(title="Test Conversation", db_manager=db_manager)
    conv.add_message("user", "Hello, how are you?")
    conv.add_message("assistant", "I'm doing well, thank you!")
    return conv


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        role="user", content="Test message", timestamp="2024-01-01T12:00:00", message_id=1
    )


@pytest.fixture
def gen_params():
    """Create default generation parameters for testing."""
    return GenerationParams()


@pytest.fixture(autouse=True)
def cleanup_model_manager():
    """Reset the global model manager before and after each test.
    
    This ensures tests don't interfere with each other by resetting
    the singleton ModelManager instance.
    """
    import src.core.model as model_module
    import src.core.database as database_module

    # Reset before test
    model_module._model_manager = None
    database_module._db_manager = None
    
    yield
    
    # Reset after test
    model_module._model_manager = None
    database_module._db_manager = None


@pytest.fixture
def mock_model_manager(mocker):
    """Create a mocked ModelManager for testing without actual model loading."""
    manager = mocker.MagicMock(spec=ModelManager)
    manager.is_loaded.return_value = False
    manager.is_loading.return_value = False
    manager.get_status.return_value = "Not loaded"
    manager.generate_response.return_value = "Mock response"
    manager.generate_response_dry_run.return_value = "[DRY RUN] Mock response"
    return manager


# Add useful marks for categorizing tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "e2e: marks end-to-end tests")
    config.addinivalue_line("markers", "unit: marks unit tests")
    config.addinivalue_line("markers", "integration: marks integration tests")


# Pytest hooks for performance optimization
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add timing information to test reports."""
    outcome = yield
    rep = outcome.get_result()
    
    # Set test duration
    if hasattr(rep, "duration"):
        setattr(rep, "duration", rep.duration)
