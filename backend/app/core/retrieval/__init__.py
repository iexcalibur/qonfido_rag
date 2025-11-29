"""
Qonfido RAG - Retrieval Module
===============================
Search implementations: lexical, semantic, and hybrid.
"""

from app.core.retrieval.hybrid import HybridSearcher, HybridSearchResult, get_hybrid_searcher
from app.core.retrieval.lexical import LexicalSearcher, LexicalSearchResult, get_lexical_searcher
from app.core.retrieval.reranker import MockReranker, Reranker, RerankedResult, get_reranker
from app.core.retrieval.semantic import SemanticSearcher, SemanticSearchResult, get_semantic_searcher

__all__ = [
    "LexicalSearcher",
    "LexicalSearchResult",
    "get_lexical_searcher",
    "SemanticSearcher",
    "SemanticSearchResult",
    "get_semantic_searcher",
    "HybridSearcher",
    "HybridSearchResult",
    "get_hybrid_searcher",
    "Reranker",
    "MockReranker",
    "RerankedResult",
    "get_reranker",
]
