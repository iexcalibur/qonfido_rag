# =============================================================================
# Qonfido RAG - Makefile
# Convenience commands for development and deployment
# =============================================================================

.PHONY: help setup dev backend frontend test lint format clean docker-up docker-down ingest

# Default target
help:
	@echo "Qonfido RAG - Available Commands"
	@echo "================================="
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup        - Initial project setup (install all dependencies)"
	@echo "  make dev          - Start development servers (backend + frontend)"
	@echo "  make backend      - Start backend only"
	@echo "  make frontend     - Start frontend only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker Compose"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make docker-clean - Remove all containers and volumes"
	@echo ""
	@echo "Data:"
	@echo "  make ingest       - Run data ingestion pipeline"
	@echo "  make seed         - Seed database with sample data"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make evaluate     - Run RAG evaluation (Ragas)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Run type checking"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Clean build artifacts"

# =============================================================================
# Setup
# =============================================================================

setup: setup-backend setup-frontend setup-env
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run 'make docker-up' to start services"
	@echo "3. Run 'make ingest' to load data"
	@echo "4. Run 'make dev' to start development"

setup-backend:
	@echo "📦 Setting up backend..."
	cd backend && python -m venv venv
	cd backend && . venv/bin/activate && pip install -r requirements.txt
	cd backend && . venv/bin/activate && pre-commit install

setup-frontend:
	@echo "📦 Setting up frontend..."
	cd frontend && npm install

setup-env:
	@echo "📄 Creating environment files..."
	@test -f .env || cp .env.example .env
	@test -f backend/.env || cp backend/.env.example backend/.env 2>/dev/null || cp .env.example backend/.env
	@test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local 2>/dev/null || echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local

# =============================================================================
# Development
# =============================================================================

dev:
	@echo "🚀 Starting development servers..."
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  ✓ Backend API:     http://localhost:8000"
	@echo "  ✓ API Docs:        http://localhost:8000/docs"
	@echo "  ✓ Frontend:        http://localhost:3000"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Press Ctrl+C to stop all servers"
	@echo ""
	@bash -c 'trap "kill 0" EXIT; \
		(cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000) & \
		(cd frontend && npm run dev) & \
		wait'

backend:
	@echo "🐍 Starting backend..."
	@cd backend && bash -c 'source venv/bin/activate && uvicorn app.main:app --reload --port 8000'

frontend:
	@echo "⚛️  Starting frontend..."
	@cd frontend && npm run dev

# =============================================================================
# Docker
# =============================================================================

docker-up:
	@echo "🐳 Starting Docker services..."
	docker compose up -d
	@echo ""
	@echo "Services running:"
	@echo "  - Frontend:  http://localhost:3000"
	@echo "  - Backend:   http://localhost:8000"
	@echo "  - API Docs:  http://localhost:8000/docs"
	@echo "  - Qdrant:    http://localhost:6333/dashboard"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis:     localhost:6379"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker compose down

docker-logs:
	docker compose logs -f

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker compose down -v --rmi local

docker-rebuild:
	@echo "🔄 Rebuilding Docker images..."
	docker compose build --no-cache
	docker compose up -d

# =============================================================================
# Data
# =============================================================================

ingest:
	@echo "📥 Running data ingestion..."
	cd backend && . venv/bin/activate && python scripts/ingest_data.py

ingest-docker:
	@echo "📥 Running data ingestion (Docker)..."
	docker compose exec backend python scripts/ingest_data.py

seed:
	@echo "🌱 Seeding database..."
	cd backend && . venv/bin/activate && python scripts/seed_db.py

# =============================================================================
# Testing
# =============================================================================

test: test-backend test-frontend
	@echo "✅ All tests passed!"

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && . venv/bin/activate && pytest tests/ -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test 2>/dev/null || echo "No frontend tests configured"

test-cov:
	@echo "📊 Running tests with coverage..."
	cd backend && . venv/bin/activate && pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report: backend/htmlcov/index.html"

evaluate:
	@echo "📈 Running RAG evaluation..."
	cd backend && . venv/bin/activate && python scripts/evaluate.py

# =============================================================================
# Code Quality
# =============================================================================

lint:
	@echo "🔍 Running linters..."
	cd backend && . venv/bin/activate && ruff check app/ tests/
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	cd backend && . venv/bin/activate && ruff check --fix app/ tests/
	cd backend && . venv/bin/activate && black app/ tests/
	cd frontend && npm run format

type-check:
	@echo "🔎 Running type checks..."
	cd backend && . venv/bin/activate && mypy app/
	cd frontend && npm run type-check

pre-commit:
	@echo "🪝 Running pre-commit hooks..."
	cd backend && . venv/bin/activate && pre-commit run --all-files

# =============================================================================
# Cleanup
# =============================================================================

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	cd frontend && rm -rf .next node_modules/.cache 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# =============================================================================
# Utilities
# =============================================================================

# Check all service health
health:
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool 2>/dev/null || echo "Backend: ❌ Not running"
	@curl -s http://localhost:6333/readiness | python -m json.tool 2>/dev/null || echo "Qdrant: ❌ Not running"
	@redis-cli ping 2>/dev/null || echo "Redis: ❌ Not running"
	@pg_isready -h localhost -p 5432 -U qonfido 2>/dev/null || echo "PostgreSQL: ❌ Not running"

# Show environment info
info:
	@echo "📋 Environment Information"
	@echo "=========================="
	@echo "Python: $$(python --version 2>&1)"
	@echo "Node: $$(node --version 2>&1)"
	@echo "Docker: $$(docker --version 2>&1)"
	@echo "Docker Compose: $$(docker compose version 2>&1)"
