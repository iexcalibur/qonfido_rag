"""Hybrid search combining lexical and semantic retrieval using RRF."""

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.core.retrieval.lexical import LexicalSearcher, get_lexical_searcher
from app.core.retrieval.semantic import SemanticSearcher, get_semantic_searcher

logger = logging.getLogger(__name__)


@dataclass
class HybridSearchResult:
    """Hybrid search result with combined scores from lexical and semantic searches."""
    
    id: str
    text: str
    score: float
    lexical_score: float | None
    semantic_score: float | None
    lexical_rank: int | None
    semantic_rank: int | None
    metadata: dict[str, Any]
    source: str


class HybridSearcher:
    """Hybrid search using Reciprocal Rank Fusion (RRF) with parallel retrieval."""

    def __init__(
        self,
        lexical_searcher: LexicalSearcher | None = None,
        semantic_searcher: SemanticSearcher | None = None,
        rrf_k: int = 60,
        use_parallel: bool = True,
    ):
        self.lexical_searcher = lexical_searcher or get_lexical_searcher()
        self.semantic_searcher = semantic_searcher or get_semantic_searcher()
        self.rrf_k = rrf_k
        self.use_parallel = use_parallel
        self._executor = ThreadPoolExecutor(max_workers=2) if use_parallel else None

    def search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = 5,
        source_filter: str | None = None,
        alpha: float = 0.5,
    ) -> list[HybridSearchResult]:
        """Perform hybrid search using RRF fusion of lexical and semantic results."""
        fetch_k = top_k * 3

        if self.use_parallel and self._executor:
            lexical_results, semantic_results = self._parallel_search(
                query, query_embedding, fetch_k, source_filter
            )
        else:
            lexical_results = self.lexical_searcher.search(
                query=query,
                top_k=fetch_k,
                source_filter=source_filter,
            )
            semantic_results = self.semantic_searcher.search(
                query_embedding=query_embedding,
                top_k=fetch_k,
                source_filter=source_filter,
            )

        lexical_map = {}
        for rank, result in enumerate(lexical_results, 1):
            lexical_map[result.id] = (rank, result)

        semantic_map = {}
        for rank, result in enumerate(semantic_results, 1):
            semantic_map[result.id] = (rank, result)

        all_ids = set(lexical_map.keys()) | set(semantic_map.keys())

        scored_results = []
        
        for doc_id in all_ids:
            lexical_rank = None
            lexical_score = None
            semantic_rank = None
            semantic_score = None
            text = ""
            metadata = {}
            source = "unknown"

            if doc_id in lexical_map:
                lexical_rank, lex_result = lexical_map[doc_id]
                lexical_score = lex_result.score
                text = lex_result.text
                metadata = lex_result.metadata
                source = lex_result.source

            if doc_id in semantic_map:
                semantic_rank, sem_result = semantic_map[doc_id]
                semantic_score = sem_result.score
                if not text:
                    text = sem_result.text
                    metadata = sem_result.metadata
                    source = sem_result.source

            rrf_score = 0.0
            
            if lexical_rank is not None:
                rrf_score += (1 - alpha) * (1 / (self.rrf_k + lexical_rank))
            
            if semantic_rank is not None:
                rrf_score += alpha * (1 / (self.rrf_k + semantic_rank))

            scored_results.append(
                HybridSearchResult(
                    id=doc_id,
                    text=text,
                    score=rrf_score,
                    lexical_score=lexical_score,
                    semantic_score=semantic_score,
                    lexical_rank=lexical_rank,
                    semantic_rank=semantic_rank,
                    metadata=metadata,
                    source=source,
                )
            )

        scored_results.sort(key=lambda x: x.score, reverse=True)
        
        logger.debug(
            f"Hybrid: {len(lexical_results)} lexical + "
            f"{len(semantic_results)} semantic = {len(scored_results)} combined"
        )
        
        return scored_results[:top_k]

    def _parallel_search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int,
        source_filter: str | None,
    ) -> tuple[list, list]:
        """Run lexical and semantic searches in parallel for faster retrieval."""
        lexical_future = self._executor.submit(
            self.lexical_searcher.search,
            query=query,
            top_k=top_k,
            source_filter=source_filter,
        )
        semantic_future = self._executor.submit(
            self.semantic_searcher.search,
            query_embedding=query_embedding,
            top_k=top_k,
            source_filter=source_filter,
        )
        
        lexical_results = lexical_future.result()
        semantic_results = semantic_future.result()
        
        logger.debug("Parallel retrieval completed")
        return lexical_results, semantic_results

    def __del__(self):
        """Cleanup executor on deletion."""
        if self._executor:
            self._executor.shutdown(wait=False)


_hybrid_searcher: HybridSearcher | None = None


def get_hybrid_searcher(**kwargs) -> HybridSearcher:
    """Get or create global hybrid searcher instance."""
    global _hybrid_searcher
    if _hybrid_searcher is None:
        _hybrid_searcher = HybridSearcher(**kwargs)
    return _hybrid_searcher