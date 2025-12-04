"""Clear all caches"""
from cache import _cache, _cache_time

_cache.clear()
_cache_time.clear()
print("✅ Cache cleared successfully!")
