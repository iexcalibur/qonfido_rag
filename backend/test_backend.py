#!/usr/bin/env python3
"""
Qonfido RAG - Backend Test Script
==================================
Comprehensive test script to verify backend setup and configuration.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing Python imports...")
    
    try:
        import fastapi
        print("  ✓ FastAPI")
    except ImportError as e:
        print(f"  ✗ FastAPI: {e}")
        return False
    
    try:
        import pydantic
        print("  ✓ Pydantic")
    except ImportError as e:
        print(f"  ✗ Pydantic: {e}")
        return False
    
    try:
        from app.config import Settings
        print("  ✓ App Config")
    except ImportError as e:
        print(f"  ✗ App Config: {e}")
        return False
    
    try:
        from app.main import app
        print("  ✓ FastAPI App")
    except ImportError as e:
        print(f"  ✗ FastAPI App: {e}")
        return False
    
    return True


def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    
    try:
        from app.config import Settings
        
        # Try to load settings
        settings = Settings()
        print(f"  ✓ Environment: {settings.environment}")
        print(f"  ✓ Log Level: {settings.log_level}")
        print(f"  ✓ Embedding Model: {settings.embedding_model}")
        print(f"  ✓ Claude Model: {settings.claude_model}")
        
        # Check API keys
        anthropic_key = settings.anthropic_api_key.get_secret_value()
        if not anthropic_key or anthropic_key.startswith("sk-ant-your") or anthropic_key.startswith("your-key"):
            print("  ⚠ ANTHROPIC_API_KEY not properly set")
            return False
        else:
            print("  ✓ ANTHROPIC_API_KEY is set")
        
        cohere_key = settings.cohere_api_key.get_secret_value() if settings.cohere_api_key else None
        if cohere_key and not cohere_key.startswith("your"):
            print("  ✓ COHERE_API_KEY is set")
        else:
            print("  ⚠ COHERE_API_KEY not set (optional, reranking disabled)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def test_data_files():
    """Test if data files exist."""
    print("\n🔍 Testing data files...")
    
    try:
        from app.config import settings
        
        # Check FAQs file
        faqs_path = Path(settings.faqs_path)
        if faqs_path.exists():
            print(f"  ✓ FAQs file exists: {faqs_path}")
        else:
            print(f"  ✗ FAQs file missing: {faqs_path}")
            # Check if alternative exists
            alt_path = Path("data/raw/faqs.csv")
            if alt_path.exists():
                print(f"  ⚠ Found alternative: {alt_path}")
            return False
        
        # Check funds file
        funds_path = Path(settings.funds_path)
        if funds_path.exists():
            print(f"  ✓ Funds file exists: {funds_path}")
        else:
            print(f"  ✗ Funds file missing: {funds_path}")
            # Check if alternative exists
            alt_path = Path("data/raw/funds.csv")
            if alt_path.exists():
                print(f"  ⚠ Found alternative: {alt_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Data file check error: {e}")
        return False


def test_fastapi_app():
    """Test if FastAPI app can be created."""
    print("\n🔍 Testing FastAPI application...")
    
    try:
        from app.main import app
        print(f"  ✓ App title: {app.title}")
        print(f"  ✓ App version: {app.version}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"  ✓ Routes found: {len(routes)}")
        
        # Check for key routes
        key_routes = ["/", "/api/v1/health", "/api/v1/query", "/docs"]
        for route in key_routes:
            if route in routes:
                print(f"  ✓ Route exists: {route}")
            else:
                print(f"  ⚠ Route missing: {route}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FastAPI app error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test database connection."""
    print("\n🔍 Testing database...")
    
    try:
        from app.db.session import DatabaseManager
        
        db_manager = DatabaseManager()
        print(f"  ✓ Database URL: {db_manager.database_url.split('@')[-1] if '@' in db_manager.database_url else db_manager.database_url}")
        
        # Try to create engine
        engine = db_manager.engine
        print("  ✓ Database engine created")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Qonfido RAG - Backend Setup Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Data Files", test_data_files()))
    results.append(("FastAPI App", test_fastapi_app()))
    results.append(("Database", test_database()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Backend is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

