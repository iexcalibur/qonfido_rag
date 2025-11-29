#!/usr/bin/env python3
"""
Qonfido RAG - Data Ingestion Script
====================================
Load CSV data, generate embeddings, and index into vector store.

Usage:
    python -m scripts.ingest_data
    python -m scripts.ingest_data --data-dir data/raw
    python -m scripts.ingest_data --clear  # Clear existing data first
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.core.ingestion import DataLoader, get_embedder
from app.core.retrieval import get_lexical_searcher, get_semantic_searcher
from app.db import init_db
from app.utils import setup_logging

logger = logging.getLogger(__name__)


def ingest_data(
    data_dir: str | None = None,
    clear_existing: bool = False,
    skip_db: bool = False,
) -> dict:
    """
    Ingest data from CSV files into the RAG system.
    
    Args:
        data_dir: Directory containing CSV files (defaults to settings)
        clear_existing: Whether to clear existing indexed data
        skip_db: Skip database initialization
        
    Returns:
        Dictionary with ingestion statistics
    """
    # Use settings if not provided
    if data_dir is None:
        data_dir = settings.data_dir
    
    start_time = time.time()
    stats = {
        "faqs_loaded": 0,
        "funds_loaded": 0,
        "documents_indexed": 0,
        "time_seconds": 0,
    }

    logger.info("=" * 60)
    logger.info("Starting data ingestion...")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"FAQs file: {settings.faqs_file}")
    logger.info(f"Funds file: {settings.funds_file}")
    logger.info("=" * 60)

    # Initialize database (optional)
    if not skip_db:
        try:
            init_db()
            logger.info("✓ Database initialized")
        except Exception as e:
            logger.warning(f"Database init skipped: {e}")

    # Load data
    logger.info("\n[1/4] Loading CSV data...")
    loader = DataLoader(
        data_dir=data_dir,
        faqs_file=settings.faqs_file,
        funds_file=settings.funds_file,
    )
    
    try:
        faqs, funds = loader.load_all()
        stats["faqs_loaded"] = len(faqs)
        stats["funds_loaded"] = len(funds)
        logger.info(f"✓ Loaded {len(faqs)} FAQs")
        logger.info(f"✓ Loaded {len(funds)} funds")
    except FileNotFoundError as e:
        logger.error(f"✗ Data files not found: {e}")
        logger.error(f"  Please place CSV files in: {data_dir}/")
        logger.error(f"  Expected files: {settings.faqs_file}, {settings.funds_file}")
        return stats

    if not faqs and not funds:
        logger.warning("⚠ No data loaded. Check your CSV files.")
        logger.info(f"  Looking for: {data_dir}/{settings.faqs_file}")
        logger.info(f"  Looking for: {data_dir}/{settings.funds_file}")
        # Continue anyway - may have only one type
        
    # Prepare documents
    logger.info("\n[2/4] Preparing documents...")
    documents = loader.get_all_documents()
    
    if not documents:
        logger.error("✗ No documents to index.")
        return stats
        
    logger.info(f"✓ Prepared {len(documents)} documents for indexing")

    # Generate embeddings
    logger.info("\n[3/4] Generating embeddings...")
    logger.info(f"  Model: {settings.embedding_model}")
    
    embedder = get_embedder(model_name=settings.embedding_model)
    texts = [doc["text"] for doc in documents]
    
    embeddings = embedder.embed_texts(texts, show_progress=True)
    logger.info(f"✓ Generated embeddings: {embeddings.shape}")

    # Index documents
    logger.info("\n[4/4] Indexing documents...")
    
    # Lexical index
    lexical_searcher = get_lexical_searcher()
    lexical_searcher.index_documents(documents)
    logger.info(f"✓ Lexical index: {lexical_searcher.document_count} documents")

    # Semantic index
    semantic_searcher = get_semantic_searcher()
    if clear_existing:
        semantic_searcher.clear()
        logger.info("  Cleared existing vector store")
    
    semantic_searcher.index_documents(documents, embeddings)
    logger.info(f"✓ Semantic index: {semantic_searcher.document_count} documents")

    stats["documents_indexed"] = len(documents)
    stats["time_seconds"] = round(time.time() - start_time, 2)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  FAQs loaded:        {stats['faqs_loaded']}")
    logger.info(f"  Funds loaded:       {stats['funds_loaded']}")
    logger.info(f"  Documents indexed:  {stats['documents_indexed']}")
    logger.info(f"  Time taken:         {stats['time_seconds']}s")
    logger.info("=" * 60)

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest CSV data into the RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.ingest_data
  python -m scripts.ingest_data --data-dir /path/to/data
  python -m scripts.ingest_data --clear --verbose
        """,
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Directory containing CSV files (default: from settings)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing indexed data before ingestion",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip database initialization",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Run ingestion
    try:
        stats = ingest_data(
            data_dir=args.data_dir,
            clear_existing=args.clear,
            skip_db=args.skip_db,
        )
        
        if stats["documents_indexed"] > 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nIngestion cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
