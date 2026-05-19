"""
Mistral model loading and inference utilities.
Reuses the configuration from request.py
"""
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from transformers import Mistral3ForConditionalGeneration, FineGrainedFP8Config
from typing import List, Dict, Optional

# Model configuration (reuse from request.py)
MODEL_NAME = '/workspace/Ministral-3-3B-Instruct-2512'

# Quantization options
QUANTIZATION_METHODS = {
    'none': None,
    '8bit': BitsAndBytesConfig(load_in_8bit=True),
    '4bit': BitsAndBytesConfig(load_in_4bit=True),
    'fp8': FineGrainedFP8Config(dequantize=True),
}

# Initialize tokenizer and model (lazy loading)
_tokenizer = None
_model = None
_model_loading = False
_model_loaded = False


def get_tokenizer():
    """Get or initialize the tokenizer."""
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return _tokenizer


def get_model():
    """Get or initialize the model."""
    global _model
    if _model is None:
        quant_config = QUANTIZATION_METHODS.get('fp8')  # Default to FP8
        _model = Mistral3ForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            quantization_config=quant_config
        )
    return _model


def load_model(quant_method: str = 'fp8', model_name: str = None):
    """
    Load the model with specified quantization method.
    
    Args:
        quant_method: Quantization method ('none', '8bit', '4bit', 'fp8')
        model_name: Model name/path (defaults to MODEL_NAME)
    
    Returns:
        Tuple of (model, tokenizer)
    """
    global _model, _tokenizer, _model_loading, _model_loaded
    
    _model_loading = True
    _model_loaded = False
    
    load_name = model_name or MODEL_NAME
    
    # Load tokenizer first
    _tokenizer = AutoTokenizer.from_pretrained(load_name)
    
    # Get quantization config
    quant_config = QUANTIZATION_METHODS.get(quant_method)
    
    # Load model
    _model = Mistral3ForConditionalGeneration.from_pretrained(
        load_name,
        device_map="auto",
        quantization_config=quant_config
    )
    
    _model_loading = False
    _model_loaded = True
    
    return _model, _tokenizer


def is_model_loaded():
    """Check if model is loaded."""
    return _model is not None


def is_model_loading():
    """Check if model is currently loading."""
    global _model_loading
    return _model_loading


def get_model_status():
    """Get model loading status as string."""
    if _model_loading:
        return "Loading..."
    elif _model_loaded:
        return "Loaded ✓"
    else:
        return "Not loaded"


# Default generation parameters for Mistral-3
DEFAULT_GEN_PARAMS = {
    'max_new_tokens': 512,
    'temperature': 0.7,
    'do_sample': True,
    'top_k': 50,
    'top_p': 0.92,
    'repetition_penalty': 1.0,
    'num_return_sequences': 1,
}

# Parameter descriptions for UI
GEN_PARAM_DESCRIPTIONS = {
    'max_new_tokens': 'Maximum new tokens to generate (higher = longer responses)',
    'temperature': 'Randomness: 0.0=deterministic, 1.0+ = more creative/random',
    'do_sample': 'Enable sampling (False = greedy/argmax decoding)',
    'top_k': 'Keep only top-k highest probability tokens for sampling',
    'top_p': 'Nucleus sampling: keep tokens with cumulative probability > p',
    'repetition_penalty': 'Penalty for repeated tokens (1.0=no penalty, >1.0=discourage repetition)',
    'num_return_sequences': 'Number of response sequences to generate',
}


def generate_response(
    messages: List[Dict[str, str]],
    max_new_tokens: int = DEFAULT_GEN_PARAMS['max_new_tokens'],
    temperature: float = DEFAULT_GEN_PARAMS['temperature'],
    do_sample: bool = DEFAULT_GEN_PARAMS['do_sample'],
    top_k: int = DEFAULT_GEN_PARAMS['top_k'],
    top_p: float = DEFAULT_GEN_PARAMS['top_p'],
    repetition_penalty: float = DEFAULT_GEN_PARAMS['repetition_penalty'],
    num_return_sequences: int = DEFAULT_GEN_PARAMS['num_return_sequences'],
    **kwargs
) -> str:
    """
    Generate a response from the model given a list of messages.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        max_new_tokens: Maximum number of new tokens to generate
        temperature: Sampling temperature (0.0-2.0+)
        do_sample: Whether to sample from distribution (vs greedy)
        top_k: Number of top tokens to consider for sampling
        top_p: Nucleus sampling probability threshold (0.0-1.0)
        repetition_penalty: Penalty for repeated tokens
        num_return_sequences: Number of sequences to generate
    
    Returns:
        Generated response text
    """
    tokenizer = get_tokenizer()
    model = get_model()
    
    # Format messages for Mistral chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(text, return_tensors='pt').to('cuda')
    input_length = inputs.input_ids.shape[1]
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=do_sample,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        num_return_sequences=num_return_sequences,
        pad_token_id=tokenizer.eos_token_id,
        **kwargs
    )
    
    # Only decode the newly generated tokens (skip input tokens)
    # For multiple sequences, just take the first one
    response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    
    return response.strip()


def generate_response_dry_run(messages: List[Dict[str, str]], **kwargs) -> str:
    """
    Generate a dry run response without loading the actual model.
    Useful for debugging and testing without GPU/model requirements.
    Accepts same parameters as generate_response for API consistency.
    """
    user_message = messages[-1]['content'] if messages else ""
    params_str = ""
    for k, v in kwargs.items():
        if k != 'messages' and v is not None:
            params_str += f" {k}={v}"
    msg = f"[DRY RUN{params_str}] Mock response to: {user_message[:100]}..." if len(user_message) > 100 else f"[DRY RUN{params_str}] Mock response to: {user_message}"
    return msg


def chat_completion(messages: List[Dict[str, str]], **kwargs) -> Dict[str, str]:
    """
    Generate a chat completion response.
    
    Returns a dict with 'role' and 'content' keys.
    """
    response = generate_response(messages, **kwargs)
    return {
        "role": "assistant",
        "content": response
    }
