"""Data access layer for database operations."""

import logging
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.db.models import FAQ, Fund, QueryLog

logger = logging.getLogger(__name__)


class FundRepository:
    """Repository for Fund database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, fund_data: dict[str, Any]) -> Fund:
        """Create a new fund record."""
        fund = Fund(**fund_data)
        self.session.add(fund)
        self.session.commit()
        self.session.refresh(fund)
        return fund

    def get_by_id(self, fund_id: int) -> Fund | None:
        """Get fund by internal ID."""
        return self.session.get(Fund, fund_id)

    def get_by_external_id(self, external_id: str) -> Fund | None:
        """Get fund by external ID."""
        statement = select(Fund).where(Fund.external_id == external_id)
        return self.session.exec(statement).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Fund]:
        """Get all funds with pagination."""
        statement = select(Fund).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_by_category(self, category: str) -> list[Fund]:
        """Get funds by category."""
        statement = select(Fund).where(Fund.category == category)
        return list(self.session.exec(statement).all())

    def get_by_risk_level(self, risk_level: str) -> list[Fund]:
        """Get funds by risk level."""
        statement = select(Fund).where(Fund.risk_level == risk_level)
        return list(self.session.exec(statement).all())

    def get_top_by_sharpe(self, limit: int = 10) -> list[Fund]:
        """Get top funds by Sharpe ratio."""
        statement = (
            select(Fund)
            .where(Fund.sharpe_ratio.isnot(None))
            .order_by(Fund.sharpe_ratio.desc())
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def get_top_by_cagr(self, years: int = 3, limit: int = 10) -> list[Fund]:
        """Get top funds by CAGR for specified years."""
        if years == 1:
            column = Fund.cagr_1yr
        elif years == 5:
            column = Fund.cagr_5yr
        else:
            column = Fund.cagr_3yr

        statement = (
            select(Fund)
            .where(column.isnot(None))
            .order_by(column.desc())
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def bulk_create(self, funds_data: list[dict[str, Any]]) -> list[Fund]:
        """Bulk create fund records."""
        funds = [Fund(**data) for data in funds_data]
        self.session.add_all(funds)
        self.session.commit()
        for fund in funds:
            self.session.refresh(fund)
        return funds

    def count(self) -> int:
        """Get total fund count."""
        statement = select(Fund)
        return len(list(self.session.exec(statement).all()))


class FAQRepository:
    """Repository for FAQ database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, faq_data: dict[str, Any]) -> FAQ:
        """Create a new FAQ record."""
        faq = FAQ(**faq_data)
        self.session.add(faq)
        self.session.commit()
        self.session.refresh(faq)
        return faq

    def get_by_id(self, faq_id: int) -> FAQ | None:
        """Get FAQ by internal ID."""
        return self.session.get(FAQ, faq_id)

    def get_by_external_id(self, external_id: str) -> FAQ | None:
        """Get FAQ by external ID."""
        statement = select(FAQ).where(FAQ.external_id == external_id)
        return self.session.exec(statement).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[FAQ]:
        """Get all FAQs with pagination."""
        statement = select(FAQ).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_by_category(self, category: str) -> list[FAQ]:
        """Get FAQs by category."""
        statement = select(FAQ).where(FAQ.category == category)
        return list(self.session.exec(statement).all())

    def bulk_create(self, faqs_data: list[dict[str, Any]]) -> list[FAQ]:
        """Bulk create FAQ records."""
        faqs = [FAQ(**data) for data in faqs_data]
        self.session.add_all(faqs)
        self.session.commit()
        for faq in faqs:
            self.session.refresh(faq)
        return faqs

    def count(self) -> int:
        """Get total FAQ count."""
        statement = select(FAQ)
        return len(list(self.session.exec(statement).all()))


class QueryLogRepository:
    """Repository for query log operations."""

    def __init__(self, session: Session):
        self.session = session

    def log_query(
        self,
        query: str,
        search_mode: str,
        query_type: str | None = None,
        response_time_ms: float | None = None,
        num_sources: int | None = None,
        confidence: float | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> QueryLog:
        """Log a query for analytics."""
        log = QueryLog(
            query=query,
            search_mode=search_mode,
            query_type=query_type,
            response_time_ms=response_time_ms,
            num_sources=num_sources,
            confidence=confidence,
            user_id=user_id,
            session_id=session_id,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_recent(self, limit: int = 100) -> list[QueryLog]:
        """Get recent query logs."""
        statement = (
            select(QueryLog)
            .order_by(QueryLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def get_stats(self) -> dict[str, Any]:
        """Get query statistics."""
        logs = list(self.session.exec(select(QueryLog)).all())
        
        if not logs:
            return {
                "total_queries": 0,
                "avg_response_time_ms": None,
                "avg_confidence": None,
                "search_mode_distribution": {},
                "query_type_distribution": {},
            }

        total = len(logs)
        response_times = [l.response_time_ms for l in logs if l.response_time_ms]
        confidences = [l.confidence for l in logs if l.confidence]
        
        search_modes = {}
        query_types = {}
        
        for log in logs:
            search_modes[log.search_mode] = search_modes.get(log.search_mode, 0) + 1
            if log.query_type:
                query_types[log.query_type] = query_types.get(log.query_type, 0) + 1

        return {
            "total_queries": total,
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else None,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else None,
            "search_mode_distribution": search_modes,
            "query_type_distribution": query_types,
        }
