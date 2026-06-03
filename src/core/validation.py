"""
Validation module for user input sanitization and validation.
Provides functions to validate and sanitize user input before processing.
"""

import re
from typing import Any


def sanitize_user_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize and validate user input.

    Args:
        text: The input text to sanitize.
        max_length: Maximum allowed length for the input.

    Returns:
        str: The sanitized text.

    Raises:
        ValueError: If input is invalid or too long.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    if not text.strip():
        raise ValueError("Input cannot be empty or whitespace only")

    if len(text) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")

    # Remove control characters (except newline, tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    return text.strip()


def validate_conversation_title(title: str, max_length: int = 200) -> str:
    """
    Validate and sanitize a conversation title.

    Args:
        title: The title to validate.
        max_length: Maximum allowed length for the title.

    Returns:
        str: The validated and sanitized title.

    Raises:
        ValueError: If title is invalid.
    """
    if not isinstance(title, str):
        raise ValueError("Title must be a string")

    if not title.strip():
        return "New Chat"  # Default title for empty input

    if len(title) > max_length:
        raise ValueError(f"Title too long (max {max_length} characters)")

    # Remove control characters
    title = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", title)

    return title.strip()


def validate_message_role(role: str) -> str:
    """
    Validate a message role.

    Args:
        role: The role to validate (e.g., 'user', 'assistant').

    Returns:
        str: The validated role.

    Raises:
        ValueError: If role is invalid.
    """
    valid_roles = {"user", "assistant", "system"}

    if not isinstance(role, str):
        raise ValueError("Role must be a string")

    role = role.lower().strip()

    if role not in valid_roles:
        raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")

    return role


def validate_generation_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Validate generation parameters.

    Args:
        params: Dictionary of generation parameters.

    Returns:
        dict: The validated parameters.

    Raises:
        ValueError: If any parameter is invalid.
    """
    validated = {}

    if "max_new_tokens" in params:
        max_tokens = params["max_new_tokens"]
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValueError("max_new_tokens must be a positive integer")
        if max_tokens > 4096:
            raise ValueError("max_new_tokens cannot exceed 4096")
        validated["max_new_tokens"] = max_tokens

    if "temperature" in params:
        temp = params["temperature"]
        if not isinstance(temp, (int, float)) or temp < 0:
            raise ValueError("temperature must be a non-negative number")
        if temp > 2.0:
            raise ValueError("temperature cannot exceed 2.0")
        validated["temperature"] = float(temp)

    if "do_sample" in params:
        do_sample = params["do_sample"]
        if not isinstance(do_sample, bool):
            raise ValueError("do_sample must be a boolean")
        validated["do_sample"] = do_sample

    if "top_k" in params:
        top_k = params["top_k"]
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        validated["top_k"] = top_k

    if "top_p" in params:
        top_p = params["top_p"]
        if not isinstance(top_p, (int, float)) or not (0 <= top_p <= 1):
            raise ValueError("top_p must be a number between 0 and 1")
        validated["top_p"] = float(top_p)

    if "repetition_penalty" in params:
        rep_pen = params["repetition_penalty"]
        if not isinstance(rep_pen, (int, float)) or rep_pen < 0:
            raise ValueError("repetition_penalty must be a non-negative number")
        validated["repetition_penalty"] = float(rep_pen)

    if "num_return_sequences" in params:
        num_seq = params["num_return_sequences"]
        if not isinstance(num_seq, int) or num_seq <= 0:
            raise ValueError("num_return_sequences must be a positive integer")
        if num_seq > 5:
            raise ValueError("num_return_sequences cannot exceed 5")
        validated["num_return_sequences"] = num_seq

    return validated
