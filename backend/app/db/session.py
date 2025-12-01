"""Database connection and session management."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./qonfido_rag.db"


class DatabaseManager:
    """Database connection manager supporting SQLite and PostgreSQL with async operations."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or DEFAULT_DATABASE_URL
        self._engine = None
        self._async_session_maker = None

    def _normalize_database_url(self, url: str) -> str:
        """Normalize database URL for async SQLAlchemy compatibility.
        """
        if url.startswith("postgresql://") and "+" not in url.split("://")[0]:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            logger.info("Converted PostgreSQL URL to asyncpg format for async operations")
        elif url.startswith("sqlite:///") and "+" not in url.split("://")[0]:
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
            logger.info("Converted SQLite URL to aiosqlite format for async operations")
        return url

    @property
    def engine(self):
        """Lazy load async database engine."""
        if self._engine is None:
            normalized_url = self._normalize_database_url(self.database_url)
            
            connect_args = {}
            if normalized_url.startswith("sqlite"):
                connect_args = {"check_same_thread": False}

            self._engine = create_async_engine(
                normalized_url,
                echo=False,
                connect_args=connect_args,
            )
            log_url = normalized_url.split("@")[-1] if "@" in normalized_url else normalized_url
            logger.info(f"Async database engine created: {log_url}")
        
        return self._engine

    @property
    def async_session_maker(self):
        """Get async session maker."""
        if self._async_session_maker is None:
            self._async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._async_session_maker

    async def create_tables(self) -> None:
        """Create all database tables asynchronously."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created")

    async def drop_tables(self) -> None:
        """Drop all database tables asynchronously."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        logger.warning("Database tables dropped")

    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for database sessions with automatic commit/rollback."""
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


_db_manager: DatabaseManager | None = None


def get_db_manager(database_url: str | None = None) -> DatabaseManager:
    """Get or create global database manager instance.
    """
    global _db_manager
    if _db_manager is None:
        url = database_url or settings.database_url or DEFAULT_DATABASE_URL
        _db_manager = DatabaseManager(url)
    return _db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI async dependency to get database sessions."""
    db = get_db_manager()
    async with db.session_scope() as session:
        yield session


async def init_db(database_url: str | None = None) -> None:
    """Initialize database and create tables asynchronously.
    """
    db = get_db_manager(database_url)
    await db.create_tables()
