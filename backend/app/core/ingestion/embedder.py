"""
Qonfido RAG - Embedder
=======================
Generate embeddings using sentence-transformers.
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class Embedder:
    """
    Embedding generator using sentence-transformers.
    
    Default model: BAAI/bge-m3 (1024 dimensions)
    Fallback: all-MiniLM-L6-v2 (384 dimensions)
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str | None = None,
        batch_size: int = 32,
    ):
        """
        Initialize the embedder.
        
        Args:
            model_name: HuggingFace model name
            device: Device to use ('cpu', 'cuda', or None for auto)
            batch_size: Batch size for embedding
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._device = device
        self._dimension = None

    @property
    def model(self):
        """Lazy load the model."""
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self):
        """Load the embedding model."""
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
            _ = self.model  # Trigger model loading
        return self._dimension

    def embed_texts(
        self,
        texts: list[str],
        show_progress: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress bar
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])

        logger.info(f"Embedding {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        
        logger.info(f"Generated embeddings: {embeddings.shape}")
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding


# =============================================================================
# Global Instance
# =============================================================================

_embedder: Embedder | None = None


def get_embedder(model_name: str = "BAAI/bge-m3") -> Embedder:
    """Get or create the default embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = Embedder(model_name=model_name)
    return _embedder
