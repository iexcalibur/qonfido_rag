"""
Qonfido RAG - Fund Schemas
===========================
Pydantic models for fund-related requests and responses.
"""

from pydantic import BaseModel, Field


class FundSummary(BaseModel):
    """Summary of a mutual fund."""
    
    id: str = Field(..., description="Fund ID")
    fund_name: str = Field(..., description="Name of the fund")
    fund_house: str | None = Field(None, description="Fund house/AMC")
    category: str | None = Field(None, description="Fund category")
    risk_level: str | None = Field(None, description="Risk level")


class FundDetail(BaseModel):
    """Detailed fund information."""
    
    id: str = Field(..., description="Fund ID")
    fund_name: str = Field(..., description="Name of the fund")
    fund_house: str | None = Field(None, description="Fund house/AMC")
    category: str | None = Field(None, description="Fund category")
    sub_category: str | None = Field(None, description="Fund sub-category")
    
    # Performance Metrics
    cagr_1yr: float | None = Field(None, description="1-year CAGR (%)")
    cagr_3yr: float | None = Field(None, description="3-year CAGR (%)")
    cagr_5yr: float | None = Field(None, description="5-year CAGR (%)")
    
    # Risk Metrics
    volatility: float | None = Field(None, description="Volatility/Std Dev (%)")
    sharpe_ratio: float | None = Field(None, description="Sharpe ratio")
    sortino_ratio: float | None = Field(None, description="Sortino ratio")
    max_drawdown: float | None = Field(None, description="Maximum drawdown (%)")
    beta: float | None = Field(None, description="Beta vs benchmark")
    alpha: float | None = Field(None, description="Alpha (%)")
    
    # Fund Details
    aum: float | None = Field(None, description="Assets Under Management (Cr)")
    expense_ratio: float | None = Field(None, description="Expense ratio (%)")
    nav: float | None = Field(None, description="Current NAV")
    risk_level: str | None = Field(None, description="Risk level")


class FundListResponse(BaseModel):
    """Response model for fund list."""
    
    funds: list[FundSummary] = Field(..., description="List of funds")
    total: int = Field(..., description="Total number of funds")


class FundCompareRequest(BaseModel):
    """Request model for fund comparison."""
    
    fund_ids: list[str] = Field(
        ...,
        description="List of fund IDs to compare",
        min_length=2,
        max_length=5,
    )


class FundCompareResponse(BaseModel):
    """Response model for fund comparison."""
    
    funds: list[FundDetail] = Field(..., description="List of funds to compare")
    comparison_summary: str | None = Field(None, description="AI-generated comparison summary")
