"""Main entry point for the FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.core.orchestration import get_pipeline
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    setup_logging(settings.log_level)
    
    import os
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    
    logger.info("=" * 80)
    logger.info("Starting Qonfido RAG Backend...")
    logger.info("=" * 80)
    
    logger.info("\n[1/2] Loading funds data cache...")
    try:
        from app.api.v1.funds import clear_funds_cache, get_funds
        clear_funds_cache()
        funds = get_funds()
        logger.info(f"✓ Loaded {len(funds)} funds from CSV into cache")
    except Exception as e:
        logger.warning(f"⚠ Failed to pre-load funds cache: {e}")
        logger.info("  Funds will be loaded on first request")
    
    logger.info("\n[2/2] Pre-initializing RAG pipeline...")
    logger.info("  This includes:")
    logger.info("    - Downloading embedding model (first time only, ~2.3GB)")
    logger.info("    - Generating embeddings for all documents")
    logger.info("    - Indexing for semantic and lexical search")
    logger.info("  This may take a few minutes on first run...")
    
    try:
        pipeline = get_pipeline()
        pipeline.initialize()
        logger.info("\n" + "=" * 80)
        logger.info("✓ RAG pipeline initialized successfully!")
        logger.info("✓ Backend is ready to serve requests")
        logger.info("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"\n✗ Failed to initialize RAG pipeline: {e}")
        logger.warning("API will start, but query functionality may be limited")
        logger.warning("Try restarting the server once the model download completes\n")
    
    yield
    
    logger.info("\nShutting down backend...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Financial Intelligence RAG System - AI Co-Pilot for Money",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Financial Intelligence RAG System",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
