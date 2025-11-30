#!/usr/bin/env python3
"""Seed the database with fund and FAQ data from CSV files."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ingestion import DataLoader
from app.db import (
    FAQ,
    Fund,
    FAQRepository,
    FundRepository,
    get_db_manager,
    init_db,
)
from app.utils import setup_logging

logger = logging.getLogger(__name__)


def seed_database(
    data_dir: str = "data/raw",
    clear_existing: bool = False,
) -> dict:
    """Seed the database with data from CSV files."""
    stats = {"faqs_seeded": 0, "funds_seeded": 0}

    logger.info("Initializing database...")
    db = get_db_manager()
    
    if clear_existing:
        logger.warning("Dropping existing tables...")
        db.drop_tables()
    
    db.create_tables()
    logger.info("Database tables ready")

    logger.info(f"Loading data from {data_dir}...")
    loader = DataLoader(data_dir)
    
    try:
        faqs, funds = loader.load_all()
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return stats

    if faqs:
        logger.info(f"Seeding {len(faqs)} FAQs...")
        with db.session_scope() as session:
            repo = FAQRepository(session)
            
            for faq in faqs:
                try:
                    repo.create({
                        "external_id": faq.id,
                        "question": faq.question,
                        "answer": faq.answer,
                        "category": faq.category,
                    })
                    stats["faqs_seeded"] += 1
                except Exception as e:
                    logger.warning(f"Failed to seed FAQ {faq.id}: {e}")
        
        logger.info(f"Seeded {stats['faqs_seeded']} FAQs")

    if funds:
        logger.info(f"Seeding {len(funds)} funds...")
        with db.session_scope() as session:
            repo = FundRepository(session)
            
            for fund in funds:
                try:
                    repo.create({
                        "external_id": fund.id,
                        "fund_name": fund.fund_name,
                        "fund_house": fund.fund_house,
                        "category": fund.category,
                        "sub_category": fund.sub_category,
                        "cagr_1yr": fund.cagr_1yr,
                        "cagr_3yr": fund.cagr_3yr,
                        "cagr_5yr": fund.cagr_5yr,
                        "volatility": fund.volatility,
                        "sharpe_ratio": fund.sharpe_ratio,
                        "sortino_ratio": fund.sortino_ratio,
                        "max_drawdown": fund.max_drawdown,
                        "beta": fund.beta,
                        "alpha": fund.alpha,
                        "aum": fund.aum,
                        "expense_ratio": fund.expense_ratio,
                        "nav": fund.nav,
                        "risk_level": fund.risk_level,
                    })
                    stats["funds_seeded"] += 1
                except Exception as e:
                    logger.warning(f"Failed to seed fund {fund.id}: {e}")
        
        logger.info(f"Seeded {stats['funds_seeded']} funds")

    logger.info("=" * 40)
    logger.info("DATABASE SEEDING COMPLETE")
    logger.info(f"  FAQs:  {stats['faqs_seeded']}")
    logger.info(f"  Funds: {stats['funds_seeded']}")
    logger.info("=" * 40)

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed the database with CSV data",
    )
    parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Directory containing CSV files",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    setup_logging("DEBUG" if args.verbose else "INFO")

    try:
        seed_database(
            data_dir=args.data_dir,
            clear_existing=args.clear,
        )
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
