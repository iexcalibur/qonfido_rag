"""
Qonfido RAG - API Schemas
==========================
Pydantic models for API requests and responses.
"""

from app.api.schemas.common import (
    HealthResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.api.schemas.fund import (
    FundCompareRequest,
    FundCompareResponse,
    FundDetail,
    FundListResponse,
    FundSummary,
)
from app.api.schemas.query import (
    ErrorResponse,
    FundInfo,
    QueryRequest,
    QueryResponse,
    SearchMode,
    SourceDocument,
)

__all__ = [
    # Common
    "HealthResponse",
    "MessageResponse",
    "PaginationParams",
    "PaginatedResponse",
    # Query
    "SearchMode",
    "QueryRequest",
    "QueryResponse",
    "SourceDocument",
    "FundInfo",
    "ErrorResponse",
    # Fund
    "FundSummary",
    "FundDetail",
    "FundListResponse",
    "FundCompareRequest",
    "FundCompareResponse",
]
