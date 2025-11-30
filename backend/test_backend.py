#!/usr/bin/env python3
"""Comprehensive test script to verify backend setup and configuration."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing Python imports...")
    
    try:
        import fastapi
        print("  PASS: FastAPI")
    except ImportError as e:
        print(f"  FAIL: FastAPI: {e}")
        return False
    
    try:
        import pydantic
        print("  PASS: Pydantic")
    except ImportError as e:
        print(f"  FAIL: Pydantic: {e}")
        return False
    
    try:
        from app.config import Settings
        print("  PASS: App Config")
    except ImportError as e:
        print(f"  FAIL: App Config: {e}")
        return False
    
    try:
        from app.main import app
        print("  PASS: FastAPI App")
    except ImportError as e:
        print(f"  FAIL: FastAPI App: {e}")
        return False
    
    return True


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from app.config import Settings
        
        settings = Settings()
        print(f"  PASS: Environment: {settings.environment}")
        print(f"  PASS: Log Level: {settings.log_level}")
        print(f"  PASS: Embedding Model: {settings.embedding_model}")
        print(f"  PASS: Claude Model: {settings.claude_model}")
        
        anthropic_key = settings.anthropic_api_key.get_secret_value()
        if not anthropic_key or anthropic_key.startswith("sk-ant-your") or anthropic_key.startswith("your-key"):
            print("  WARN: ANTHROPIC_API_KEY not properly set")
            return False
        else:
            print("  PASS: ANTHROPIC_API_KEY is set")
        
        cohere_key = settings.cohere_api_key.get_secret_value() if settings.cohere_api_key else None
        if cohere_key and not cohere_key.startswith("your"):
            print("  PASS: COHERE_API_KEY is set")
        else:
            print("  WARN: COHERE_API_KEY not set (optional, reranking disabled)")
        
        return True
        
    except Exception as e:
        print(f"  FAIL: Configuration error: {e}")
        return False


def test_data_files():
    """Test if data files exist."""
    print("\nTesting data files...")
    
    try:
        from app.config import settings
        
        faqs_path = Path(settings.faqs_path)
        if faqs_path.exists():
            print(f"  PASS: FAQs file exists: {faqs_path}")
        else:
            print(f"  FAIL: FAQs file missing: {faqs_path}")
            alt_path = Path("data/raw/faqs.csv")
            if alt_path.exists():
                print(f"  WARN: Found alternative: {alt_path}")
            return False
        
        funds_path = Path(settings.funds_path)
        if funds_path.exists():
            print(f"  PASS: Funds file exists: {funds_path}")
        else:
            print(f"  FAIL: Funds file missing: {funds_path}")
            alt_path = Path("data/raw/funds.csv")
            if alt_path.exists():
                print(f"  WARN: Found alternative: {alt_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  FAIL: Data file check error: {e}")
        return False


def test_fastapi_app():
    """Test if FastAPI app can be created."""
    print("\nTesting FastAPI application...")
    
    try:
        from app.main import app
        print(f"  PASS: App title: {app.title}")
        print(f"  PASS: App version: {app.version}")
        
        routes = [route.path for route in app.routes]
        print(f"  PASS: Routes found: {len(routes)}")
        
        key_routes = ["/", "/api/v1/health", "/api/v1/query", "/docs"]
        for route in key_routes:
            if route in routes:
                print(f"  PASS: Route exists: {route}")
            else:
                print(f"  WARN: Route missing: {route}")
        
        return True
        
    except Exception as e:
        print(f"  FAIL: FastAPI app error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test database connection."""
    print("\nTesting database...")
    
    try:
        from app.db.session import DatabaseManager
        
        db_manager = DatabaseManager()
        print(f"  PASS: Database URL: {db_manager.database_url.split('@')[-1] if '@' in db_manager.database_url else db_manager.database_url}")
        
        engine = db_manager.engine
        print("  PASS: Database engine created")
        
        return True
        
    except Exception as e:
        print(f"  FAIL: Database error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Qonfido RAG - Backend Setup Test")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Data Files", test_data_files()))
    results.append(("FastAPI App", test_fastapi_app()))
    results.append(("Database", test_database()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! Backend is ready.")
        return 0
    else:
        print("\nSome tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

