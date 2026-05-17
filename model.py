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

# Initialize tokenizer and model (lazy loading)
_tokenizer = None
_model = None


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
        quant_config = BitsAndBytesConfig(load_in_8bit=True)
        _model = Mistral3ForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            quantization_config=FineGrainedFP8Config(dequantize=True)
        )
    return _model


def generate_response(messages: List[Dict[str, str]], max_new_tokens: int = 512, temperature: float = 0.7) -> str:
    """
    Generate a response from the model given a list of messages.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        max_new_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature
    
    Returns:
        Generated response text
    """
    tokenizer = get_tokenizer()
    model = get_model()
    
    # Format messages for Mistral chat template
    # Mistral expects: <s> [INST] user_message [/INST] assistant_message </s>
    # For multi-turn, it continues with the pattern
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(text, return_tensors='pt').to('cuda')
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Remove the input text from the response
    # Find where the actual response starts
    if text in response:
        response = response.replace(text, "")
    
    return response.strip()


def generate_response_dry_run(messages: List[Dict[str, str]], **kwargs) -> str:
    """
    Generate a dry run response without loading the actual model.
    Useful for debugging and testing without GPU/model requirements.
    """
    user_message = messages[-1]['content'] if messages else ""
    return f"[DRY RUN] Mock response to: {user_message[:100]}..." if len(user_message) > 100 else f"[DRY RUN] Mock response to: {user_message}"


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
