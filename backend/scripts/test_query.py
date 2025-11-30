#!/usr/bin/env python3
"""Quick test script to run queries against the RAG system."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.schemas import SearchMode
from app.core.orchestration import get_pipeline
from app.utils import setup_logging

logger = logging.getLogger(__name__)


async def run_query(
    query: str,
    search_mode: str = "hybrid",
    top_k: int = 5,
    rerank: bool = True,
) -> None:
    """Run a query and print results."""
    
    print("\n" + "=" * 60)
    print(f"QUERY: {query}")
    print(f"MODE:  {search_mode} | TOP_K: {top_k} | RERANK: {rerank}")
    print("=" * 60)

    pipeline = get_pipeline()
    pipeline.initialize()

    response = await pipeline.process(
        query=query,
        search_mode=SearchMode(search_mode),
        top_k=top_k,
        rerank=rerank,
    )

    print("\nANSWER:")
    print("-" * 40)
    print(response.answer)

    print("\nMETADATA:")
    print(f"  Query Type:  {response.query_type}")
    print(f"  Confidence:  {response.confidence:.2f}")
    print(f"  Search Mode: {response.search_mode.value}")

    if response.sources:
        print(f"\nSOURCES ({len(response.sources)}):")
        print("-" * 40)
        for i, src in enumerate(response.sources, 1):
            print(f"  [{i}] ({src.source.upper()}) {src.id}")
            print(f"      Score: {src.score:.4f}")
            print(f"      Text: {src.text[:100]}...")

    if response.funds:
        print(f"\nFUNDS ({len(response.funds)}):")
        print("-" * 40)
        for fund in response.funds:
            parts = [fund.fund_name]
            if fund.sharpe_ratio:
                parts.append(f"Sharpe: {fund.sharpe_ratio:.2f}")
            if fund.cagr_3yr:
                parts.append(f"3Y CAGR: {fund.cagr_3yr:.2f}%")
            print(f"  - {' | '.join(parts)}")

    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test RAG queries",
    )
    parser.add_argument(
        "query",
        help="Query to run",
    )
    parser.add_argument(
        "--mode", "-m",
        default="hybrid",
        choices=["hybrid", "lexical", "semantic"],
        help="Search mode (default: hybrid)",
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="Number of results (default: 5)",
    )
    parser.add_argument(
        "--no-rerank",
        action="store_true",
        help="Disable reranking",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Suppress logs unless verbose
    if not args.verbose:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        setup_logging("DEBUG")

    try:
        asyncio.run(run_query(
            query=args.query,
            search_mode=args.mode,
            top_k=args.top_k,
            rerank=not args.no_rerank,
        ))
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
