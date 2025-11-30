"""SQLModel models for database tables."""

from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel


class FundBase(SQLModel):
    """Base model for fund data."""

    fund_name: str = Field(..., index=True)
    fund_house: str | None = Field(default=None, index=True)
    category: str | None = Field(default=None, index=True)
    sub_category: str | None = None
    
    cagr_1yr: float | None = None
    cagr_3yr: float | None = None
    cagr_5yr: float | None = None
    
    volatility: float | None = None
    sharpe_ratio: float | None = None
    sortino_ratio: float | None = None
    max_drawdown: float | None = None
    beta: float | None = None
    alpha: float | None = None
    
    aum: float | None = None
    expense_ratio: float | None = None
    nav: float | None = None
    risk_level: str | None = Field(default=None, index=True)


class Fund(FundBase, table=True):
    """Fund database table."""

    __tablename__ = "funds"
    
    id: int | None = Field(default=None, primary_key=True)
    external_id: str = Field(..., unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FAQBase(SQLModel):
    """Base model for FAQ data."""

    question: str
    answer: str
    category: str | None = Field(default=None, index=True)


class FAQ(FAQBase, table=True):
    """FAQ database table."""

    __tablename__ = "faqs"
    
    id: int | None = Field(default=None, primary_key=True)
    external_id: str = Field(..., unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QueryLogBase(SQLModel):
    """Base model for query logs."""

    query: str
    search_mode: str
    query_type: str | None = None
    response_time_ms: float | None = None
    num_sources: int | None = None
    confidence: float | None = None


class QueryLog(QueryLogBase, table=True):
    """Query log database table for analytics."""

    __tablename__ = "query_logs"
    
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str | None = None
    session_id: str | None = None


class EmbeddingCache(SQLModel, table=True):
    """Cache for embeddings to avoid recomputation."""

    __tablename__ = "embedding_cache"
    
    id: int | None = Field(default=None, primary_key=True)
    text_hash: str = Field(..., unique=True, index=True)
    embedding: bytes
    model_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
