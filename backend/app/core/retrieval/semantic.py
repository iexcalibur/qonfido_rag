"""Vector-based semantic search using ChromaDB."""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SemanticSearchResult:
    """Semantic search result with similarity score."""
    
    id: str
    text: str
    score: float
    metadata: dict[str, Any]
    source: str


class SemanticSearcher:
    """Semantic search using ChromaDB for in-process vector storage."""

    def __init__(
        self,
        collection_name: str = "qonfido_funds",
        persist_dir: str | None = None,
    ):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self._client = None
        self._collection = None
        self._documents: dict[str, dict] = {}

    def _initialize(self):
        """Initialize ChromaDB client and collection (lazy initialization)."""
        if self._client is not None:
            return
            
        try:
            import chromadb
            from chromadb.config import Settings
            
            if self.persist_dir:
                self._client = chromadb.PersistentClient(
                    path=self.persist_dir,
                    settings=Settings(anonymized_telemetry=False),
                )
            else:
                self._client = chromadb.Client(
                    Settings(anonymized_telemetry=False)
                )
            
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            logger.info(f"ChromaDB initialized: {self.collection_name}")
            
        except ImportError:
            logger.error("ChromaDB not installed. Run: pip install chromadb")
            raise

    def index_documents(
        self,
        documents: list[dict],
        embeddings: np.ndarray,
    ) -> None:
        """Index documents with their embeddings in ChromaDB."""
        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings count mismatch")

        self._initialize()

        logger.info(f"Indexing {len(documents)} documents for semantic search...")

        for doc in documents:
            self._documents[doc["id"]] = doc

        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = []
        
        for doc in documents:
            meta = {"source": doc.get("source", "unknown")}
            if "metadata" in doc:
                for k, v in doc["metadata"].items():
                    if v is not None and isinstance(v, (str, int, float, bool)):
                        meta[k] = v
            metadatas.append(meta)

        self._collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
        )
        
        logger.info(f"Indexed {len(documents)} documents")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[SemanticSearchResult]:
        """Search for similar documents using cosine similarity."""
        self._initialize()
        
        if self._collection.count() == 0:
            logger.warning("Collection is empty")
            return []

        where = None
        if source_filter:
            where = {"source": source_filter}

        results = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance
                
                search_results.append(
                    SemanticSearchResult(
                        id=doc_id,
                        text=results["documents"][0][i] if results["documents"] else "",
                        score=float(score),
                        metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                        source=results["metadatas"][0][i].get("source", "unknown") if results["metadatas"] else "unknown",
                    )
                )

        return search_results

    @property
    def document_count(self) -> int:
        """Get number of indexed documents."""
        self._initialize()
        return self._collection.count()
    
    def clear(self) -> None:
        """Clear all documents from the collection."""
        self._initialize()
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._documents.clear()
        logger.info("Collection cleared")


_semantic_searcher: SemanticSearcher | None = None


def get_semantic_searcher(**kwargs) -> SemanticSearcher:
    """Get or create global semantic searcher instance."""
    global _semantic_searcher
    if _semantic_searcher is None:
        _semantic_searcher = SemanticSearcher(**kwargs)
    return _semantic_searcher
