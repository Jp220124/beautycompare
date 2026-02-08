import hashlib
import logging
from cachetools import TTLCache

from app.config import get_settings
from app.models.schemas import SearchResponse

logger = logging.getLogger(__name__)
settings = get_settings()

# Global in-memory cache
_cache: TTLCache = TTLCache(
    maxsize=settings.cache_max_size,
    ttl=settings.cache_ttl_seconds,
)

# Stats
_stats = {"hits": 0, "misses": 0}


def _make_key(query: str) -> str:
    """Create a normalized cache key from a search query."""
    normalized = query.lower().strip()
    return hashlib.md5(normalized.encode()).hexdigest()


def get_cached(query: str) -> SearchResponse | None:
    """Retrieve cached search results if available."""
    key = _make_key(query)
    result = _cache.get(key)
    if result is not None:
        _stats["hits"] += 1
        logger.debug(f"Cache HIT for query: {query}")
        return result
    _stats["misses"] += 1
    logger.debug(f"Cache MISS for query: {query}")
    return None


def set_cached(query: str, response: SearchResponse) -> None:
    """Store search results in cache."""
    key = _make_key(query)
    _cache[key] = response
    logger.debug(f"Cached results for query: {query}")


def get_cache_stats() -> dict:
    """Return cache statistics."""
    total = _stats["hits"] + _stats["misses"]
    hit_rate = (_stats["hits"] / total * 100) if total > 0 else 0
    return {
        "size": len(_cache),
        "max_size": _cache.maxsize,
        "ttl_seconds": int(_cache.ttl),
        "hits": _stats["hits"],
        "misses": _stats["misses"],
        "hit_rate_percent": round(hit_rate, 1),
    }


def clear_cache() -> None:
    """Clear all cached entries."""
    _cache.clear()
    _stats["hits"] = 0
    _stats["misses"] = 0
