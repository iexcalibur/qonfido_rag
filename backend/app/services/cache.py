"""
Qonfido RAG - Cache Service
============================
Caching service for embeddings and query results.
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with value and metadata."""
    value: Any
    created_at: float
    ttl: float  # Time to live in seconds


class InMemoryCache:
    """
    Simple in-memory cache.
    
    For production, replace with Redis.
    """

    def __init__(self, default_ttl: float = 3600):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self._cache: dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry.created_at + entry.ttl

    def get(self, key: str) -> Any | None:
        """
        Get value from cache.
        
        Returns None if not found or expired.
        """
        entry = self._cache.get(key)
        if entry is None:
            return None
        
        if self._is_expired(entry):
            del self._cache[key]
            return None
        
        return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache."""
        self._cache[key] = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl=ttl or self.default_ttl,
        )

    def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if key existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
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
        return len(self._cache)


class EmbeddingCache:
    """
    Specialized cache for embeddings.
    
    Uses text hash as key to avoid recomputing embeddings.
    """

    def __init__(self, cache: InMemoryCache | None = None):
        self._cache = cache or InMemoryCache(default_ttl=86400)  # 24 hours

    def _hash_text(self, text: str) -> str:
        """Generate hash for text."""
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
        """
        Get cached embeddings for batch of texts.
        
        Returns:
            Tuple of (embeddings_or_none, indices_of_uncached)
        """
        results = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            embedding = self.get_embedding(text)
            results.append(embedding)
            if embedding is None:
                uncached_indices.append(i)
        
        return results, uncached_indices


class QueryCache:
    """
    Cache for query results.
    
    Caches full query responses to avoid repeated processing.
    """

    def __init__(self, cache: InMemoryCache | None = None):
        self._cache = cache or InMemoryCache(default_ttl=300)  # 5 minutes

    def _make_key(
        self,
        query: str,
        search_mode: str,
        top_k: int,
        source_filter: str | None,
    ) -> str:
        """Generate cache key from query parameters."""
        key_parts = [query, search_mode, str(top_k), source_filter or ""]
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
        return self._cache.get(key)

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


# =============================================================================
# Global Instances
# =============================================================================

_cache: InMemoryCache | None = None
_embedding_cache: EmbeddingCache | None = None
_query_cache: QueryCache | None = None


def get_cache() -> InMemoryCache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache


def get_embedding_cache() -> EmbeddingCache:
    """Get or create the global embedding cache instance."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache(get_cache())
    return _embedding_cache


def get_query_cache() -> QueryCache:
    """Get or create the global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache(get_cache())
    return _query_cache
