#backend/scripts/ingest_data.py

"""Data ingestion script to load and index data."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ingestion.loader import load_all_data
from app.core.ingestion.transformer import (
    transform_faqs_to_documents,
    transform_funds_to_documents,
)
from app.core.ingestion.embedder import generate_embeddings
from app.services.vector_store import VectorStoreService
from app.core.retrieval.lexical import BM25Retriever
from app.config import settings
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_data():
    """Main ingestion function."""
    logger.info("Starting data ingestion...")
    
    # 1. Load data
    logger.info("Loading data files...")
    data = load_all_data()
    faqs_df = data["faqs"]
    funds_df = data["funds"]
    
    logger.info(f"Loaded {len(faqs_df)} FAQs and {len(funds_df)} funds")
    
    # 2. Transform to documents
    logger.info("Transforming data to documents...")
    faq_docs = transform_faqs_to_documents(faqs_df)
    fund_docs = transform_funds_to_documents(funds_df)
    
    all_docs = faq_docs + fund_docs
    logger.info(f"Created {len(all_docs)} documents")
    
    # 3. Generate embeddings
    logger.info("Generating embeddings...")
    texts = [doc["content"] for doc in all_docs]
    embeddings = generate_embeddings(texts)
    embeddings_list = embeddings.tolist()
    
    # 4. Initialize vector store
    logger.info("Initializing vector store...")
    vector_store = VectorStoreService()
    vector_store.create_collection(force=False)
    
    # 5. Upload to Qdrant
    logger.info("Uploading documents to Qdrant...")
    vector_store.upload_documents(all_docs, embeddings_list)
    
    # 6. Initialize BM25 (save to disk for persistence)
    logger.info("Initializing BM25 retriever...")
    documents_text = [doc["content"] for doc in all_docs]
    metadata_list = [doc.get("metadata", {}) | {"id": doc["id"]} for doc in all_docs]
    
    # Save BM25 data for later use
    bm25_data_path = Path(settings.data_dir).parent / "processed" / "bm25_data.json"
    bm25_data_path.parent.mkdir(parents=True, exist_ok=True)
    
    bm25_data = {
        "documents": documents_text,
        "metadata": metadata_list,
    }
    
    with open(bm25_data_path, "w") as f:
        json.dump(bm25_data, f, indent=2)
    
    logger.info(f"Saved BM25 data to {bm25_data_path}")
    logger.info("✅ Data ingestion complete!")


if __name__ == "__main__":
    asyncio.run(ingest_data())