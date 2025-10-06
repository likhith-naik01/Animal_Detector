import json
from typing import Any, Callable

def get_cache():
    """Dummy cache function - returns None since we're not using Redis"""
    return None

def cached_json(key: str, ttl: int, loader: Callable[[], Any]) -> Any:
    """
    Cache JSON data - simplified version without Redis
    Just calls the loader function directly (no actual caching)
    For production, you'd use Redis for proper caching
    """
    # Simply call the loader and return data without caching
    return loader()

def invalidate_pattern(pattern: str):
    """Invalidate cache pattern - no-op without Redis"""
    pass

def publish_message(channel: str, message: dict):
    """Publish message - no-op without Redis"""
    pass