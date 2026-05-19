"""
Unit tests for ModelManager class and GenerationParams.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.model import ModelManager, GenerationParams, DEFAULT_GEN_PARAMS, GEN_PARAM_DESCRIPTIONS


@pytest.mark.unit
class TestGenerationParams:
    """Test GenerationParams dataclass."""
    
    def test_default_values(self, gen_params):
        """Test default generation parameters."""
        assert gen_params.max_new_tokens == 512
        assert gen_params.temperature == 0.7
        assert gen_params.do_sample is True
        assert gen_params.top_k == 50
        assert gen_params.top_p == 0.92
        assert gen_params.repetition_penalty == 1.0
        assert gen_params.num_return_sequences == 1
    
    def test_to_dict(self, gen_params):
        """Test converting GenerationParams to dictionary."""
        params_dict = gen_params.to_dict()
        
        assert params_dict['max_new_tokens'] == 512
        assert params_dict['temperature'] == 0.7
        assert params_dict['do_sample'] is True
        assert params_dict['top_k'] == 50
        assert params_dict['top_p'] == 0.92
        assert params_dict['repetition_penalty'] == 1.0
        assert params_dict['num_return_sequences'] == 1
    
    def test_from_dict(self):
        """Test creating GenerationParams from dictionary."""
        params_dict = {
            'max_new_tokens': 256,
            'temperature': 0.5,
            'do_sample': False,
            'top_k': 25,
            'top_p': 0.8,
            'repetition_penalty': 1.2,
            'num_return_sequences': 2
        }
        
        gen_params = GenerationParams.from_dict(params_dict)
        
        assert gen_params.max_new_tokens == 256
        assert gen_params.temperature == 0.5
        assert gen_params.do_sample is False
        assert gen_params.top_k == 25
        assert gen_params.top_p == 0.8
        assert gen_params.repetition_penalty == 1.2
        assert gen_params.num_return_sequences == 2
    
    def test_from_dict_partial(self):
        """Test creating GenerationParams from partial dictionary."""
        params_dict = {
            'max_new_tokens': 128,
            'temperature': 0.9
        }
        
        gen_params = GenerationParams.from_dict(params_dict)
        
        assert gen_params.max_new_tokens == 128
        assert gen_params.temperature == 0.9
        # Others should have defaults
        assert gen_params.top_k == 50


@pytest.mark.unit
class TestModelManager:
    """Test ModelManager class."""
    
    def test_init(self, mocker):
        """Test ModelManager initialization."""
        # Mock the imports to avoid loading actual models
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        assert manager.model_name == '/workspace/Ministral-3-3B-Instruct-2512'
        assert manager.default_quant_method == 'fp8'
        assert manager._model is None
        assert manager._tokenizer is None
    
    def test_is_loaded(self, mocker):
        """Test is_loaded method."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        assert manager.is_loaded() is False
        
        manager._model = "mock_model"
        assert manager.is_loaded() is True
    
    def test_is_loading(self, mocker):
        """Test is_loading method."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        assert manager.is_loading() is False
        
        manager._model_loading = True
        assert manager.is_loading() is True
    
    def test_get_status(self, mocker):
        """Test get_status method."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        assert manager.get_status() == "Not loaded"
        
        manager._model_loading = True
        assert manager.get_status() == "Loading..."
        
        manager._model_loading = False
        manager._model_loaded = True
        assert manager.get_status() == "Loaded ✓"
    
    def test_generate_response_dry_run(self, mocker):
        """Test generate_response_dry_run method."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        messages = [{"role": "user", "content": "Test message"}]
        response = manager.generate_response_dry_run(messages)
        
        assert "[DRY RUN]" in response
        assert "Test message" in response
    
    def test_generate_response_dry_run_with_params(self, mocker):
        """Test generate_response_dry_run with parameters."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        messages = [{"role": "user", "content": "Test"}]
        response = manager.generate_response_dry_run(
            messages,
            max_new_tokens=100,
            temperature=0.5
        )
        
        # The response should contain the dry run indicator and parameters
        assert "DRY RUN" in response
        assert "max_new_tokens=100" in response
        assert "temperature=0.5" in response
    
    def test_chat_completion(self, mocker):
        """Test chat_completion method."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        manager = ModelManager()
        
        messages = [{"role": "user", "content": "Test"}]
        
        # Mock generate_response to avoid actual model call
        manager.generate_response = lambda *args, **kwargs: "Mock response"
        
        result = manager.chat_completion(messages)
        
        assert result["role"] == "assistant"
        assert result["content"] == "Mock response"


@pytest.mark.unit
class TestDefaultGenParams:
    """Test DEFAULT_GEN_PARAMS constant."""
    
    def test_default_gen_params_is_instance(self):
        """Test that DEFAULT_GEN_PARAMS is a GenerationParams instance."""
        assert isinstance(DEFAULT_GEN_PARAMS, GenerationParams)
    
    def test_gen_param_descriptions_exist(self):
        """Test that GEN_PARAM_DESCRIPTIONS has all required keys."""
        params = DEFAULT_GEN_PARAMS.to_dict()
        for param in params.keys():
            assert param in GEN_PARAM_DESCRIPTIONS


@pytest.mark.unit
class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_get_model_manager(self, mocker):
        """Test get_model_manager function."""
        mocker.patch('src.core.model.AutoTokenizer')
        mocker.patch('src.core.model.Mistral3ForConditionalGeneration')
        
        from src.core.model import get_model_manager
        
        manager = get_model_manager()
        assert isinstance(manager, ModelManager)
        
        # Should return the same instance
        manager2 = get_model_manager()
        assert manager is manager2
