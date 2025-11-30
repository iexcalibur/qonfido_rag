"""Database connection and session management."""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = "sqlite:///./qonfido_rag.db"


class DatabaseManager:
    """Database connection manager supporting SQLite and PostgreSQL."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or DEFAULT_DATABASE_URL
        self._engine = None

    @property
    def engine(self):
        """Lazy load database engine."""
        if self._engine is None:
            connect_args = {}
            if self.database_url.startswith("sqlite"):
                connect_args["check_same_thread"] = False

            self._engine = create_engine(
                self.database_url,
                echo=False,
                connect_args=connect_args,
            )
            logger.info(f"Database engine created: {self.database_url.split('@')[-1]}")
        
        return self._engine

    def create_tables(self) -> None:
        """Create all database tables."""
        SQLModel.metadata.create_all(self.engine)
        logger.info("Database tables created")

    def drop_tables(self) -> None:
        """Drop all database tables."""
        SQLModel.metadata.drop_all(self.engine)
        logger.warning("Database tables dropped")

    def get_session(self) -> Session:
        """Get a new database session."""
        return Session(self.engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic commit/rollback."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


_db_manager: DatabaseManager | None = None


def get_db_manager(database_url: str | None = None) -> DatabaseManager:
    """Get or create global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency to get database sessions."""
    db = get_db_manager()
    with db.session_scope() as session:
        yield session


def init_db(database_url: str | None = None) -> None:
    """Initialize database and create tables."""
    db = get_db_manager(database_url)
    db.create_tables()
