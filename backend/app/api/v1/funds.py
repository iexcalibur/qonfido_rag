"""Endpoints for fund data retrieval and comparison."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.api.schemas import (
    FundCompareRequest,
    FundCompareResponse,
    FundDetail,
    FundListResponse,
    FundSummary,
)
from app.config import settings
from app.core.ingestion.loader import DataLoader

router = APIRouter(tags=["Funds"])
logger = logging.getLogger(__name__)

_loader: DataLoader | None = None
_funds_cache: list | None = None


def get_funds():
    """Get cached funds data, loading from CSV if not cached."""
    global _loader, _funds_cache
    if _funds_cache is None:
        _loader = DataLoader(
            data_dir=settings.data_dir,
            faqs_file=settings.faqs_file,
            funds_file=settings.funds_file,
        )
        _funds_cache = _loader.load_funds()
        logger.info(f"Loaded {len(_funds_cache)} funds into cache")
    return _funds_cache


def clear_funds_cache():
    """Clear the funds cache to force reload on next request."""
    global _funds_cache
    _funds_cache = None
    logger.info("Funds cache cleared")


@router.get("/funds", response_model=FundListResponse)
async def list_funds(
    category: str | None = Query(None, description="Filter by category"),
    risk_level: str | None = Query(None, description="Filter by risk level"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
) -> FundListResponse:
    """List funds with optional filtering by category or risk level."""
    try:
        funds = get_funds()
        
        # Apply filters
        filtered = funds
        if category:
            filtered = [f for f in filtered if f.category and category.lower() in f.category.lower()]
        if risk_level:
            filtered = [f for f in filtered if f.risk_level and risk_level.lower() in f.risk_level.lower()]
        
        # Convert to response model with metrics
        fund_summaries = [
            FundSummary(
                id=f.id,
                fund_name=f.fund_name,
                fund_house=f.fund_house,
                category=f.category,
                risk_level=f.risk_level,
                cagr_1yr=f.cagr_1yr,
                cagr_3yr=f.cagr_3yr,
                cagr_5yr=f.cagr_5yr,
                sharpe_ratio=f.sharpe_ratio,
                volatility=f.volatility,
            )
            for f in filtered[:limit]
        ]
        
        return FundListResponse(
            funds=fund_summaries,
            total=len(filtered),
        )
        
    except Exception as e:
        logger.error(f"Error listing funds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve funds: {str(e)}")


@router.get("/funds/{fund_id}", response_model=FundDetail)
async def get_fund(fund_id: str) -> FundDetail:
    """Get detailed information for a specific fund including all metrics."""
    try:
        funds = get_funds()
        
        # Find fund by ID
        fund = next((f for f in funds if f.id == fund_id), None)
        
        if not fund:
            raise HTTPException(status_code=404, detail=f"Fund not found: {fund_id}")
        
        return FundDetail(
            id=fund.id,
            fund_name=fund.fund_name,
            fund_house=fund.fund_house,
            category=fund.category,
            sub_category=fund.sub_category,
            cagr_1yr=fund.cagr_1yr,
            cagr_3yr=fund.cagr_3yr,
            cagr_5yr=fund.cagr_5yr,
            volatility=fund.volatility,
            sharpe_ratio=fund.sharpe_ratio,
            sortino_ratio=fund.sortino_ratio,
            max_drawdown=fund.max_drawdown,
            beta=fund.beta,
            alpha=fund.alpha,
            aum=fund.aum,
            expense_ratio=fund.expense_ratio,
            nav=fund.nav,
            risk_level=fund.risk_level,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting fund {fund_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve fund: {str(e)}")


@router.post("/funds/compare", response_model=FundCompareResponse)
async def compare_funds(request: FundCompareRequest) -> FundCompareResponse:
    """Compare 2-5 funds side by side with detailed metrics."""
    try:
        funds = get_funds()
        
        # Find requested funds
        fund_details = []
        for fund_id in request.fund_ids:
            fund = next((f for f in funds if f.id == fund_id), None)
            if fund:
                fund_details.append(
                    FundDetail(
                        id=fund.id,
                        fund_name=fund.fund_name,
                        fund_house=fund.fund_house,
                        category=fund.category,
                        sub_category=fund.sub_category,
                        cagr_1yr=fund.cagr_1yr,
                        cagr_3yr=fund.cagr_3yr,
                        cagr_5yr=fund.cagr_5yr,
                        volatility=fund.volatility,
                        sharpe_ratio=fund.sharpe_ratio,
                        sortino_ratio=fund.sortino_ratio,
                        max_drawdown=fund.max_drawdown,
                        beta=fund.beta,
                        alpha=fund.alpha,
                        aum=fund.aum,
                        expense_ratio=fund.expense_ratio,
                        nav=fund.nav,
                        risk_level=fund.risk_level,
                    )
                )
        
        if len(fund_details) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 valid fund IDs required for comparison"
            )
        
        return FundCompareResponse(
            funds=fund_details,
            comparison_summary=None,  # Can be generated by LLM
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing funds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare funds: {str(e)}")


@router.get("/funds/summary/metrics")
async def get_fund_metrics_summary() -> dict:
    """Get summary statistics (min/max/avg) for all fund metrics."""
    try:
        funds = get_funds()
        
        if not funds:
            return {
                "total_funds": 0,
                "metrics": {},
                "categories": [],
                "risk_levels": [],
            }
        
        # Calculate summary statistics
        sharpe_ratios = [f.sharpe_ratio for f in funds if f.sharpe_ratio is not None]
        cagr_3yr = [f.cagr_3yr for f in funds if f.cagr_3yr is not None]
        volatilities = [f.volatility for f in funds if f.volatility is not None]
        
        return {
            "total_funds": len(funds),
            "metrics": {
                "sharpe_ratio": {
                    "min": min(sharpe_ratios) if sharpe_ratios else None,
                    "max": max(sharpe_ratios) if sharpe_ratios else None,
                    "avg": sum(sharpe_ratios) / len(sharpe_ratios) if sharpe_ratios else None,
                },
                "cagr_3yr": {
                    "min": min(cagr_3yr) if cagr_3yr else None,
                    "max": max(cagr_3yr) if cagr_3yr else None,
                    "avg": sum(cagr_3yr) / len(cagr_3yr) if cagr_3yr else None,
                },
                "volatility": {
                    "min": min(volatilities) if volatilities else None,
                    "max": max(volatilities) if volatilities else None,
                    "avg": sum(volatilities) / len(volatilities) if volatilities else None,
                },
            },
            "categories": list(set(f.category for f in funds if f.category)),
            "risk_levels": list(set(f.risk_level for f in funds if f.risk_level)),
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")
