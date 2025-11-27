"""
Simple in-memory cache module to avoid circular imports
"""
from datetime import datetime, timedelta

# Simple in-memory cache with TTL
_cache = {}
_cache_time = {}

def cached_query(key: str, query_func, ttl_seconds: int = 300):
    """
    Simple cache with TTL.
    Args:
        key: Cache key
        query_func: Function to call if cache miss
        ttl_seconds: Time to live in seconds
    """
    now = datetime.now()
    
    if key in _cache:
        if now - _cache_time[key] < timedelta(seconds=ttl_seconds):
            return _cache[key]
    
    result = query_func()
    _cache[key] = result
    _cache_time[key] = now
    return result
