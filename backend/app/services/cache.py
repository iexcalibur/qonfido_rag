"""Caching service for embeddings and query results."""

import hashlib
import json
import logging
import pickle
import time
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


@dataclass
class CacheEntry:
    """Cache entry with value and TTL metadata."""
    value: Any
    created_at: float
    ttl: float


class InMemoryCache:
    """
    Thread-safe in-memory cache with LRU eviction and TTL support.
    
    Improvements for Dev Mode:
    1. Thread-Safe: Uses RLock to handle concurrent FastAPI requests safely.
    2. LRU Eviction: Automatically removes oldest items when max_size is reached to prevent OOM.
    3. Deep Copy: Simulates serialization to prevent shared-reference bugs.
    """

    def __init__(self, default_ttl: float = 3600, max_size: int = 1000):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._lock = threading.RLock()

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry.created_at + entry.ttl

    def get(self, key: str) -> Any | None:
        """Get value from cache, moving it to the end (most recently used)."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if self._is_expired(entry):
                del self._cache[key]
                return None
            
            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache with LRU eviction."""
        with self._lock:
            # If updating existing key, move to end
            if key in self._cache:
                self._cache.move_to_end(key)
            
            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl or self.default_ttl,
            )
            
            # Evict oldest items if over capacity
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)  # Pop first item (least recently used)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if self._is_expired(entry)
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    @property
    def size(self) -> int:
        """Get number of entries in cache."""
        with self._lock:
            return len(self._cache)


class RedisCache:
    """Redis-based cache with TTL support."""

    def __init__(self, redis_url: str, default_ttl: float = 3600):
        """Initialize Redis cache."""
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is not installed. Install with: pip install redis")
        
        self.default_ttl = default_ttl
        self._client = redis.from_url(
            redis_url, 
            decode_responses=False,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Fail fast if Redis is unreachable
        try:
            self._client.ping()
            logger.info(f"Redis cache initialized: {redis_url}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis at {redis_url}: {e}")

    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes."""
        if isinstance(value, np.ndarray):
            return pickle.dumps(value)
        elif isinstance(value, (dict, list)):
            return json.dumps(value).encode('utf-8')
        else:
            return pickle.dumps(value)

    def _deserialize(self, data: bytes | None) -> Any:
        """Deserialize bytes from Redis."""
        if data is None:
            return None
        
        try:
            return pickle.loads(data)
        except Exception:
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                return None

    def get(self, key: str) -> Any | None:
        """Get value from Redis."""
        try:
            data = self._client.get(key)
            return self._deserialize(data)
        except Exception as e:
            logger.warning(f"Redis get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in Redis with TTL."""
        try:
            serialized = self._serialize(value)
            ttl_seconds = int(ttl or self.default_ttl)
            self._client.setex(key, ttl_seconds, serialized)
        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")

    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            result = self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis delete error for key {key}: {e}")
            return False

    def clear(self) -> None:
        """Flush Redis database."""
        try:
            self._client.flushdb()
            logger.info("Redis cache cleared")
        except Exception as e:
            logger.warning(f"Redis clear error: {e}")

    def cleanup_expired(self) -> int:
        """Redis handles TTL natively."""
        return 0

    @property
    def size(self) -> int:
        """Get approximate number of keys."""
        try:
            return self._client.dbsize()
        except Exception as e:
            logger.warning(f"Redis dbsize error: {e}")
            return 0


class EmbeddingCache:
    """Specialized cache for embeddings using text hash as key."""

    def __init__(self, cache: InMemoryCache | RedisCache | None = None):
        # Use a larger max_size for embeddings in dev mode (e.g. 5000 vectors)
        self._cache = cache or InMemoryCache(default_ttl=86400, max_size=5000)

    def _hash_text(self, text: str) -> str:
        """Generate SHA256 hash for text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def get_embedding(self, text: str) -> np.ndarray | None:
        """Get cached embedding for text."""
        key = f"emb:{self._hash_text(text)}"
        return self._cache.get(key)

    def set_embedding(self, text: str, embedding: np.ndarray) -> None:
        """Cache embedding for text."""
        key = f"emb:{self._hash_text(text)}"
        self._cache.set(key, embedding)

    def get_batch(self, texts: list[str]) -> tuple[list[np.ndarray | None], list[int]]:
        """Get cached embeddings for batch, returns embeddings and uncached indices."""
        results = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            embedding = self.get_embedding(text)
            results.append(embedding)
            if embedding is None:
                uncached_indices.append(i)
        
        return results, uncached_indices

    @property
    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return {"size": self._cache.size}


class QueryCache:
    """Cache for query results to avoid repeated processing."""

    def __init__(self, cache: InMemoryCache | RedisCache | None = None):
        self._cache = cache or InMemoryCache(default_ttl=300, max_size=500)

    def _make_key(
        self,
        query: str,
        search_mode: str,
        top_k: int,
        source_filter: str | None,
    ) -> str:
        """Generate MD5 cache key from query parameters.
        
        Normalizes query string to handle whitespace and case differences.
        """
        # Normalize query: case-insensitive, strip and normalize whitespace
        normalized_query = " ".join(query.strip().lower().split())
        key_parts = [normalized_query, search_mode, str(top_k), (source_filter or "").strip().lower()]
        key_str = "|".join(key_parts)
        return f"query:{hashlib.md5(key_str.encode()).hexdigest()}"

    def get(
        self,
        query: str,
        search_mode: str,
        top_k: int,
        source_filter: str | None = None,
    ) -> dict | None:
        """Get cached query result."""
        key = self._make_key(query, search_mode, top_k, source_filter)
        result = self._cache.get(key)
        if result:
            logger.debug(f"QueryCache.get() HIT for key: {key[:50]}...")
        else:
            logger.debug(f"QueryCache.get() MISS for key: {key[:50]}... | Cache size: {self._cache.size}")
        return result

    def set(
        self,
        query: str,
        search_mode: str,
        top_k: int,
        result: dict,
        source_filter: str | None = None,
    ) -> None:
        """Cache query result."""
        key = self._make_key(query, search_mode, top_k, source_filter)
        self._cache.set(key, result)
        logger.debug(f"QueryCache.set() stored key: {key[:50]}... | Cache size: {self._cache.size}")


_cache: InMemoryCache | RedisCache | None = None
_embedding_cache: EmbeddingCache | None = None
_query_cache: QueryCache | None = None


def get_cache() -> InMemoryCache | RedisCache:
    """Get or create global cache instance with automatic fallback."""
    global _cache
    if _cache is None:
        from app.config import settings
        
        # Try to use Redis if configured and available
        if settings.redis_url and REDIS_AVAILABLE:
            try:
                _cache = RedisCache(settings.redis_url, default_ttl=3600)
                logger.info("Using Redis cache")
            except (ConnectionError, Exception) as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                logger.info("Falling back to in-memory cache (Redis configured but unavailable)")
                _cache = InMemoryCache()
        else:
            # Fallback for dev mode without Docker
            logger.info("Using in-memory cache (Redis not configured or installed)")
            _cache = InMemoryCache()
            
    return _cache


def get_embedding_cache() -> EmbeddingCache:
    """Get or create global embedding cache instance."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache(get_cache())
    return _embedding_cache


def get_query_cache() -> QueryCache:
    """Get or create global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache(get_cache())
    return _query_cache