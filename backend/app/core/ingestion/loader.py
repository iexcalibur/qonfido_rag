"""Load and parse CSV data files for FAQs and fund performance."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FAQItem(BaseModel):
    """Single FAQ entry."""

    id: str
    question: str
    answer: str
    category: str | None = None
    source: str = "faq"

    @property
    def text_for_embedding(self) -> str:
        """Combine question and answer for embedding."""
        return f"Question: {self.question}\nAnswer: {self.answer}"
    
    def to_document(self) -> dict[str, Any]:
        """Convert to document format for indexing."""
        return {
            "id": self.id,
            "text": self.text_for_embedding,
            "source": self.source,
            "metadata": {
                "question": self.question,
                "answer": self.answer,
                "category": self.category,
            },
        }


class FundData(BaseModel):
    """Mutual fund performance data with metrics."""

    id: str
    fund_name: str
    fund_house: str | None = None
    category: str | None = None
    sub_category: str | None = None
    cagr_1yr: float | None = Field(None, description="1-year CAGR")
    cagr_3yr: float | None = Field(None, description="3-year CAGR")
    cagr_5yr: float | None = Field(None, description="5-year CAGR")
    volatility: float | None = Field(None, description="Standard deviation of returns")
    sharpe_ratio: float | None = Field(None, description="Sharpe ratio")
    sortino_ratio: float | None = Field(None, description="Sortino ratio")
    max_drawdown: float | None = Field(None, description="Maximum drawdown")
    beta: float | None = Field(None, description="Beta vs benchmark")
    alpha: float | None = Field(None, description="Alpha vs benchmark")
    aum: float | None = Field(None, description="Assets Under Management (Cr)")
    expense_ratio: float | None = Field(None, description="Expense ratio (%)")
    nav: float | None = Field(None, description="Current NAV")
    min_investment: float | None = Field(None, description="Minimum investment amount")
    risk_level: str | None = Field(None, description="Risk level: Low/Moderate/High")
    source: str = "fund"

    @property
    def text_for_embedding(self) -> str:
        """Convert fund data to rich text description for embedding."""
        parts = [f"Fund Name: {self.fund_name}"]

        if self.fund_house:
            parts.append(f"Fund House: {self.fund_house}")
        if self.category:
            parts.append(f"Category: {self.category}")
        if self.sub_category:
            parts.append(f"Sub-Category: {self.sub_category}")

        performance_parts = []
        if self.cagr_1yr is not None:
            performance_parts.append(f"1-year CAGR: {self.cagr_1yr:.2f}%")
        if self.cagr_3yr is not None:
            performance_parts.append(f"3-year CAGR: {self.cagr_3yr:.2f}%")
        if self.cagr_5yr is not None:
            performance_parts.append(f"5-year CAGR: {self.cagr_5yr:.2f}%")
        if performance_parts:
            parts.append(f"Performance: {', '.join(performance_parts)}")

        risk_parts = []
        if self.sharpe_ratio is not None:
            risk_parts.append(f"Sharpe Ratio: {self.sharpe_ratio:.2f}")
        if self.volatility is not None:
            risk_parts.append(f"Volatility: {self.volatility:.2f}%")
        if self.sortino_ratio is not None:
            risk_parts.append(f"Sortino Ratio: {self.sortino_ratio:.2f}")
        if self.max_drawdown is not None:
            risk_parts.append(f"Max Drawdown: {self.max_drawdown:.2f}%")
        if self.beta is not None:
            risk_parts.append(f"Beta: {self.beta:.2f}")
        if self.alpha is not None:
            risk_parts.append(f"Alpha: {self.alpha:.2f}%")
        if risk_parts:
            parts.append(f"Risk Metrics: {', '.join(risk_parts)}")

        if self.risk_level:
            parts.append(f"Risk Level: {self.risk_level}")
        if self.aum is not None:
            parts.append(f"AUM: ₹{self.aum:.2f} Cr")
        if self.expense_ratio is not None:
            parts.append(f"Expense Ratio: {self.expense_ratio:.2f}%")

        return "\n".join(parts)

    @property
    def metadata(self) -> dict[str, Any]:
        """Metadata for filtering in vector store."""
        return {
            "id": self.id,
            "fund_name": self.fund_name,
            "fund_house": self.fund_house,
            "category": self.category,
            "sub_category": self.sub_category,
            "cagr_1yr": self.cagr_1yr,
            "cagr_3yr": self.cagr_3yr,
            "cagr_5yr": self.cagr_5yr,
            "sharpe_ratio": self.sharpe_ratio,
            "volatility": self.volatility,
            "risk_level": self.risk_level,
            "aum": self.aum,
            "expense_ratio": self.expense_ratio,
        }
    
    def to_document(self) -> dict[str, Any]:
        """Convert to document format for indexing."""
        return {
            "id": self.id,
            "text": self.text_for_embedding,
            "source": self.source,
            "metadata": self.metadata,
        }


class DataLoader:
    """Load and parse CSV data files with flexible column matching."""

    def __init__(
        self, 
        data_dir: str = "data/raw", 
        faqs_file: str = "faqs.csv", 
        funds_file: str = "funds.csv"
    ):
        self.data_dir = Path(data_dir)
        self.faqs_file = faqs_file
        self.funds_file = funds_file

    def load_faqs(self, filename: str | None = None) -> list[FAQItem]:
        """Load FAQ data from CSV with flexible column matching."""
        if filename is None:
            filename = self.faqs_file
            
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.warning(f"FAQ file not found: {filepath}")
            return []

        logger.info(f"Loading FAQs from {filepath}")

        try:
            df = pd.read_csv(filepath)
            df = df.fillna("")

            faqs = []
            for idx, row in df.iterrows():
                question = self._get_column_value(row, ["question", "Question", "QUESTION", "query", "Query"])
                answer = self._get_column_value(row, ["answer", "Answer", "ANSWER", "response", "Response"])
                category = self._get_column_value(row, ["category", "Category", "CATEGORY", "topic", "Topic"])

                if question and answer:
                    faqs.append(
                        FAQItem(
                            id=f"faq_{idx}",
                            question=str(question).strip(),
                            answer=str(answer).strip(),
                            category=str(category).strip() if category else None,
                        )
                    )

            logger.info(f"Loaded {len(faqs)} FAQs")
            return faqs

        except Exception as e:
            logger.error(f"Error loading FAQs: {e}")
            raise

    def load_funds(self, filename: str | None = None) -> list[FundData]:
        """Load fund performance data from CSV with flexible column matching."""
        if filename is None:
            filename = self.funds_file
            
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.warning(f"Funds file not found: {filepath}")
            return []

        logger.info(f"Loading fund data from {filepath}")

        try:
            df = pd.read_csv(filepath)

            funds = []
            for idx, row in df.iterrows():
                fund = FundData(
                    id=f"fund_{idx}",
                    fund_name=self._get_column_value(
                        row, ["fund_name", "Fund Name", "name", "Name", "scheme_name", "Scheme Name"]
                    ) or f"Fund {idx}",
                    fund_house=self._get_column_value(
                        row, ["fund_house", "Fund House", "amc", "AMC", "fund_family"]
                    ),
                    category=self._get_column_value(
                        row, ["category", "Category", "fund_category", "type"]
                    ),
                    sub_category=self._get_column_value(
                        row, ["sub_category", "Sub Category", "subcategory"]
                    ),
                    cagr_1yr=self._get_numeric_value(
                        row, ["cagr_1yr", "cagr_1yr (%)", "1yr_cagr", "return_1yr", "1_year_return", "returns_1yr", "1yr_cagr (%)"]
                    ),
                    cagr_3yr=self._get_numeric_value(
                        row, ["cagr_3yr", "cagr_3yr (%)", "3yr_cagr", "return_3yr", "3_year_return", "returns_3yr", "3yr_cagr (%)"]
                    ),
                    cagr_5yr=self._get_numeric_value(
                        row, ["cagr_5yr", "cagr_5yr (%)", "5yr_cagr", "return_5yr", "5_year_return", "returns_5yr", "5yr_cagr (%)"]
                    ),
                    volatility=self._get_numeric_value(
                        row, ["volatility", "volatility (%)", "std_dev", "standard_deviation", "risk", "volatility %"]
                    ),
                    sharpe_ratio=self._get_numeric_value(
                        row, ["sharpe_ratio", "sharpe", "Sharpe Ratio", "sharpe_3yr"]
                    ),
                    sortino_ratio=self._get_numeric_value(
                        row, ["sortino_ratio", "sortino", "Sortino Ratio"]
                    ),
                    max_drawdown=self._get_numeric_value(
                        row, ["max_drawdown", "drawdown", "max_dd"]
                    ),
                    beta=self._get_numeric_value(row, ["beta", "Beta"]),
                    alpha=self._get_numeric_value(row, ["alpha", "Alpha"]),
                    aum=self._get_numeric_value(
                        row, ["aum", "AUM", "assets", "fund_size", "corpus"]
                    ),
                    expense_ratio=self._get_numeric_value(
                        row, ["expense_ratio", "Expense Ratio", "ter", "TER"]
                    ),
                    nav=self._get_numeric_value(row, ["nav", "NAV", "price"]),
                    min_investment=self._get_numeric_value(
                        row, ["min_investment", "minimum_investment", "min_sip"]
                    ),
                    risk_level=self._get_column_value(
                        row, ["risk_level", "Risk Level", "risk_category", "riskometer"]
                    ),
                )
                funds.append(fund)

            logger.info(f"Loaded {len(funds)} funds")
            return funds

        except Exception as e:
            logger.error(f"Error loading funds: {e}")
            raise

    def _get_column_value(self, row: pd.Series, column_names: list[str]) -> str | None:
        """Get value from row using flexible column name matching."""
        for col in column_names:
            if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
                return str(row[col]).strip()
        return None

    def _get_numeric_value(self, row: pd.Series, column_names: list[str]) -> float | None:
        """Get numeric value from row with percentage string handling."""
        for col in column_names:
            if col in row.index and pd.notna(row[col]):
                try:
                    value = row[col]
                    if isinstance(value, str):
                        value = value.replace("%", "").replace(",", "").strip()
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return None
    
    def load_all(self) -> tuple[list[FAQItem], list[FundData]]:
        """Load all FAQs and funds from CSV files."""
        faqs = self.load_faqs()
        funds = self.load_funds()
        return faqs, funds
    
    def get_all_documents(self) -> list[dict[str, Any]]:
        """Get all documents in format ready for indexing."""
        faqs, funds = self.load_all()
        
        documents = []
        documents.extend([faq.to_document() for faq in faqs])
        documents.extend([fund.to_document() for fund in funds])
        
        logger.info(f"Total documents: {len(documents)} ({len(faqs)} FAQs + {len(funds)} funds)")
        return documents
