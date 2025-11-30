"""Data loading and embedding generation."""

from app.core.ingestion.embedder import Embedder, get_embedder
from app.core.ingestion.loader import DataLoader, FAQItem, FundData

__all__ = [
    "DataLoader",
    "FAQItem",
    "FundData",
    "Embedder",
    "get_embedder",
]
