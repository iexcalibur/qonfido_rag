"""Generate embeddings using sentence-transformers with caching support."""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class Embedder:
    """Embedding generator using sentence-transformers with caching and batch processing."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str | None = None,
        batch_size: int = 32,
        use_cache: bool = True,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.use_cache = use_cache
        self._model = None
        self._device = device
        self._dimension = None
        self._cache = None
        
        if use_cache:
            try:
                from app.services.cache import get_embedding_cache
                self._cache = get_embedding_cache()
                logger.info("Embedding cache enabled")
            except Exception as e:
                logger.warning(f"Could not initialize embedding cache: {e}")
                self._cache = None

    @property
    def model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self):
        """Load embedding model with fallback to all-MiniLM-L6-v2 on failure."""
        logger.info(f"Loading embedding model: {self.model_name}")
        try:
            from sentence_transformers import SentenceTransformer
            
            self._model = SentenceTransformer(
                self.model_name,
                device=self._device,
            )
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Dimension: {self._dimension}")
            
        except Exception as e:
            logger.warning(f"Failed to load {self.model_name}: {e}")
            logger.info("Falling back to all-MiniLM-L6-v2")
            
            from sentence_transformers import SentenceTransformer
            
            self.model_name = "all-MiniLM-L6-v2"
            self._model = SentenceTransformer(
                self.model_name,
                device=self._device,
            )
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Fallback model loaded. Dimension: {self._dimension}")

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            _ = self.model
        return self._dimension

    def embed_texts(
        self,
        texts: list[str],
        show_progress: bool = True,
    ) -> np.ndarray:
        """Generate embeddings for list of texts with caching support."""
        if not texts:
            return np.array([])

        if self._cache and self.use_cache:
            cached_results, uncached_indices = self._cache.get_batch(texts)
            
            if not uncached_indices:
                logger.info(f"Cache hit: All {len(texts)} embeddings from cache")
                return np.array(cached_results)
            
            cache_hits = len(texts) - len(uncached_indices)
            if cache_hits > 0:
                logger.info(f"Cache: {cache_hits}/{len(texts)} hits, computing {len(uncached_indices)} new")
            
            uncached_texts = [texts[i] for i in uncached_indices]
            new_embeddings = self._embed_batch(uncached_texts, show_progress)
            
            for idx, embedding in zip(uncached_indices, new_embeddings):
                self._cache.set_embedding(texts[idx], embedding)
            
            result = []
            new_idx = 0
            for i, cached in enumerate(cached_results):
                if cached is not None:
                    result.append(cached)
                else:
                    result.append(new_embeddings[new_idx])
                    new_idx += 1
            
            return np.array(result)
        
        logger.info(f"Embedding {len(texts)} texts (no cache)...")
        return self._embed_batch(texts, show_progress)

    def _embed_batch(self, texts: list[str], show_progress: bool = True) -> np.ndarray:
        """Embed batch of texts using the model."""
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for single query with caching."""
        if self._cache and self.use_cache:
            cached = self._cache.get_embedding(query)
            if cached is not None:
                logger.debug("Query embedding cache hit")
                return cached
        
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        
        if self._cache and self.use_cache:
            self._cache.set_embedding(query, embedding)
        
        return embedding
    
    @property
    def cache_stats(self) -> dict:
        """Get cache statistics."""
        if self._cache:
            return {
                "enabled": True,
                "size": self._cache._cache.size,
            }
        return {"enabled": False, "size": 0}


_embedder: Embedder | None = None


def get_embedder(model_name: str = "BAAI/bge-m3", use_cache: bool = True) -> Embedder:
    """Get or create global embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=model_name, use_cache=use_cache)
    return _embedder