"""
Utility functions for the sample project.

This module contains various helper functions and utilities
used throughout the application.
"""

import re
import hashlib
import logging
from typing import Any, Callable, TypeVar, List, Dict
from functools import wraps
from datetime import datetime, timedelta

# Type variable for generic functions
T = TypeVar('T')

# Configure logging
logger = logging.getLogger(__name__)


def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure function execution time.
    
    Args:
        func: Function to be timed
        
    Returns:
        Wrapped function that logs execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {duration:.4f} seconds")
    
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between attempts in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay} seconds..."
                        )
                        import time
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_string(value: Any, min_length: int = 1, max_length: int = 255) -> str:
    """Validate and clean string input.
    
    Args:
        value: Value to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Cleaned string value
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"Expected string, got {type(value).__name__}")
    
    cleaned = value.strip()
    
    if len(cleaned) < min_length:
        raise ValidationError(f"String too short: minimum {min_length} characters")
    
    if len(cleaned) > max_length:
        raise ValidationError(f"String too long: maximum {max_length} characters")
    
    return cleaned


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with salt.
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
        
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        import secrets
        salt = secrets.token_hex(16)
    
    # Combine password and salt
    salted_password = password + salt
    
    # Hash using SHA-256
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hash
        salt: Salt used for hashing
        
    Returns:
        True if password matches, False otherwise
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hashed_password


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        sanitized = name[:max_name_length] + ('.' + ext if ext else '')
    
    return sanitized


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
        
    Raises:
        ValueError: If chunk_size is less than 1
    """
    if chunk_size < 1:
        raise ValueError("Chunk size must be at least 1")
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


class CacheManager:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache manager.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set a cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        expiry_time = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expiry_time
        }
    
    def get(self, key: str) -> Any:
        """Get a cache value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        if datetime.now() > entry['expires_at']:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """Delete a cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed, False otherwise
        """
        return self.cache.pop(key, None) is not None
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


# Global cache instance
cache = CacheManager()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix 