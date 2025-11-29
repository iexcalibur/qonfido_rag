"""
Qonfido RAG - Vector Store Service
===================================
Service wrapper for vector store operations.
"""

import logging
from typing import Any

import numpy as np

from app.core.retrieval.semantic import SemanticSearcher, SemanticSearchResult

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service for vector store operations.
    
    Wraps the semantic searcher with additional functionality:
    - Connection management
    - Health checks
    - Batch operations
    """

    def __init__(
        self,
        collection_name: str = "qonfido_funds",
        persist_dir: str | None = None,
    ):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self._searcher = SemanticSearcher(
            collection_name=collection_name,
            persist_dir=persist_dir,
        )

    def index_documents(
        self,
        documents: list[dict[str, Any]],
        embeddings: np.ndarray,
    ) -> int:
        """
        Index documents with embeddings.
        
        Returns:
            Number of documents indexed
        """
        self._searcher.index_documents(documents, embeddings)
        return len(documents)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[SemanticSearchResult]:
        """Search for similar documents."""
        return self._searcher.search(
            query_embedding=query_embedding,
            top_k=top_k,
            source_filter=source_filter,
        )

    def get_document_count(self) -> int:
        """Get number of indexed documents."""
        return self._searcher.document_count

    def clear(self) -> None:
        """Clear all documents from the store."""
        self._searcher.clear()

    def health_check(self) -> dict[str, Any]:
        """Check vector store health."""
        try:
            count = self.get_document_count()
            return {
                "status": "healthy",
                "collection": self.collection_name,
                "document_count": count,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# =============================================================================
# Global Instance
# =============================================================================

_vector_store_service: VectorStoreService | None = None


def get_vector_store_service(**kwargs) -> VectorStoreService:
    """Get or create the global vector store service instance."""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService(**kwargs)
    return _vector_store_service
