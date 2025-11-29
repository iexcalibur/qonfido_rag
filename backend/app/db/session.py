"""
Qonfido RAG - Database Session Management
==========================================
Async database session configuration using SQLModel.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlmodel import SQLModel

from app.config import settings

# Database engine
engine: AsyncEngine | None = None

# Session factory
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str | None = None) -> None:
    """
    Initialize database engine and session factory.
    
    Args:
        database_url: Optional database URL. If not provided, uses settings.
    """
    global engine, AsyncSessionLocal
    
    # Use provided URL or check if database is configured
    db_url = database_url or getattr(settings, "database_url", None)
    
    if not db_url:
        # Database is optional - ChromaDB is used for vector storage
        return
    
    # Create async engine
    engine = create_async_engine(
        db_url,
        echo=settings.debug if hasattr(settings, "debug") else False,
        future=True,
        pool_pre_ping=True,  # Verify connections before using
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def create_tables() -> None:
    """
    Create all database tables.
    
    Should be called during application startup.
    """
    if engine is None:
        return
    
    async with engine.begin() as conn:
        # Import models to register them
        from app.db.models import QueryLog  # noqa: F401
        
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_tables() -> None:
    """
    Drop all database tables.
    
    Warning: Use only in development/testing.
    """
    if engine is None:
        return
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session context manager.
    
    Usage:
        async with get_db_session() as session:
            # Use session
            pass
    """
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first or configure database_url."
        )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with get_db_session() as session:
        yield session


# Initialize on import if database_url is configured
if hasattr(settings, "database_url") and getattr(settings, "database_url", None):
    init_db()
