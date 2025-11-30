"""Rerank search results using Cohere Rerank API."""

import logging
import os
from dataclasses import dataclass
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RerankedResult:
    """Reranked search result with original and rerank scores."""
    
    id: str
    text: str
    original_score: float
    rerank_score: float
    original_rank: int
    new_rank: int
    metadata: dict[str, Any]
    source: str


class Reranker:
    """Rerank search results using Cohere Rerank API for improved accuracy."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "rerank-english-v3.0",
    ):
        self.model = model
        self._client = None
        try:
            settings_key = settings.cohere_api_key.get_secret_value() if settings.cohere_api_key else None
        except Exception:
            settings_key = None
        
        self._api_key = (
            api_key 
            or settings_key
            or os.getenv("COHERE_API_KEY")
        )

    @property
    def client(self):
        """Lazy load Cohere client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("Cohere API key not provided")
            
            try:
                import cohere
                self._client = cohere.Client(self._api_key)
                logger.info("Cohere client initialized")
            except ImportError:
                logger.error("Cohere not installed. Run: pip install cohere")
                raise
                
        return self._client

    def rerank(
        self,
        query: str,
        results: list,
        top_k: int = 3,
    ) -> list[RerankedResult]:
        """Rerank search results using Cohere API."""
        if not results:
            return []

        documents = [r.text for r in results]
        
        try:
            response = self.client.rerank(
                model=self.model,
                query=query,
                documents=documents,
                top_n=min(top_k, len(documents)),
                return_documents=False,
            )
            
            reranked = []
            for new_rank, item in enumerate(response.results, 1):
                original_idx = item.index
                original_result = results[original_idx]
                
                reranked.append(
                    RerankedResult(
                        id=original_result.id,
                        text=original_result.text,
                        original_score=original_result.score,
                        rerank_score=item.relevance_score,
                        original_rank=original_idx + 1,
                        new_rank=new_rank,
                        metadata=original_result.metadata,
                        source=original_result.source,
                    )
                )
            
            return reranked
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return [
                RerankedResult(
                    id=r.id,
                    text=r.text,
                    original_score=r.score,
                    rerank_score=r.score,
                    original_rank=i + 1,
                    new_rank=i + 1,
                    metadata=r.metadata,
                    source=r.source,
                )
                for i, r in enumerate(results[:top_k])
            ]


class MockReranker:
    """Mock reranker for testing without API calls."""

    def rerank(
        self,
        query: str,
        results: list,
        top_k: int = 3,
    ) -> list[RerankedResult]:
        """Mock rerank returning top results unchanged."""
        return [
            RerankedResult(
                id=r.id,
                text=r.text,
                original_score=r.score,
                rerank_score=r.score * 0.95,
                original_rank=i + 1,
                new_rank=i + 1,
                metadata=r.metadata,
                source=r.source,
            )
            for i, r in enumerate(results[:top_k])
        ]


_reranker = None


def get_reranker(use_mock: bool = False, **kwargs):
    """Get or create global reranker instance."""
    global _reranker
    
    if use_mock:
        return MockReranker()
    
    if _reranker is None:
        _reranker = Reranker(**kwargs)
    return _reranker
