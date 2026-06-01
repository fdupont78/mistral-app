"""
Model module for loading and managing Mistral models.
Provides model loading, response generation, and configuration management.
"""

from dataclasses import dataclass
from typing import Any

import torch
from transformers import (
    AutoTokenizer,
    BitsAndBytesConfig,
    FineGrainedFP8Config,
    Mistral3ForConditionalGeneration,
)

# Model configuration
MODEL_NAME = "/workspace/Ministral-3-3B-Instruct-2512"

# Quantization options
QUANTIZATION_METHODS = {
    "none": None,
    "8bit": BitsAndBytesConfig(load_in_8bit=True),
    "4bit": BitsAndBytesConfig(load_in_4bit=True),
    "fp8": FineGrainedFP8Config(dequantize=True),
}

# Quantization descriptions for UI
QUANTIZATION_DESCRIPTIONS = {
    "none": "No quantization (full precision, ~15GB VRAM for 3B)",
    "8bit": "8-bit quantization (~6-8GB VRAM)",
    "4bit": "4-bit quantization (~3-4GB VRAM)",
    "fp8": "FP8 quantization (NVIDIA GPUs, ~4GB VRAM)",
}


@dataclass
class GenerationParams:
    """Container for generation parameters."""

    max_new_tokens: int = 512
    temperature: float = 0.7
    do_sample: bool = True
    top_k: int = 50
    top_p: float = 0.92
    repetition_penalty: float = 1.0
    num_return_sequences: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "do_sample": self.do_sample,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
            "num_return_sequences": self.num_return_sequences,
        }

    @classmethod
    def from_dict(cls, params: dict[str, Any]) -> "GenerationParams":
        """Create from dictionary."""
        return cls(**{k: v for k, v in params.items() if k in cls.__dataclass_fields__})


# Default generation parameters for Mistral-3
DEFAULT_GEN_PARAMS = GenerationParams()

# Parameter descriptions for UI
GEN_PARAM_DESCRIPTIONS = {
    "max_new_tokens": "Maximum new tokens to generate (higher = longer responses)",
    "temperature": "Randomness: 0.0=deterministic, 1.0+ = more creative/random",
    "do_sample": "Enable sampling (False = greedy/argmax decoding)",
    "top_k": "Keep only top-k highest probability tokens for sampling",
    "top_p": "Nucleus sampling: keep tokens with cumulative probability > p",
    "repetition_penalty": "Penalty for repeated tokens (1.0=no penalty, >1.0=discourage repetition)",
    "num_return_sequences": "Number of response sequences to generate",
}


class ModelManager:
    """
    Manages model loading and response generation.

    Provides lazy loading of tokenizer and model, with support for
    different quantization methods and model configurations.
    """

    def __init__(self, model_name: str | None = None, quant_method: str = "fp8"):
        """
        Initialize the ModelManager.

        Args:
            model_name: Hugging Face model path. Defaults to MODEL_NAME.
            quant_method: Default quantization method ('none', '8bit', '4bit', 'fp8').
        """
        self.model_name = model_name or MODEL_NAME
        self.default_quant_method = quant_method
        self._tokenizer: Any | None = None
        self._model: Any | None = None
        self._model_loading: bool = False
        self._model_loaded: bool = False

    def get_tokenizer(self) -> Any:
        """
        Get or initialize the tokenizer.

        Returns:
            The loaded tokenizer.
        """
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return self._tokenizer

    def get_model(self) -> Any:
        """
        Get or initialize the model.

        Returns:
            The loaded model.
        """
        if self._model is None:
            quant_config = QUANTIZATION_METHODS.get(self.default_quant_method)
            self._model = Mistral3ForConditionalGeneration.from_pretrained(
                self.model_name, device_map="auto", quantization_config=quant_config
            )
        return self._model

    def load_model(self, quant_method: str = None, model_name: str = None) -> tuple[Any, Any]:
        """
        Load the model with specified quantization method.

        Args:
            quant_method: Quantization method ('none', '8bit', '4bit', 'fp8').
                         If None, uses default.
            model_name: Model name/path. If None, uses default.

        Returns:
            Tuple of (model, tokenizer)
        """
        load_name = model_name or self.model_name
        load_quant = quant_method or self.default_quant_method

        self._model_loading = True
        self._model_loaded = False

        # Load tokenizer first
        self._tokenizer = AutoTokenizer.from_pretrained(load_name)

        # Get quantization config
        quant_config = QUANTIZATION_METHODS.get(load_quant)

        # Load model
        self._model = Mistral3ForConditionalGeneration.from_pretrained(
            load_name, device_map="auto", quantization_config=quant_config
        )

        self._model_loading = False
        self._model_loaded = True

        return self._model, self._tokenizer

    def unload_model(self):
        """Unload the model and tokenizer to free memory."""
        self._model = None
        self._tokenizer = None
        self._model_loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def is_loaded(self) -> bool:
        """
        Check if model is loaded.

        Returns:
            bool: True if model is loaded.
        """
        return self._model is not None

    def is_loading(self) -> bool:
        """
        Check if model is currently loading.

        Returns:
            bool: True if model is loading.
        """
        return self._model_loading

    def get_status(self) -> str:
        """
        Get model loading status as string.

        Returns:
            str: Status message.
        """
        if self._model_loading:
            return "Loading..."
        elif self._model_loaded:
            return "Loaded ✓"
        else:
            return "Not loaded"

    def generate_response(
        self,
        messages: list[dict[str, str]],
        max_new_tokens: int = None,
        temperature: float = None,
        do_sample: bool = None,
        top_k: int = None,
        top_p: float = None,
        repetition_penalty: float = None,
        num_return_sequences: int = None,
        **kwargs,
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
            str: Generated response text
        """
        tokenizer = self.get_tokenizer()
        model = self.get_model()

        # Use defaults if not specified
        if max_new_tokens is None:
            max_new_tokens = DEFAULT_GEN_PARAMS.max_new_tokens
        if temperature is None:
            temperature = DEFAULT_GEN_PARAMS.temperature
        if do_sample is None:
            do_sample = DEFAULT_GEN_PARAMS.do_sample
        if top_k is None:
            top_k = DEFAULT_GEN_PARAMS.top_k
        if top_p is None:
            top_p = DEFAULT_GEN_PARAMS.top_p
        if repetition_penalty is None:
            repetition_penalty = DEFAULT_GEN_PARAMS.repetition_penalty
        if num_return_sequences is None:
            num_return_sequences = DEFAULT_GEN_PARAMS.num_return_sequences

        # Format messages for Mistral chat template
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        inputs = tokenizer(text, return_tensors="pt").to("cuda")
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
            **kwargs,
        )

        # Only decode the newly generated tokens (skip input tokens)
        # For multiple sequences, just take the first one
        response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)

        return response.strip()

    def generate_response_dry_run(self, messages: list[dict[str, str]], **kwargs) -> str:
        """
        Generate a dry run response without loading the actual model.
        Useful for debugging and testing without GPU/model requirements.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional parameters to include in the mock response

        Returns:
            str: Mock response string
        """
        user_message = messages[-1]["content"] if messages else ""

        # Build parameter string
        params_str = ""
        for k, v in kwargs.items():
            if k != "messages" and v is not None:
                params_str += f" {k}={v}"

        if len(user_message) > 100:
            msg = f"[DRY RUN{params_str}] Mock response to: {user_message[:100]}..."
        else:
            msg = f"[DRY RUN{params_str}] Mock response to: {user_message}"

        return msg

    def chat_completion(self, messages: list[dict[str, str]], **kwargs) -> dict[str, str]:
        """
        Generate a chat completion response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Generation parameters

        Returns:
            dict: Response with 'role' and 'content' keys
        """
        response = self.generate_response(messages, **kwargs)
        return {"role": "assistant", "content": response}


# Global instance for backward compatibility
_model_manager = None


def get_model_manager() -> ModelManager:
    """
    Get the global ModelManager instance.

    Returns:
        ModelManager: The global model manager instance.
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


# Backward compatibility functions (deprecated, use ModelManager directly)
def get_tokenizer():
    """Get tokenizer (backward compatibility)."""
    return get_model_manager().get_tokenizer()


def get_model():
    """Get model (backward compatibility)."""
    return get_model_manager().get_model()


def load_model(quant_method: str = "fp8", model_name: str = None):
    """Load model (backward compatibility)."""
    return get_model_manager().load_model(quant_method, model_name)


def is_model_loaded():
    """Check if model is loaded (backward compatibility)."""
    return get_model_manager().is_loaded()


def is_model_loading():
    """Check if model is loading (backward compatibility)."""
    return get_model_manager().is_loading()


def get_model_status():
    """Get model status (backward compatibility)."""
    return get_model_manager().get_status()


def generate_response(messages: list[dict[str, str]], **kwargs) -> str:
    """Generate response (backward compatibility)."""
    return get_model_manager().generate_response(messages, **kwargs)


def generate_response_dry_run(messages: list[dict[str, str]], **kwargs) -> str:
    """Generate dry run response (backward compatibility)."""
    return get_model_manager().generate_response_dry_run(messages, **kwargs)


def chat_completion(messages: list[dict[str, str]], **kwargs) -> dict[str, str]:
    """Chat completion (backward compatibility)."""
    return get_model_manager().chat_completion(messages, **kwargs)
