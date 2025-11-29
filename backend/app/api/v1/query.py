"""
Qonfido RAG - Query Endpoints
==============================
Main RAG query endpoints.
"""

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

# Initialize pipeline (will be done properly with dependency injection)
_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline."""
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
    """
    Process a RAG query.
    
    This endpoint:
    1. Classifies the query (FAQ vs numerical vs hybrid)
    2. Retrieves relevant documents using the specified search mode
    3. Optionally reranks results
    4. Generates a response using Claude
    
    **Search Modes:**
    - `lexical`: BM25 keyword-based search
    - `semantic`: Vector similarity search
    - `hybrid`: Combined lexical + semantic with RRF fusion
    
    **Example Queries:**
    - "What is an index fund?" (FAQ query)
    - "Which funds have the best Sharpe ratio?" (Numerical query)
    - "Explain low-risk funds with good returns" (Hybrid query)
    """
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
    """
    List available search modes.
    
    Returns information about each search mode and when to use them.
    """
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
