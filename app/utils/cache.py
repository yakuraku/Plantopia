"""
In-memory caching utility for API responses (100% FREE - no Redis needed!)

This module provides a simple, production-ready caching solution using Python's
cachetools library. Perfect for single-server deployments where you want fast
caching without the overhead of running Redis or Memcached.

Features:
- TTL (Time To Live) support per cache entry
- Automatic eviction of old entries
- Thread-safe with async support
- Cache invalidation patterns
- Performance monitoring

Usage:
    from app.utils.cache import cached

    @cached(ttl=600, prefix="plants")
    async def get_all_plants(self):
        # Expensive database operation
        return data  # Cached for 10 minutes
"""
import json
import hashlib
import time
import logging
from typing import Optional, Any, Callable
from functools import wraps
from cachetools import TTLCache
import asyncio

logger = logging.getLogger(__name__)

# In-memory cache (singleton) - stores data in application memory
_cache_store: Optional[TTLCache] = None
_cache_lock = asyncio.Lock()

# Cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "evictions": 0
}


def get_cache() -> TTLCache:
    """
    Get in-memory cache instance (lazy initialization)

    Returns:
        TTLCache: Shared cache instance with 1000 item capacity
    """
    global _cache_store
    if _cache_store is None:
        # Create cache with max 1000 items
        # TTL is managed per-item in the decorator
        _cache_store = TTLCache(maxsize=1000, ttl=3600)
        logger.info("Initialized in-memory cache with maxsize=1000")
    return _cache_store


def cache_key(*args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        str: MD5 hash of arguments
    """
    # Filter out self/cls from args for class methods
    filtered_args = []
    for arg in args:
        # Skip class instances (self, cls)
        if not hasattr(arg, '__class__') or isinstance(arg, (str, int, float, bool, list, dict)):
            filtered_args.append(arg)

    # Create a deterministic string representation
    try:
        key_data = json.dumps({
            "args": [str(arg) for arg in filtered_args],
            "kwargs": {k: str(v) for k, v in kwargs.items()}
        }, sort_keys=True)
    except Exception:
        # Fallback for non-serializable objects
        key_data = f"{filtered_args}:{kwargs}"

    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300, prefix: str = ""):
    """
    Decorator for caching async function results in memory

    Args:
        ttl: Time to live in seconds (default 5 minutes)
        prefix: Cache key prefix for organization

    Returns:
        Decorated function with caching support

    Example:
        @cached(ttl=600, prefix="plants")
        async def get_all_plants(self):
            # Expensive operation
            return data  # Cached for 10 minutes

    Notes:
        - Cache is cleared on application restart (expected behavior)
        - Works best for single-server deployments
        - For multi-server, each server has its own cache (still beneficial)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            global _cache_stats

            # Generate cache key
            key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            cache = get_cache()
            cached_result = None
            is_valid = False

            async with _cache_lock:
                if key in cache:
                    cached_result, cached_time = cache[key]
                    # Check if still valid
                    if time.time() - cached_time < ttl:
                        is_valid = True
                        _cache_stats["hits"] += 1
                    else:
                        # Expired, remove it
                        del cache[key]
                        _cache_stats["evictions"] += 1
                        logger.debug(f"Cache evicted (expired): {key}")

            if is_valid and cached_result is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_result

            # Cache miss - call function
            _cache_stats["misses"] += 1
            logger.debug(f"Cache miss: {key}")

            result = await func(*args, **kwargs)

            # Store in cache with timestamp
            async with _cache_lock:
                try:
                    cache[key] = (result, time.time())
                    logger.debug(f"Cached result for {ttl}s: {key}")
                except Exception as e:
                    # Cache full or other error - not critical
                    logger.warning(f"Failed to cache result: {e}")

            return result

        # Add cache invalidation method to the function
        wrapper.invalidate_cache = lambda: invalidate_cache(f"{prefix}:{func.__name__}:*")

        # Add cache statistics method
        wrapper.get_stats = lambda: get_cache_stats()

        return wrapper
    return decorator


def invalidate_cache(pattern: str = None):
    """
    Invalidate cache entries matching pattern

    Args:
        pattern: Pattern to match (e.g., "plants:*" for all plant cache)
                 None to clear entire cache

    Example:
        # Clear all plant-related cache
        invalidate_cache("plants:*")

        # Clear everything
        invalidate_cache()
    """
    cache = get_cache()

    if pattern is None:
        # Clear entire cache
        cache.clear()
        logger.info("Cleared entire cache")
        return

    # Remove keys matching pattern
    prefix = pattern.replace("*", "")
    keys_to_delete = [k for k in list(cache.keys()) if k.startswith(prefix)]

    for key in keys_to_delete:
        cache.pop(key, None)

    if keys_to_delete:
        logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching: {pattern}")


def get_cache_stats() -> dict:
    """
    Get cache performance statistics

    Returns:
        dict: Statistics including hits, misses, size, hit rate

    Example:
        stats = get_cache_stats()
        print(f"Hit rate: {stats['hit_rate']:.2%}")
    """
    global _cache_stats
    cache = get_cache()

    total_requests = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = _cache_stats["hits"] / total_requests if total_requests > 0 else 0

    return {
        "size": len(cache),
        "max_size": cache.maxsize,
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "evictions": _cache_stats["evictions"],
        "hit_rate": hit_rate,
        "total_requests": total_requests
    }


def reset_cache_stats():
    """Reset cache statistics (useful for testing)"""
    global _cache_stats
    _cache_stats = {
        "hits": 0,
        "misses": 0,
        "evictions": 0
    }
    logger.info("Reset cache statistics")


# Optional: Cache warming function
async def warm_cache(func_list: list):
    """
    Pre-populate cache with commonly accessed data

    Args:
        func_list: List of (function, args, kwargs) tuples to pre-cache

    Example:
        await warm_cache([
            (get_all_plants, (), {}),
            (get_plant_by_id, (1,), {})
        ])
    """
    logger.info(f"Warming cache with {len(func_list)} entries...")

    for func, args, kwargs in func_list:
        try:
            await func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to warm cache for {func.__name__}: {e}")

    logger.info("Cache warming complete")
