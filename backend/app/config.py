"""
Qonfido RAG - Configuration Settings
=====================================
Centralized configuration using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend directory (parent of app/)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # Application
    # =========================================================================
    app_name: str = "Qonfido RAG"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # =========================================================================
    # API Keys
    # =========================================================================
    anthropic_api_key: SecretStr = Field(..., description="Anthropic Claude API Key")
    cohere_api_key: SecretStr | None = Field(None, description="Cohere API Key for Reranking")

    # =========================================================================
    # Embedding Model
    # =========================================================================
    embedding_model: str = Field(
        "BAAI/bge-m3",
        description="HuggingFace embedding model name",
    )
    embedding_dimension: int = Field(1024, description="Embedding vector dimension")
    embedding_batch_size: int = Field(32, description="Batch size for embedding")

    # =========================================================================
    # LLM - Claude
    # =========================================================================
    claude_model: str = Field(
        "claude-3-opus-20240229",
        description="Claude model to use. Valid models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307",
    )
    claude_max_tokens: int = Field(1024, description="Max tokens for Claude response")
    claude_temperature: float = Field(0.3, description="Temperature for Claude")

    # =========================================================================
    # Retrieval Settings
    # =========================================================================
    default_top_k: int = Field(5, description="Default number of results to retrieve")
    enable_rerank: bool = Field(True, description="Enable Cohere reranking")
    rerank_model: str = Field("rerank-english-v3.0", description="Cohere rerank model")
    rerank_top_k: int = Field(3, description="Number of results after reranking")

    # Hybrid Search
    hybrid_alpha: float = Field(
        0.5,
        description="Hybrid search weight: 0=pure lexical, 1=pure semantic",
        ge=0.0,
        le=1.0,
    )
    rrf_k: int = Field(60, description="RRF constant for rank fusion")

    # =========================================================================
    # Vector Store - ChromaDB (Simple, no server needed)
    # =========================================================================
    chroma_collection_name: str = Field("qonfido_funds", description="ChromaDB collection name")
    chroma_persist_dir: str = Field("./chroma_db", description="ChromaDB persistence directory")

    # =========================================================================
    # Data Paths
    # =========================================================================
    data_dir: str = Field("data/raw", description="Data directory containing CSV files")
    faqs_file: str = Field("faqs.csv", description="FAQs CSV filename")
    funds_file: str = Field("funds.csv", description="Fund performance CSV filename")

    # =========================================================================
    # Computed Properties
    # =========================================================================
    @property
    def faqs_path(self) -> str:
        return f"{self.data_dir}/{self.faqs_file}"

    @property
    def funds_path(self) -> str:
        return f"{self.data_dir}/{self.funds_file}"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience instance
settings = get_settings()
