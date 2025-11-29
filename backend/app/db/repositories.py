"""
Qonfido RAG - Database Repositories
====================================
Repository pattern for database operations.
Provides a clean abstraction layer over database access.
"""

import datetime
from typing import Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import QueryLog, QueryFeedback


class QueryLogRepository:
    """Repository for query log operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
        """
        self.session = session

    async def create(
        self,
        query: str,
        retrieval_mode: str,
        response_time_ms: Optional[float] = None,
        answer_length: Optional[int] = None,
        sources_count: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> QueryLog:
        """
        Create a new query log entry.
        
        Args:
            query: User query text
            retrieval_mode: Retrieval mode used
            response_time_ms: Response time in milliseconds
            answer_length: Length of generated answer
            sources_count: Number of sources retrieved
            user_id: Optional user identifier
            
        Returns:
            Created QueryLog instance
        """
        log_entry = QueryLog(
            query=query,
            retrieval_mode=retrieval_mode,
            response_time_ms=response_time_ms,
            answer_length=answer_length,
            sources_count=sources_count,
            user_id=user_id,
        )
        
        self.session.add(log_entry)
        await self.session.commit()
        await self.session.refresh(log_entry)
        
        return log_entry

    async def get_by_id(self, log_id: int) -> Optional[QueryLog]:
        """
        Get query log by ID.
        
        Args:
            log_id: Query log ID
            
        Returns:
            QueryLog instance or None if not found
        """
        result = await self.session.execute(
            select(QueryLog).where(QueryLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def get_recent(
        self,
        limit: int = 100,
        user_id: Optional[str] = None,
    ) -> list[QueryLog]:
        """
        Get recent query logs.
        
        Args:
            limit: Maximum number of logs to return
            user_id: Optional filter by user ID
            
        Returns:
            List of QueryLog instances
        """
        query = select(QueryLog).order_by(desc(QueryLog.created_at)).limit(limit)
        
        if user_id:
            query = query.where(QueryLog.user_id == user_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_stats(
        self,
        days: int = 30,
        user_id: Optional[str] = None,
    ) -> dict:
        """
        Get query statistics.
        
        Args:
            days: Number of days to analyze
            user_id: Optional filter by user ID
            
        Returns:
            Dictionary with statistics
        """
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        query = select(QueryLog).where(QueryLog.created_at >= cutoff_date)
        
        if user_id:
            query = query.where(QueryLog.user_id == user_id)
        
        result = await self.session.execute(query)
        logs = list(result.scalars().all())
        
        if not logs:
            return {
                "total_queries": 0,
                "avg_response_time_ms": None,
                "retrieval_mode_distribution": {},
            }
        
        # Calculate statistics
        response_times = [log.response_time_ms for log in logs if log.response_time_ms]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else None
        )
        
        # Retrieval mode distribution
        mode_counts = {}
        for log in logs:
            mode = log.retrieval_mode
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            "total_queries": len(logs),
            "avg_response_time_ms": avg_response_time,
            "retrieval_mode_distribution": mode_counts,
            "period_days": days,
        }

    async def count(self) -> int:
        """
        Get total count of query logs.
        
        Returns:
            Total count
        """
        result = await self.session.execute(
            select(func.count(QueryLog.id))
        )
        return result.scalar_one() or 0


class QueryFeedbackRepository:
    """Repository for query feedback operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
        """
        self.session = session

    async def create(
        self,
        query_log_id: Optional[int] = None,
        rating: int = 5,
        helpful: Optional[bool] = None,
        feedback_text: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> QueryFeedback:
        """
        Create a new feedback entry.
        
        Args:
            query_log_id: Reference to query log entry
            rating: User rating from 1-5
            helpful: Whether the answer was helpful
            feedback_text: Optional text feedback
            user_id: Optional user identifier
            
        Returns:
            Created QueryFeedback instance
        """
        feedback = QueryFeedback(
            query_log_id=query_log_id,
            rating=rating,
            helpful=helpful,
            feedback_text=feedback_text,
            user_id=user_id,
        )
        
        self.session.add(feedback)
        await self.session.commit()
        await self.session.refresh(feedback)
        
        return feedback

    async def get_by_query_log_id(
        self,
        query_log_id: int,
    ) -> Optional[QueryFeedback]:
        """
        Get feedback for a specific query log.
        
        Args:
            query_log_id: Query log ID
            
        Returns:
            QueryFeedback instance or None if not found
        """
        result = await self.session.execute(
            select(QueryFeedback).where(
                QueryFeedback.query_log_id == query_log_id
            )
        )
        return result.scalar_one_or_none()

    async def get_average_rating(
        self,
        days: int = 30,
    ) -> Optional[float]:
        """
        Get average feedback rating.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Average rating or None if no feedback
        """
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        result = await self.session.execute(
            select(func.avg(QueryFeedback.rating)).where(
                QueryFeedback.created_at >= cutoff_date
            )
        )
        return result.scalar_one()
