"""
Qonfido RAG - Scripts Package
==============================
CLI utility scripts for development, data management, and evaluation.

This package contains standalone scripts that can be executed independently:
- ingest_data.py: Load CSV data, generate embeddings, and build search indexes
- seed_db.py: Seed PostgreSQL database with fund and FAQ data
- evaluate.py: Evaluate RAG quality using test queries and metrics
- test_query.py: Test individual queries against the RAG pipeline

Usage:
    python -m scripts.ingest_data
    python -m scripts.evaluate
    python -m scripts.test_query "your query here"

Or use the Makefile commands:
    make ingest      # Run data ingestion
    make seed        # Seed database
    make evaluate    # Run evaluation

Note: This __init__.py file makes the scripts folder a Python package,
allowing scripts to be run as modules (python -m scripts.script_name).
The scripts are standalone and don't need to export anything from this package.
"""
