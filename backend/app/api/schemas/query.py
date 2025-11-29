"""
Qonfido RAG - Query Schemas
============================
Pydantic models for query requests and responses.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    """Search mode options."""
    
    LEXICAL = "lexical"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    
    query: str = Field(
        ...,
        description="User's question or query",
        min_length=1,
        max_length=1000,
        examples=["Which funds have the best Sharpe ratio?"],
    )
    search_mode: SearchMode = Field(
        default=SearchMode.HYBRID,
        description="Search mode: lexical, semantic, or hybrid",
    )
    top_k: int = Field(
        default=5,
        description="Number of results to retrieve",
        ge=1,
        le=20,
    )
    rerank: bool = Field(
        default=True,
        description="Whether to apply reranking",
    )
    source_filter: str | None = Field(
        default=None,
        description="Filter by source type: 'faq' or 'fund'",
    )


class SourceDocument(BaseModel):
    """A source document used in the response."""
    
    id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Document text content")
    source: str = Field(..., description="Source type: 'faq' or 'fund'")
    score: float = Field(..., description="Relevance score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FundInfo(BaseModel):
    """Fund information in response."""
    
    fund_name: str = Field(..., description="Name of the fund")
    fund_house: str | None = Field(None, description="Fund house/AMC")
    category: str | None = Field(None, description="Fund category")
    cagr_1yr: float | None = Field(None, description="1-year CAGR")
    cagr_3yr: float | None = Field(None, description="3-year CAGR")
    cagr_5yr: float | None = Field(None, description="5-year CAGR")
    sharpe_ratio: float | None = Field(None, description="Sharpe ratio")
    volatility: float | None = Field(None, description="Volatility")
    risk_level: str | None = Field(None, description="Risk level")


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    
    answer: str = Field(..., description="Generated answer to the query")
    query_type: str = Field(
        default="hybrid",
        description="Detected query type: faq, numerical, or hybrid",
    )
    funds: list[FundInfo] = Field(
        default_factory=list,
        description="List of relevant funds mentioned",
    )
    sources: list[SourceDocument] = Field(
        default_factory=list,
        description="Source documents used for the answer",
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score of the response",
        ge=0.0,
        le=1.0,
    )
    search_mode: SearchMode = Field(
        ...,
        description="Search mode used",
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
