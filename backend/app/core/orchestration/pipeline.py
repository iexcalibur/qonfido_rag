"""
Qonfido RAG - Pipeline
=======================
Main RAG pipeline that orchestrates ingestion, retrieval, and generation.
"""

import logging
from typing import Any

from app.api.schemas import (
    FundInfo,
    QueryResponse,
    SearchMode,
    SourceDocument,
)
from app.core.generation import get_generator
from app.core.ingestion import DataLoader, get_embedder
from app.core.retrieval import (
    get_hybrid_searcher,
    get_lexical_searcher,
    get_reranker,
    get_semantic_searcher,
)

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Main RAG pipeline orchestrating:
    1. Data ingestion and indexing
    2. Query embedding
    3. Retrieval (lexical/semantic/hybrid)
    4. Reranking (optional)
    5. Response generation
    """

    def __init__(
        self,
        data_dir: str = "data/raw",
        use_reranker: bool = True,
    ):
        self.data_dir = data_dir
        self.use_reranker = use_reranker
        self._initialized = False
        
        # Components
        self.embedder = get_embedder()
        self.lexical_searcher = get_lexical_searcher()
        self.semantic_searcher = get_semantic_searcher()
        self.hybrid_searcher = get_hybrid_searcher()
        self.generator = get_generator()
        
        # Try to get reranker (may fail if no API key)
        try:
            self.reranker = get_reranker() if use_reranker else None
        except Exception as e:
            logger.warning(f"Reranker not available: {e}")
            self.reranker = None

    def initialize(self) -> None:
        """Initialize the pipeline by loading and indexing data."""
        if self._initialized:
            return

        logger.info("Initializing RAG pipeline...")
        
        # Load data
        loader = DataLoader(self.data_dir)
        documents = loader.get_all_documents()
        
        if not documents:
            logger.warning("No documents loaded!")
            self._initialized = True
            return

        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedder.embed_texts(texts)
        
        # Index for lexical search
        self.lexical_searcher.index_documents(documents)
        
        # Index for semantic search
        self.semantic_searcher.index_documents(documents, embeddings)
        
        self._initialized = True
        logger.info(f"Pipeline initialized with {len(documents)} documents")

    async def process(
        self,
        query: str,
        search_mode: SearchMode = SearchMode.HYBRID,
        top_k: int = 5,
        rerank: bool = True,
        source_filter: str | None = None,
    ) -> QueryResponse:
        """
        Process a query through the RAG pipeline.
        
        Args:
            query: User's question
            search_mode: Search mode (lexical/semantic/hybrid)
            top_k: Number of results to retrieve
            rerank: Whether to apply reranking
            source_filter: Filter by source type
            
        Returns:
            QueryResponse with answer and sources
        """
        # Ensure initialized
        if not self._initialized:
            self.initialize()

        # Embed query
        query_embedding = self.embedder.embed_query(query)
        
        # Retrieve documents based on mode
        if search_mode == SearchMode.LEXICAL:
            results = self.lexical_searcher.search(
                query=query,
                top_k=top_k,
                source_filter=source_filter,
            )
        elif search_mode == SearchMode.SEMANTIC:
            results = self.semantic_searcher.search(
                query_embedding=query_embedding,
                top_k=top_k,
                source_filter=source_filter,
            )
        else:  # HYBRID
            results = self.hybrid_searcher.search(
                query=query,
                query_embedding=query_embedding,
                top_k=top_k,
                source_filter=source_filter,
            )

        # Optionally rerank
        if rerank and self.reranker and results:
            try:
                results = self.reranker.rerank(
                    query=query,
                    results=results,
                    top_k=min(top_k, len(results)),
                )
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")

        # Prepare context for generation
        context = [
            {
                "text": r.text,
                "source": r.source,
                "metadata": r.metadata,
            }
            for r in results
        ]

        # Generate response
        answer = self.generator.generate(
            query=query,
            context=context,
        )

        # Classify query type
        query_type = self._classify_query(query, results)

        # Extract fund info
        funds = self._extract_fund_info(results)

        # Build source documents
        sources = [
            SourceDocument(
                id=r.id,
                text=r.text[:500],  # Truncate for response
                source=r.source,
                score=r.score if hasattr(r, 'score') else (r.rerank_score if hasattr(r, 'rerank_score') else 0.0),
                metadata=r.metadata,
            )
            for r in results
        ]

        # Calculate confidence
        confidence = self._calculate_confidence(results)

        return QueryResponse(
            answer=answer,
            query_type=query_type,
            funds=funds,
            sources=sources,
            confidence=confidence,
            search_mode=search_mode,
        )

    def _classify_query(self, query: str, results: list) -> str:
        """Classify the query type based on content and results."""
        query_lower = query.lower()
        
        # Check for numerical indicators
        numerical_keywords = [
            "best", "top", "highest", "lowest", "sharpe", "cagr",
            "return", "performance", "risk", "volatility", "compare"
        ]
        
        # Check for FAQ indicators
        faq_keywords = [
            "what is", "what are", "how does", "explain", "define",
            "meaning", "difference between"
        ]
        
        is_numerical = any(kw in query_lower for kw in numerical_keywords)
        is_faq = any(kw in query_lower for kw in faq_keywords)
        
        # Check result sources
        if results:
            sources = [r.source for r in results[:3]]
            fund_count = sources.count("fund")
            faq_count = sources.count("faq")
            
            if fund_count > faq_count and is_numerical:
                return "numerical"
            elif faq_count > fund_count and is_faq:
                return "faq"
        
        return "hybrid"

    def _extract_fund_info(self, results: list) -> list[FundInfo]:
        """Extract fund information from results."""
        funds = []
        seen_names = set()
        
        for r in results:
            if r.source != "fund":
                continue
            
            metadata = r.metadata
            fund_name = metadata.get("fund_name")
            
            if not fund_name or fund_name in seen_names:
                continue
            
            seen_names.add(fund_name)
            
            funds.append(
                FundInfo(
                    fund_name=fund_name,
                    fund_house=metadata.get("fund_house"),
                    category=metadata.get("category"),
                    cagr_1yr=metadata.get("cagr_1yr"),
                    cagr_3yr=metadata.get("cagr_3yr"),
                    cagr_5yr=metadata.get("cagr_5yr"),
                    sharpe_ratio=metadata.get("sharpe_ratio"),
                    volatility=metadata.get("volatility"),
                    risk_level=metadata.get("risk_level"),
                )
            )
        
        return funds[:5]  # Limit to top 5 funds

    def _calculate_confidence(self, results: list) -> float:
        """Calculate confidence score based on retrieval results."""
        if not results:
            return 0.0
        
        # Use average of top scores
        scores = []
        for r in results[:3]:
            if hasattr(r, 'rerank_score'):
                scores.append(r.rerank_score)
            elif hasattr(r, 'score'):
                scores.append(r.score)
        
        if not scores:
            return 0.5
        
        # Normalize to 0-1 range
        avg_score = sum(scores) / len(scores)
        return min(max(avg_score, 0.0), 1.0)


# =============================================================================
# Global Instance
# =============================================================================

_pipeline: RAGPipeline | None = None


def get_pipeline(**kwargs) -> RAGPipeline:
    """Get or create the global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline(**kwargs)
    return _pipeline
