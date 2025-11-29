"""
Qonfido RAG - Database Module
==============================
Database models, sessions, and repositories.
"""

from app.db.models import FAQ, Fund, QueryLog, EmbeddingCache
from app.db.repositories import FAQRepository, FundRepository, QueryLogRepository
from app.db.session import (
    DatabaseManager,
    get_db_manager,
    get_session,
    init_db,
)

__all__ = [
    # Models
    "Fund",
    "FAQ",
    "QueryLog",
    "EmbeddingCache",
    # Session
    "DatabaseManager",
    "get_db_manager",
    "get_session",
    "init_db",
    # Repositories
    "FundRepository",
    "FAQRepository",
    "QueryLogRepository",
]
