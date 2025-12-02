"""
Common utility functions used across the application.
"""

import hashlib
import re
from typing import Any


def generate_id(text: str, prefix: str = "") -> str:
    hash_val = hashlib.md5(text.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_val}" if prefix else hash_val


def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Remove extra whitespace   
    text = re.sub(r"\s+", " ", text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    
    return text[: max_length - len(suffix)] + suffix


def safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    
    try:
        # Handle percentage strings like "12.5%"
        if isinstance(value, str):
            value = value.replace("%", "").replace(",", "").strip()
        return float(value)
    except (ValueError, TypeError):
        return default


def format_percentage(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_currency(value: float | None, currency: str = "₹", decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{currency}{value:,.{decimals}f}"
