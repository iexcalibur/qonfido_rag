"""
Qonfido RAG - Database Module
==============================
Database configuration, models, and repositories.
"""

from app.db.models import QueryLog, QueryFeedback
from app.db.repositories import (
    QueryLogRepository,
    QueryFeedbackRepository,
)
from app.db.session import (
    get_db,
    get_db_session,
    init_db,
    create_tables,
    drop_tables,
    engine,
    AsyncSessionLocal,
)

__all__ = [
    # Models
    "QueryLog",
    "QueryFeedback",
    # Repositories
    "QueryLogRepository",
    "QueryFeedbackRepository",
    # Session management
    "get_db",
    "get_db_session",
    "init_db",
    "create_tables",
    "drop_tables",
    "engine",
    "AsyncSessionLocal",
]

