"""
Qonfido RAG - Pipeline
=======================
Main RAG pipeline that orchestrates ingestion, retrieval, and generation.

Features:
- Query caching for repeated queries
- Embedding caching for efficiency
- Parallel hybrid retrieval
- Optional reranking with Cohere
- Smart Persistence with Hash-based change detection
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from app.api.schemas import (
    FundInfo,
    QueryResponse,
    SearchMode,
    SourceDocument,
)
from app.config import settings
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
    2. Query embedding (with caching)
    3. Retrieval (lexical/semantic/hybrid with parallel execution)
    4. Reranking (optional)
    5. Response generation
    6. Query result caching
    """

    def __init__(
        self,
        data_dir: str | None = None,
        use_reranker: bool = True,
        use_query_cache: bool = True,
    ):
        # Use settings if not provided (settings.data_dir already includes 'raw')
        self.data_dir = data_dir or settings.data_dir
        self.use_reranker = use_reranker
        self.use_query_cache = use_query_cache
        self._initialized = False
        
        # Components (lazy loaded) - enable caching and parallel
        # Enable ChromaDB persistence with configured directory
        self.embedder = get_embedder(use_cache=True)
        self.lexical_searcher = get_lexical_searcher()
        self.semantic_searcher = get_semantic_searcher(
            collection_name=settings.chroma_collection_name,
            persist_dir=settings.chroma_persist_dir,
        )
        self.hybrid_searcher = get_hybrid_searcher(use_parallel=True)
        self.generator = get_generator()
        
        # State file path for hash-based change detection
        # Store in parent directory to keep raw data directory clean
        self._state_file = Path(self.data_dir).parent / "index.state"
        
        # Query cache
        self._query_cache = None
        if use_query_cache:
            try:
                from app.services.cache import get_query_cache
                self._query_cache = get_query_cache()
                logger.info("Query cache enabled")
            except Exception as e:
                logger.warning(f"Query cache not available: {e}")
        
        # Try to get reranker (may fail if no API key)
        try:
            self.reranker = get_reranker() if use_reranker else None
        except Exception as e:
            logger.warning(f"Reranker not available: {e}")
            self.reranker = None

    def _get_current_state_hash(self) -> str:
        """
        Generate a hash of current data files and configuration.
        
        This hash represents the "fingerprint" of the current data state.
        If the hash changes, we know the data or config has changed and
        we need to re-index.
        
        Returns:
            Hexadecimal hash string representing current data state
        """
        hasher = hashlib.md5()
        
        # 1. Hash the data files
        files = [
            Path(settings.faqs_path),
            Path(settings.funds_path),
        ]
        
        for file_path in files:
            if file_path.exists():
                try:
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hasher.update(chunk)
                except Exception as e:
                    logger.warning(f"Failed to hash file {file_path}: {e}")
            else:
                logger.warning(f"Data file not found: {file_path}")
                # Include in hash even if missing to detect file addition/removal
                hasher.update(str(file_path).encode())
        
        # 2. Hash critical config (if model changes, we must re-index)
        # Include embedding model name and dimension
        hasher.update(settings.embedding_model.encode())
        hasher.update(str(settings.embedding_dimension).encode())
        
        return hasher.hexdigest()

    def initialize(self, clear_existing: bool = False) -> None:
        """
        Initialize the pipeline by loading and indexing data.
        
        Uses hash-based change detection for smart persistence:
        - Always loads documents and builds lexical index (fast, in-memory)
        - Only checks hash for semantic indexing (slow, persistent)
        - If data/config unchanged: Uses persistent vector store (fast startup)
        - If data/config changed: Clears and re-indexes (ensures fresh data)
        
        Args:
            clear_existing: If True, forces a rebuild of the semantic index regardless of state.
        """
        if self._initialized:
            return
            
        logger.info("Initializing RAG pipeline...")
        
        # 1. Always Load Data (Fast) - Needed for Lexical Search (BM25) which isn't persistent
        loader = DataLoader(
            data_dir=self.data_dir,
            faqs_file=settings.faqs_file,
            funds_file=settings.funds_file,
        )
        documents = loader.get_all_documents()
        
        if not documents:
            logger.warning("No documents loaded!")
            self._initialized = True
            return
            
        logger.info(f"Loaded {len(documents)} documents from CSV files")
        
        # 2. Always Build Lexical Index (Fast, In-Memory)
        # BM25 doesn't persist, so we rebuild it every time (it's fast)
        self.lexical_searcher.index_documents(documents)
        logger.info("✓ Lexical search index built")
        
        # 3. Smart Semantic Indexing (Slow, Persistent)
        # Check if we can skip the expensive embedding/indexing step
        current_hash = self._get_current_state_hash()
        should_reindex = clear_existing
        
        if not clear_existing and self._state_file.exists():
            try:
                saved_state = json.loads(self._state_file.read_text())
                saved_hash = saved_state.get("hash")
                
                if saved_hash == current_hash:
                    # Hash matches - check if the collection actually has data
                    try:
                        self.semantic_searcher._initialize()
                        doc_count = self.semantic_searcher.document_count
                        
                        if doc_count > 0:
                            logger.info("✅ Data/Config unchanged. Using persistent vector store.")
                            logger.info(f"✓ Loaded {doc_count} documents from persistent store (instant startup!)")
                            self._initialized = True
                            
                            # Log cache stats
                            if hasattr(self.embedder, 'cache_stats'):
                                stats = self.embedder.cache_stats
                                logger.info(f"Embedding cache: {stats.get('size', 0)} entries")
                            
                            logger.info(f"Pipeline initialized with {len(documents)} documents")
                            return
                        else:
                            logger.warning("⚠ Persistence file matches but vector store is empty. Re-indexing.")
                            should_reindex = True
                    except Exception as e:
                        logger.warning(f"⚠ Failed to check persistent store: {e}. Re-indexing.")
                        should_reindex = True
                else:
                    logger.info("🔄 Change detected. Hash mismatch:")
                    logger.info(f"  Saved:   {saved_hash[:16] if saved_hash else 'None'}...")
                    logger.info(f"  Current: {current_hash[:16]}...")
                    should_reindex = True
            except Exception as e:
                logger.warning(f"⚠ State file corrupted, forcing refresh: {e}")
                should_reindex = True
        else:
            if not self._state_file.exists():
                logger.info("🔄 No state file found. Starting full semantic ingestion...")
            should_reindex = True
        
        # --- Re-index Semantic Search (Data Changed or Force Refresh) ---
        if should_reindex:
            logger.info("🔄 Change detected or index missing. Starting full semantic ingestion...")
            
            # Clear existing semantic index to ensure clean state
            try:
                self.semantic_searcher.clear()
                logger.info("✓ Cleared existing semantic index")
            except Exception as e:
                logger.warning(f"⚠ Failed to clear existing semantic index (may not exist): {e}")
            
            # Generate embeddings (this is the slow part, but caching helps)
            texts = [doc["text"] for doc in documents]
            embeddings = self.embedder.embed_texts(texts)
            
            # Index into Vector Store (persistent)
            self.semantic_searcher.index_documents(documents, embeddings)
            logger.info("✓ Semantic search index built and persisted")
            
            # Save new state
            try:
                state_data = {
                    "hash": current_hash,
                    "document_count": len(documents),
                    "embedding_model": settings.embedding_model,
                }
                self._state_file.parent.mkdir(parents=True, exist_ok=True)
                self._state_file.write_text(json.dumps(state_data, indent=2))
                logger.info(f"✓ Index state saved to {self._state_file}")
            except Exception as e:
                logger.warning(f"⚠ Failed to save index state: {e}")
        
        self._initialized = True
        logger.info(f"✅ Pipeline initialized with {len(documents)} documents")
        
        # Log cache stats
        if hasattr(self.embedder, 'cache_stats'):
            stats = self.embedder.cache_stats
            logger.info(f"Embedding cache: {stats.get('size', 0)} entries")

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
        # Check query cache first
        if self._query_cache and self.use_query_cache:
            cached = self._query_cache.get(
                query=query,
                search_mode=search_mode.value,
                top_k=top_k,
                source_filter=source_filter,
            )
            if cached:
                logger.info("Query cache hit!")
                return QueryResponse(**cached)
        
        # Ensure initialized
        if not self._initialized:
            self.initialize()

        # Embed query (with caching)
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
        else:  # HYBRID (with parallel retrieval)
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

        response = QueryResponse(
            answer=answer,
            query_type=query_type,
            funds=funds,
            sources=sources,
            confidence=confidence,
            search_mode=search_mode,
        )
        
        # Cache the response
        if self._query_cache and self.use_query_cache:
            self._query_cache.set(
                query=query,
                search_mode=search_mode.value,
                top_k=top_k,
                result=response.model_dump(),
                source_filter=source_filter,
            )

        return response

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
        """Extract fund information from results, with fallback to funds cache."""
        from app.api.v1.funds import get_funds
        
        def _to_float(value) -> float | None:
            """Convert value to float, handling None and string cases."""
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            return None
        
        funds = []
        seen_names = set()
        
        # Get full fund data from cache for fallback (by name and ID)
        try:
            all_funds = get_funds()
            funds_by_name = {f.fund_name: f for f in all_funds}
            funds_by_id = {f.id: f for f in all_funds}
        except Exception as e:
            logger.warning(f"Could not load funds cache for fallback: {e}")
            funds_by_name = {}
            funds_by_id = {}
        
        for r in results:
            if r.source != "fund":
                continue
            
            metadata = r.metadata
            fund_name = metadata.get("fund_name")
            fund_id = metadata.get("id")
            
            if not fund_name or fund_name in seen_names:
                continue
            
            seen_names.add(fund_name)
            
            # Try to get full fund data from cache (prefer by ID, fallback to name)
            cached_fund = None
            if fund_id and fund_id in funds_by_id:
                cached_fund = funds_by_id[fund_id]
            elif fund_name in funds_by_name:
                cached_fund = funds_by_name[fund_name]
            
            # Extract and convert numeric values from metadata
            cagr_1yr = _to_float(metadata.get("cagr_1yr"))
            cagr_3yr = _to_float(metadata.get("cagr_3yr"))
            cagr_5yr = _to_float(metadata.get("cagr_5yr"))
            sharpe_ratio = _to_float(metadata.get("sharpe_ratio"))
            volatility = _to_float(metadata.get("volatility"))
            
            # Use metadata first, but fallback to cached fund data if metadata values are missing
            fund_info = FundInfo(
                fund_name=fund_name,
                fund_house=metadata.get("fund_house") or (cached_fund.fund_house if cached_fund else None),
                category=metadata.get("category") or (cached_fund.category if cached_fund else None),
                cagr_1yr=cagr_1yr if cagr_1yr is not None else (cached_fund.cagr_1yr if cached_fund else None),
                cagr_3yr=cagr_3yr if cagr_3yr is not None else (cached_fund.cagr_3yr if cached_fund else None),
                cagr_5yr=cagr_5yr if cagr_5yr is not None else (cached_fund.cagr_5yr if cached_fund else None),
                sharpe_ratio=sharpe_ratio if sharpe_ratio is not None else (cached_fund.sharpe_ratio if cached_fund else None),
                volatility=volatility if volatility is not None else (cached_fund.volatility if cached_fund else None),
                risk_level=metadata.get("risk_level") or (cached_fund.risk_level if cached_fund else None),
            )
            
            funds.append(fund_info)
        
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
    
    @property
    def cache_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        stats = {
            "embedding_cache": self.embedder.cache_stats if hasattr(self.embedder, 'cache_stats') else {},
            "query_cache_enabled": self._query_cache is not None,
        }
        if self._query_cache:
            stats["query_cache_size"] = self._query_cache._cache.size
        return stats


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