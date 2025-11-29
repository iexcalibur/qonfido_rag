"""
Qonfido RAG - Common Schemas
=============================
Shared Pydantic models used across the API.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")
    services: dict[str, bool] = Field(
        default_factory=dict,
        description="Status of dependent services",
    )


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str = Field(..., description="Response message")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Base paginated response."""
    
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
