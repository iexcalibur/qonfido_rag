"""
Qonfido RAG - Core Module
==========================
Core business logic for the RAG system.
"""

from app.core.orchestration import RAGPipeline, get_pipeline

__all__ = [
    "RAGPipeline",
    "get_pipeline",
]
