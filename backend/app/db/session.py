"""
Qonfido RAG - Database Session
===============================
Database connection and session management.
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)

# Default to SQLite for simplicity (no server needed)
DEFAULT_DATABASE_URL = "sqlite:///./qonfido_rag.db"


class DatabaseManager:
    """
    Database connection manager.
    
    Supports:
    - SQLite (default, no setup needed)
    - PostgreSQL (for production)
    """

    def __init__(self, database_url: str | None = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection string.
                         SQLite: sqlite:///./database.db
                         PostgreSQL: postgresql://user:pass@host:port/db
        """
        self.database_url = database_url or DEFAULT_DATABASE_URL
        self._engine = None

    @property
    def engine(self):
        """Lazy load database engine."""
        if self._engine is None:
            # SQLite specific settings
            connect_args = {}
            if self.database_url.startswith("sqlite"):
                connect_args["check_same_thread"] = False

            self._engine = create_engine(
                self.database_url,
                echo=False,  # Set True for SQL debugging
                connect_args=connect_args,
            )
            logger.info(f"Database engine created: {self.database_url.split('@')[-1]}")
        
        return self._engine

    def create_tables(self) -> None:
        """Create all database tables."""
        SQLModel.metadata.create_all(self.engine)
        logger.info("Database tables created")

    def drop_tables(self) -> None:
        """Drop all database tables (use with caution!)."""
        SQLModel.metadata.drop_all(self.engine)
        logger.warning("Database tables dropped")

    def get_session(self) -> Session:
        """Get a new database session."""
        return Session(self.engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        
        Usage:
            with db.session_scope() as session:
                session.add(obj)
                session.commit()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# =============================================================================
# Global Instance
# =============================================================================

_db_manager: DatabaseManager | None = None


def get_db_manager(database_url: str | None = None) -> DatabaseManager:
    """Get or create the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database sessions.
    
    Usage in endpoints:
        @router.get("/items")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    db = get_db_manager()
    with db.session_scope() as session:
        yield session


def init_db(database_url: str | None = None) -> None:
    """Initialize database and create tables."""
    db = get_db_manager(database_url)
    db.create_tables()
