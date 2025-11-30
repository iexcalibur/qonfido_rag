"""RAG query endpoints for natural language fund queries."""

import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    ErrorResponse,
    QueryRequest,
    QueryResponse,
    SearchMode,
)
from app.core.orchestration.pipeline import RAGPipeline

router = APIRouter(tags=["Query"])
logger = logging.getLogger(__name__)

_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def query(request: QueryRequest) -> QueryResponse:
    """Process a RAG query with retrieval and generation."""
    try:
        logger.info(f"Processing query: {request.query[:50]}... | mode={request.search_mode}")
        
        pipeline = get_pipeline()
        
        response = await pipeline.process(
            query=request.query,
            search_mode=request.search_mode,
            top_k=request.top_k,
            rerank=request.rerank,
            source_filter=request.source_filter,
        )
        
        logger.info(f"Query processed successfully | sources={len(response.sources)}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search-modes")
async def list_search_modes() -> dict:
    """List available search modes and their descriptions."""
    return {
        "modes": [
            {
                "name": SearchMode.LEXICAL.value,
                "description": "BM25 keyword-based search",
                "best_for": "Exact keyword matching, specific terms",
            },
            {
                "name": SearchMode.SEMANTIC.value,
                "description": "Vector similarity search using embeddings",
                "best_for": "Conceptual similarity, paraphrased queries",
            },
            {
                "name": SearchMode.HYBRID.value,
                "description": "Combined lexical + semantic with RRF fusion",
                "best_for": "Best overall accuracy, recommended default",
            },
        ],
        "default": SearchMode.HYBRID.value,
    }
