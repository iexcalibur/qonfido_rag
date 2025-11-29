"""
Qonfido RAG - Database Models
==============================
SQLModel models for persistent data storage.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class QueryLog(SQLModel, table=True):
    """
    Query log model for tracking user queries and responses.
    
    Useful for analytics, debugging, and improving the RAG system.
    """

    __tablename__ = "query_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    query: str = Field(..., index=True, description="User query text")
    retrieval_mode: str = Field(
        ...,
        description="Retrieval mode used: lexical, semantic, or hybrid",
    )
    response_time_ms: Optional[float] = Field(
        None,
        description="Response time in milliseconds",
    )
    answer_length: Optional[int] = Field(
        None,
        description="Length of generated answer",
    )
    sources_count: Optional[int] = Field(
        None,
        description="Number of sources retrieved",
    )
    user_id: Optional[str] = Field(
        None,
        index=True,
        description="Optional user identifier for analytics",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Timestamp when query was executed",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "query": "What is the best mutual fund for retirement?",
                "retrieval_mode": "hybrid",
                "response_time_ms": 1234.5,
                "answer_length": 450,
                "sources_count": 5,
            }
        }


class QueryFeedback(SQLModel, table=True):
    """
    User feedback on query responses.
    
    Useful for improving the RAG system based on user satisfaction.
    """

    __tablename__ = "query_feedback"

    id: Optional[int] = Field(default=None, primary_key=True)
    query_log_id: Optional[int] = Field(
        None,
        foreign_key="query_logs.id",
        index=True,
        description="Reference to query log entry",
    )
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="User rating from 1-5",
    )
    helpful: Optional[bool] = Field(
        None,
        description="Whether the answer was helpful",
    )
    feedback_text: Optional[str] = Field(
        None,
        description="Optional text feedback from user",
    )
    user_id: Optional[str] = Field(
        None,
        index=True,
        description="Optional user identifier",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Timestamp when feedback was submitted",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "query_log_id": 1,
                "rating": 5,
                "helpful": True,
                "feedback_text": "Very helpful response!",
            }
        }
