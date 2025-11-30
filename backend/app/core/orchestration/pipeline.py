"""Main RAG pipeline orchestrating ingestion, retrieval, and generation."""

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
    """Main RAG pipeline with caching, parallel retrieval, and hash-based persistence."""

    def __init__(
        self,
        data_dir: str | None = None,
        use_reranker: bool = True,
        use_query_cache: bool = True,
    ):
        self.data_dir = data_dir or settings.data_dir
        self.use_reranker = use_reranker
        self.use_query_cache = use_query_cache
        self._initialized = False
        
        self.embedder = get_embedder(use_cache=True)
        self.lexical_searcher = get_lexical_searcher()
        self.semantic_searcher = get_semantic_searcher(
            collection_name=settings.chroma_collection_name,
            persist_dir=settings.chroma_persist_dir,
        )
        self.hybrid_searcher = get_hybrid_searcher(use_parallel=True)
        self.generator = get_generator()
        
        self._state_file = Path(self.data_dir).parent / "index.state"
        
        self._query_cache = None
        if use_query_cache:
            try:
                from app.services.cache import get_query_cache
                self._query_cache = get_query_cache()
                logger.info("Query cache enabled")
            except Exception as e:
                logger.warning(f"Query cache not available: {e}")
        
        try:
            self.reranker = get_reranker() if use_reranker else None
        except Exception as e:
            logger.warning(f"Reranker not available: {e}")
            self.reranker = None

    def _get_current_state_hash(self) -> str:
        """Generate MD5 hash of data files and config for change detection."""
        hasher = hashlib.md5()
        
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
                hasher.update(str(file_path).encode())
        
        hasher.update(settings.embedding_model.encode())
        hasher.update(str(settings.embedding_dimension).encode())
        
        return hasher.hexdigest()

    def initialize(self, clear_existing: bool = False) -> None:
        """Initialize pipeline with hash-based change detection for fast startup."""
        if self._initialized:
            return
            
        logger.info("Initializing RAG pipeline...")
        
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
        
        self.lexical_searcher.index_documents(documents)
        logger.info("✓ Lexical search index built")
        
        current_hash = self._get_current_state_hash()
        should_reindex = clear_existing
        
        if not clear_existing and self._state_file.exists():
            try:
                saved_state = json.loads(self._state_file.read_text())
                saved_hash = saved_state.get("hash")
                
                if saved_hash == current_hash:
                    try:
                        self.semantic_searcher._initialize()
                        doc_count = self.semantic_searcher.document_count
                        
                        if doc_count > 0:
                            logger.info("Data/Config unchanged. Using persistent vector store.")
                            logger.info(f"✓ Loaded {doc_count} documents from persistent store (instant startup!)")
                            self._initialized = True
                            
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
        
        if should_reindex:
            logger.info("🔄 Change detected or index missing. Starting full semantic ingestion...")
            
            try:
                self.semantic_searcher.clear()
                logger.info("✓ Cleared existing semantic index")
            except Exception as e:
                logger.warning(f"⚠ Failed to clear existing semantic index (may not exist): {e}")
            
            texts = [doc["text"] for doc in documents]
            embeddings = self.embedder.embed_texts(texts)
            
            self.semantic_searcher.index_documents(documents, embeddings)
            logger.info("✓ Semantic search index built and persisted")
            
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
        logger.info(f"Pipeline initialized with {len(documents)} documents")
        
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
        """Process query through RAG pipeline: retrieve, rerank, generate."""
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
        
        if not self._initialized:
            self.initialize()

        query_embedding = self.embedder.embed_query(query)
        
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
        else:
            results = self.hybrid_searcher.search(
                query=query,
                query_embedding=query_embedding,
                top_k=top_k,
                source_filter=source_filter,
            )

        if rerank and self.reranker and results:
            try:
                results = self.reranker.rerank(
                    query=query,
                    results=results,
                    top_k=min(top_k, len(results)),
                )
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")

        context = [
            {
                "text": r.text,
                "source": r.source,
                "metadata": r.metadata,
            }
            for r in results
        ]

        answer = self.generator.generate(
            query=query,
            context=context,
        )

        query_type = self._classify_query(query, results)
        funds = self._extract_fund_info(results)

        sources = [
            SourceDocument(
                id=r.id,
                text=r.text[:500],
                source=r.source,
                score=r.score if hasattr(r, 'score') else (r.rerank_score if hasattr(r, 'rerank_score') else 0.0),
                metadata=r.metadata,
            )
            for r in results
        ]

        confidence = self._calculate_confidence(results)

        response = QueryResponse(
            answer=answer,
            query_type=query_type,
            funds=funds,
            sources=sources,
            confidence=confidence,
            search_mode=search_mode,
        )
        
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
        """Classify query type (faq/numerical/hybrid) based on content and results."""
        query_lower = query.lower()
        
        numerical_keywords = [
            "best", "top", "highest", "lowest", "sharpe", "cagr",
            "return", "performance", "risk", "volatility", "compare"
        ]
        
        faq_keywords = [
            "what is", "what are", "how does", "explain", "define",
            "meaning", "difference between"
        ]
        
        is_numerical = any(kw in query_lower for kw in numerical_keywords)
        is_faq = any(kw in query_lower for kw in faq_keywords)
        
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
        """Extract fund information from results with fallback to funds cache."""
        from app.api.v1.funds import get_funds
        
        def _to_float(value) -> float | None:
            """Convert value to float handling None and string cases."""
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
            
            cached_fund = None
            if fund_id and fund_id in funds_by_id:
                cached_fund = funds_by_id[fund_id]
            elif fund_name in funds_by_name:
                cached_fund = funds_by_name[fund_name]
            
            cagr_1yr = _to_float(metadata.get("cagr_1yr"))
            cagr_3yr = _to_float(metadata.get("cagr_3yr"))
            cagr_5yr = _to_float(metadata.get("cagr_5yr"))
            sharpe_ratio = _to_float(metadata.get("sharpe_ratio"))
            volatility = _to_float(metadata.get("volatility"))
            
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
        
        return funds[:5]

    def _calculate_confidence(self, results: list) -> float:
        """Calculate confidence score from top retrieval result scores."""
        if not results:
            return 0.0
        
        scores = []
        for r in results[:3]:
            if hasattr(r, 'rerank_score'):
                scores.append(r.rerank_score)
            elif hasattr(r, 'score'):
                scores.append(r.score)
        
        if not scores:
            return 0.5
        
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


_pipeline: RAGPipeline | None = None


def get_pipeline(**kwargs) -> RAGPipeline:
    """Get or create global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline(**kwargs)
    return _pipeline