"""
Qonfido RAG - Lexical Search
=============================
BM25-based lexical/keyword search implementation.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


@dataclass
class LexicalSearchResult:
    """Represents a lexical search result."""
    
    id: str
    text: str
    score: float
    metadata: dict[str, Any]
    source: str


class LexicalSearcher:
    """
    BM25-based lexical search engine.
    
    BM25 is great for:
    - Exact keyword matching
    - Specific fund names
    - Technical terms
    """

    def __init__(self):
        self._index: BM25Okapi | None = None
        self._documents: list[dict] = []
        self._tokenized_docs: list[list[str]] = []

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text for BM25."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = [t.strip() for t in text.split() if t.strip()]
        return tokens

    def index_documents(self, documents: list[dict]) -> None:
        """
        Index documents for search.
        
        Args:
            documents: List of dicts with 'id', 'text', 'metadata', 'source' keys
        """
        if not documents:
            logger.warning("No documents to index")
            return

        logger.info(f"Indexing {len(documents)} documents for lexical search...")
        
        self._documents = documents
        self._tokenized_docs = [
            self._tokenize(doc["text"]) for doc in documents
        ]
        
        self._index = BM25Okapi(self._tokenized_docs)
        
        logger.info(f"Indexed {len(documents)} documents")

    def search(
        self,
        query: str,
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[LexicalSearchResult]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            source_filter: Filter by source ('faq' or 'fund')
            
        Returns:
            List of LexicalSearchResult objects
        """
        if self._index is None:
            logger.warning("Index not built. Call index_documents first.")
            return []

        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []

        scores = self._index.get_scores(query_tokens)
        scored_indices = [(score, idx) for idx, score in enumerate(scores)]
        scored_indices.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, idx in scored_indices:
            if score <= 0:
                continue
                
            doc = self._documents[idx]
            
            if source_filter and doc.get("source") != source_filter:
                continue
            
            results.append(
                LexicalSearchResult(
                    id=doc["id"],
                    text=doc["text"],
                    score=float(score),
                    metadata=doc.get("metadata", {}),
                    source=doc.get("source", "unknown"),
                )
            )
            
            if len(results) >= top_k:
                break

        return results

    @property
    def document_count(self) -> int:
        """Get the number of indexed documents."""
        return len(self._documents)


# =============================================================================
# Global Instance
# =============================================================================

_lexical_searcher: LexicalSearcher | None = None


def get_lexical_searcher() -> LexicalSearcher:
    """Get or create the global lexical searcher instance."""
    global _lexical_searcher
    if _lexical_searcher is None:
        _lexical_searcher = LexicalSearcher()
    return _lexical_searcher
