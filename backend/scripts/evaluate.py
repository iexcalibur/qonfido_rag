#!/usr/bin/env python3
"""Evaluate RAG quality using test queries and multiple metrics."""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.schemas import SearchMode
from app.core.orchestration import get_pipeline
from app.utils import setup_logging

logger = logging.getLogger(__name__)

EVAL_QUESTIONS = [
    {
        "question": "What is a mutual fund?",
        "expected_type": "faq",
        "expected_keywords": ["investment", "pool", "diversified", "NAV", "money"],
    },
    {
        "question": "What is the difference between growth and dividend option?",
        "expected_type": "faq",
        "expected_keywords": ["growth", "dividend", "reinvest", "payout"],
    },
    {
        "question": "How do I invest in mutual funds?",
        "expected_type": "faq",
        "expected_keywords": ["invest", "SIP", "lump sum", "KYC", "account"],
    },
    {
        "question": "What is SIP and how does it work?",
        "expected_type": "faq",
        "expected_keywords": ["systematic", "investment", "plan", "regular", "monthly"],
    },
    {
        "question": "What is Sharpe ratio?",
        "expected_type": "faq",
        "expected_keywords": ["risk", "return", "adjusted", "measure", "performance"],
    },
    {
        "question": "Which funds have the highest Sharpe ratio?",
        "expected_type": "numerical",
        "should_have_funds": True,
        "expected_source": "fund",
    },
    {
        "question": "Show me top performing funds by 3-year CAGR",
        "expected_type": "numerical",
        "should_have_funds": True,
        "expected_source": "fund",
    },
    {
        "question": "What are the lowest volatility funds?",
        "expected_type": "numerical",
        "should_have_funds": True,
        "expected_source": "fund",
    },
    {
        "question": "Which large cap funds have the best returns?",
        "expected_type": "numerical",
        "should_have_funds": True,
        "expected_keywords": ["large cap"],
    },
    {
        "question": "Explain index funds and show me some good options",
        "expected_type": "hybrid",
        "expected_keywords": ["index", "fund", "track", "benchmark"],
    },
    {
        "question": "What are low risk funds with good returns?",
        "expected_type": "hybrid",
        "should_have_funds": True,
        "expected_keywords": ["risk", "return"],
    },
]


def evaluate_response(query_info: dict, response, latency_ms: float) -> dict:
    """Evaluate a single response against expected criteria."""
    result = {
        "question": query_info["question"],
        "expected_type": query_info["expected_type"],
        "detected_type": response.query_type,
        "latency_ms": round(latency_ms, 2),
        "passed": True,
        "checks": [],
        "scores": {},
    }
    
    if not response.answer or len(response.answer) < 30:
        result["passed"] = False
        result["checks"].append("FAIL: Answer too short or empty")
        result["scores"]["answer_quality"] = 0.0
    else:
        result["checks"].append(f"PASS: Answer generated ({len(response.answer)} chars)")
        result["scores"]["answer_quality"] = min(1.0, len(response.answer) / 200)
    
    if "expected_keywords" in query_info:
        answer_lower = response.answer.lower()
        keywords = query_info["expected_keywords"]
        keywords_found = sum(1 for kw in keywords if kw.lower() in answer_lower)
        keyword_ratio = keywords_found / len(keywords)
        result["scores"]["keyword_coverage"] = keyword_ratio
        
        if keyword_ratio >= 0.4:
            result["checks"].append(f"PASS: Keywords: {keywords_found}/{len(keywords)} ({keyword_ratio:.0%})")
        else:
            result["passed"] = False
            result["checks"].append(f"WARN: Keywords: {keywords_found}/{len(keywords)} ({keyword_ratio:.0%})")
    
    if query_info.get("should_have_funds"):
        if response.funds and len(response.funds) > 0:
            result["checks"].append(f"PASS: Funds returned: {len(response.funds)}")
            result["scores"]["funds_retrieved"] = 1.0
        else:
            result["passed"] = False
            result["checks"].append("FAIL: No funds returned (expected funds)")
            result["scores"]["funds_retrieved"] = 0.0
    
    if "expected_source" in query_info:
        sources = [s.source for s in response.sources] if response.sources else []
        if query_info["expected_source"] in sources:
            result["checks"].append(f"PASS: Source type: {query_info['expected_source']}")
            result["scores"]["source_match"] = 1.0
        else:
            result["checks"].append(f"WARN: Expected source '{query_info['expected_source']}' not found")
            result["scores"]["source_match"] = 0.0
    
    type_match = query_info["expected_type"] == response.query_type
    result["scores"]["type_accuracy"] = 1.0 if type_match else 0.0
    if type_match:
        result["checks"].append(f"PASS: Type match: {response.query_type}")
    else:
        result["checks"].append(f"WARN: Type mismatch: expected {query_info['expected_type']}, got {response.query_type}")
    
    result["scores"]["confidence"] = response.confidence
    if response.confidence and response.confidence > 0.3:
        result["checks"].append(f"PASS: Confidence: {response.confidence:.2f}")
    else:
        result["checks"].append(f"WARN: Low confidence: {response.confidence:.2f}")
    
    num_sources = len(response.sources) if response.sources else 0
    result["scores"]["sources_count"] = min(1.0, num_sources / 5)
    result["checks"].append(f"{'PASS' if num_sources >= 3 else 'WARN'}: Sources: {num_sources}")
    
    return result


async def run_evaluation(
    mode: str = "hybrid",
    verbose: bool = False,
    rerank: bool = True,
) -> dict:
    """Run evaluation for a specific search mode."""
    logger.info(f"\n{'='*60}")
    logger.info(f"RAG Evaluation - Mode: {mode.upper()}")
    logger.info(f"{'='*60}")

    pipeline = get_pipeline()
    pipeline.initialize()

    results = []
    total_latency = 0
    successful_queries = 0

    for i, query_info in enumerate(EVAL_QUESTIONS, 1):
        question = query_info["question"]
        
        if verbose:
            logger.info(f"\n[{i}/{len(EVAL_QUESTIONS)}] {question}")
        
        start_time = time.time()
        
        try:
            response = await pipeline.process(
                query=question,
                search_mode=SearchMode(mode),
                top_k=5,
                rerank=rerank,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            total_latency += latency_ms
            successful_queries += 1
            
            # Evaluate response
            eval_result = evaluate_response(query_info, response, latency_ms)
            results.append(eval_result)
            
            if verbose:
                status = "PASS" if eval_result["passed"] else "FAIL"
                logger.info(f"   Status: {status} ({latency_ms:.0f}ms)")
                for check in eval_result["checks"]:
                    logger.info(f"   {check}")
                logger.info(f"   Answer: {response.answer[:80]}...")
            
            # Add delay between queries to respect rate limits (e.g., Cohere trial: 10/min)
            # Sleep 7 seconds between queries when reranking to stay under 10/min limit
            if i < len(EVAL_QUESTIONS) and rerank:
                await asyncio.sleep(7)
                
        except Exception as e:
            logger.error(f"   ERROR: {e}")
            results.append({
                "question": question,
                "expected_type": query_info["expected_type"],
                "passed": False,
                "checks": [f"ERROR: {str(e)}"],
                "latency_ms": 0,
                "scores": {},
            })
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    # Calculate average latency only from successful queries
    avg_latency = total_latency / successful_queries if successful_queries > 0 else 0
    
    score_keys = ["answer_quality", "keyword_coverage", "confidence", "type_accuracy", "sources_count"]
    avg_scores = {}
    for key in score_keys:
        values = [r["scores"].get(key, 0) for r in results if "scores" in r]
        avg_scores[key] = sum(values) / len(values) if values else 0
    
    summary = {
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "total_queries": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total > 0 else 0,
        "avg_latency_ms": round(avg_latency, 2),
        "avg_scores": {k: round(v, 3) for k, v in avg_scores.items()},
        "results": results,
    }
    
    logger.info(f"\n{'='*60}")
    logger.info(f"EVALUATION SUMMARY - {mode.upper()}")
    logger.info(f"{'='*60}")
    logger.info(f"Pass Rate:      {passed}/{total} ({summary['pass_rate']*100:.1f}%)")
    logger.info(f"Avg Latency:    {avg_latency:.0f}ms")
    logger.info(f"Avg Confidence: {avg_scores.get('confidence', 0):.3f}")
    logger.info(f"Keyword Match:  {avg_scores.get('keyword_coverage', 0)*100:.1f}%")
    logger.info(f"Type Accuracy:  {avg_scores.get('type_accuracy', 0)*100:.1f}%")
    logger.info(f"{'='*60}")
    
    return summary


async def compare_modes(verbose: bool = False, rerank: bool = True) -> dict:
    """Compare all search modes."""
    modes = ["lexical", "semantic", "hybrid"]
    results = {}
    
    for mode in modes:
        results[mode] = await run_evaluation(mode=mode, verbose=verbose, rerank=rerank)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"MODE COMPARISON")
    logger.info(f"{'='*60}")
    logger.info(f"{'Mode':<12} {'Pass Rate':<12} {'Latency':<12} {'Confidence':<12}")
    logger.info(f"{'-'*48}")
    
    for mode, data in results.items():
        pass_rate = f"{data['pass_rate']*100:.1f}%"
        latency = f"{data['avg_latency_ms']:.0f}ms"
        confidence = f"{data['avg_scores'].get('confidence', 0):.3f}"
        logger.info(f"{mode:<12} {pass_rate:<12} {latency:<12} {confidence:<12}")
    
    best_mode = max(results.keys(), key=lambda m: results[m]['pass_rate'])
    logger.info(f"\nBest performing mode: {best_mode.upper()}")
    logger.info(f"{'='*60}")
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate RAG system quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.evaluate
  python -m scripts.evaluate --mode all --verbose
  python -m scripts.evaluate --mode hybrid --output results.json
        """,
    )
    parser.add_argument(
        "--mode",
        choices=["lexical", "semantic", "hybrid", "all"],
        default="hybrid",
        help="Search mode to evaluate (default: hybrid)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Save results to JSON file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each query",
    )
    parser.add_argument(
        "--no-rerank",
        action="store_true",
        help="Disable reranking to avoid rate limits (faster evaluation)",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    rerank_enabled = not args.no_rerank
    
    try:
        if args.mode == "all":
            results = asyncio.run(compare_modes(verbose=args.verbose, rerank=rerank_enabled))
        else:
            results = asyncio.run(run_evaluation(mode=args.mode, verbose=args.verbose, rerank=rerank_enabled))
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"\nResults saved to: {args.output}")
        if args.mode == "all":
            avg_pass_rate = sum(r["pass_rate"] for r in results.values()) / len(results)
            sys.exit(0 if avg_pass_rate >= 0.6 else 1)
        else:
            sys.exit(0 if results["pass_rate"] >= 0.6 else 1)
            
    except KeyboardInterrupt:
        logger.info("\nEvaluation cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()