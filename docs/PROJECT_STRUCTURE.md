# Qonfido RAG - Project Structure

Complete project structure with file descriptions and organization.

```
qonfido-rag/
│
├── 📄 README.md                          # Main project documentation
├── 📄 docker-compose.yml                 # Docker Compose configuration
├── 📄 Makefile                           # Convenience commands
├── 📄 package.json                       # Root package.json (if any)
├── 📄 .gitignore                         # Git ignore rules
│
├── 📁 backend/                           # Python FastAPI Backend
│   ├── 📄 requirements.txt               # Python dependencies
│   ├── 📄 test_backend.py                # Backend test runner
│   ├── 📄 .env.example                   # Backend environment template (if exists)
│   │
│   ├── 📁 app/                           # Main application package
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                    # FastAPI app entry point
│   │   ├── 📄 config.py                  # Settings & configuration (Pydantic)
│   │   │
│   │   ├── 📁 api/                       # REST API Layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📁 v1/                    # API version 1
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 router.py          # Main API router
│   │   │   │   ├── 📄 query.py           # RAG query endpoints
│   │   │   │   ├── 📄 funds.py           # Fund data endpoints
│   │   │   │   └── 📄 health.py          # Health check endpoints
│   │   │   └── 📁 schemas/               # Pydantic request/response schemas
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 query.py           # Query request/response models
│   │   │       ├── 📄 fund.py            # Fund-related schemas
│   │   │       └── 📄 common.py          # Shared schemas (Health, Error)
│   │   │
│   │   ├── 📁 core/                      # Core Business Logic
│   │   │   ├── 📄 __init__.py
│   │   │   │
│   │   │   ├── 📁 ingestion/             # Data Ingestion Pipeline
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 loader.py          # CSV data loading (FAQs, Funds)
│   │   │   │   └── 📄 embedder.py        # Embedding generation (BGE-M3)
│   │   │   │
│   │   │   ├── 📁 retrieval/             # Retrieval Layer
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 lexical.py         # BM25 lexical search
│   │   │   │   ├── 📄 semantic.py        # Semantic search (ChromaDB)
│   │   │   │   ├── 📄 hybrid.py          # Hybrid search with RRF fusion
│   │   │   │   └── 📄 reranker.py        # Cohere reranking (optional)
│   │   │   │
│   │   │   ├── 📁 generation/            # Generation Layer
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 llm.py             # Claude API wrapper
│   │   │   │   └── 📄 prompts.py         # Prompt templates
│   │   │   │
│   │   │   └── 📁 orchestration/         # Pipeline Orchestration
│   │   │       ├── 📄 __init__.py
│   │   │       └── 📄 pipeline.py        # Main RAG pipeline coordinator
│   │   │
│   │   ├── 📁 db/                        # Database Layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 session.py             # Database session management
│   │   │   ├── 📄 models.py              # SQLModel database models
│   │   │   └── 📄 repositories.py        # Data access layer
│   │   │
│   │   ├── 📁 services/                  # Service Layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 vector_store.py        # Vector store wrapper
│   │   │   └── 📄 cache.py               # In-memory caching service
│   │   │
│   │   └── 📁 utils/                     # Utilities
│   │       ├── 📄 __init__.py
│   │       ├── 📄 logging.py             # Logging configuration
│   │       └── 📄 helpers.py             # Helper functions
│   │
│   ├── 📁 data/                          # Data Directory
│   │   ├── 📁 raw/                       # Raw CSV files
│   │   │   ├── 📄 faqs.csv               # Mutual fund FAQs
│   │   │   └── 📄 funds.csv              # Fund performance data
│   │   └── 📁 processed/                 # Processed data (if any)
│   │
│   ├── 📁 scripts/                       # Utility Scripts
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ingest_data.py             # Data ingestion script
│   │   ├── 📄 seed_db.py                 # Database seeding
│   │   ├── 📄 evaluate.py                # RAG evaluation script
│   │   └── 📄 test_query.py              # Query testing script
│   │
│   ├── 📁 tests/                         # Backend Tests
│   │   ├── 📄 __init__.py
│   │   ├── 📁 unit/                      # Unit tests
│   │   │   └── 📄 __init__.py
│   │   ├── 📁 integration/               # Integration tests
│   │   │   └── 📄 __init__.py
│   │   └── 📁 evaluation/                # Evaluation tests
│   │       └── 📄 __init__.py
│   │
│   └── 📁 venv/                          # Virtual environment (gitignored)
│
├── 📁 frontend/                          # Next.js Frontend
│   ├── 📄 package.json                   # Node dependencies
│   ├── 📄 package-lock.json              # Lock file
│   ├── 📄 tsconfig.json                  # TypeScript configuration
│   ├── 📄 tailwind.config.ts             # Tailwind CSS configuration
│   ├── 📄 postcss.config.js              # PostCSS configuration
│   ├── 📄 next.config.js                 # Next.js configuration
│   ├── 📄 next-env.d.ts                  # Next.js TypeScript declarations
│   │
│   ├── 📁 src/
│   │   ├── 📁 app/                       # Next.js App Router
│   │   │   ├── 📄 layout.tsx             # Root layout
│   │   │   ├── 📄 page.tsx               # Home page
│   │   │   ├── 📄 globals.css            # Global styles
│   │   │   ├── 📁 chat/                  # Chat interface page
│   │   │   │   └── 📄 page.tsx
│   │   │   └── 📁 funds/                 # Fund explorer pages
│   │   │       ├── 📄 page.tsx           # Funds list page
│   │   │       └── 📁 [fundId]/          # Dynamic route for fund details
│   │   │           └── 📄 page.tsx
│   │   │
│   │   ├── 📁 components/                # React Components
│   │   │   ├── 📄 Header.tsx             # Main navigation header
│   │   │   │
│   │   │   ├── 📁 chat/                  # Chat-related components
│   │   │   │   ├── 📄 ChatInput.tsx      # Chat input with search mode
│   │   │   │   ├── 📄 ChatMessage.tsx    # Individual chat message
│   │   │   │   ├── 📄 CitationChip.tsx   # Source citation badge
│   │   │   │   ├── 📄 FundAnalysisResults.tsx  # Fund metrics grid
│   │   │   │   ├── 📄 FundInsightCard.tsx      # Individual fund card
│   │   │   │   ├── 📄 FundMetricsUtils.ts      # Metric utility functions
│   │   │   │   ├── 📄 WelcomeMessage.tsx # Welcome screen
│   │   │   │   └── 📄 index.ts           # Component exports
│   │   │   │
│   │   │   └── 📁 layout/                # Layout components
│   │   │       ├── 📄 ConditionalLayout.tsx    # Conditional layout wrapper
│   │   │       ├── 📄 Header.tsx         # Alternative header
│   │   │       └── 📄 index.ts           # Component exports
│   │   │
│   │   ├── 📁 lib/                       # Utility Libraries
│   │   │   ├── 📄 api.ts                 # API client functions
│   │   │   └── 📄 utils.ts               # Utility functions
│   │   │
│   │   ├── 📁 types/                     # TypeScript Type Definitions
│   │   │   └── 📄 index.ts               # All type definitions
│   │   │
│   │   └── 📁 hooks/                     # Custom React Hooks
│   │       └── 📄 index.ts               # Custom hooks (useChat, useFunds, etc.)
│   │
│   └── 📁 node_modules/                  # Node dependencies (gitignored)
│
├── 📁 docs/                              # Documentation
│   ├── 📄 PROJECT_STRUCTURE.md           # This file - project structure
│   ├── 📄 BACKEND_STRUCTURE.md           # Backend folder structure overview
│   ├── 📄 FRONTEND_STRUCTURE.md          # Frontend folder structure overview
│   ├── 📄 DATA_FLOW.md                   # End-to-end data flow (ASCII)
│   ├── 📄 DATA_FLOW_DIAGRAMS.md          # Visual flow diagrams (Mermaid)
│   └── 📄 DEEP_ARCHITECTURE.md           # Deep technical architecture
│
├── 📁 infra/                             # Infrastructure configs
│   ├── 📁 docker/                        # Docker configurations
│   └── 📁 scripts/                       # Infrastructure scripts
│
├── 📁 evaluation/                        # Evaluation artifacts
│   └── 📁 results/                       # Evaluation results
│
└── 📄 IMPROVEMENT_COMPARISON_ANALYSIS.md # Analysis document (if exists)
```

## Directory Purposes

### Backend (`/backend`)

#### `app/` - Main Application Package
- **`main.py`**: FastAPI application entry point, lifespan management, route registration
- **`config.py`**: Centralized configuration using Pydantic Settings, environment variables

#### `app/api/` - REST API Layer
- **`v1/`**: Version 1 API endpoints
  - `router.py`: Combines all endpoint routers
  - `query.py`: Main RAG query endpoint (`POST /api/v1/query`)
  - `funds.py`: Fund explorer endpoints (`GET /api/v1/funds`, `/funds/{id}`)
  - `health.py`: Health check endpoint
- **`schemas/`**: Pydantic request/response models for type validation

#### `app/core/` - Core Business Logic
- **`ingestion/`**: Data loading and processing
  - `loader.py`: CSV loading, flexible column matching, data models (FAQItem, FundData)
  - `embedder.py`: Embedding generation using BGE-M3, batch processing, caching
- **`retrieval/`**: Search implementations
  - `lexical.py`: BM25 keyword-based search
  - `semantic.py`: ChromaDB vector similarity search
  - `hybrid.py`: Hybrid search with RRF fusion and parallel execution
  - `reranker.py`: Cohere reranking API integration (optional)
- **`generation/`**: LLM response generation
  - `llm.py`: Claude API integration
  - `prompts.py`: Prompt templates for different query types
- **`orchestration/`**: RAG pipeline coordination
  - `pipeline.py`: Main RAGPipeline class, end-to-end query processing

#### `app/db/` - Database Layer
- SQLModel ORM models and database session management
- Data access layer (repositories)

#### `app/services/` - External Services
- `vector_store.py`: Vector store wrapper (ChromaDB)
- `cache.py`: In-memory caching service (embedding cache, query cache)

#### `app/utils/` - Utilities
- Logging configuration and helper functions

#### `data/` - Data Files
- `raw/`: CSV files (faqs.csv, funds.csv)
- `processed/`: Processed data directory (if any)

#### `scripts/` - Utility Scripts
- `ingest_data.py`: Data ingestion and indexing
- `seed_db.py`: Database seeding
- `evaluate.py`: RAG evaluation and metrics
- `test_query.py`: Query testing tool

#### `tests/` - Test Suite
- `unit/`: Unit tests
- `integration/`: Integration tests
- `evaluation/`: Evaluation tests

---

### Frontend (`/frontend`)

#### `src/app/` - Next.js App Router
- File-based routing with pages for homepage, chat, and fund explorer
- Dynamic routes for fund details (`[fundId]`)

#### `src/components/` - React Components
- **`chat/`**: Chat interface components (input, messages, citations, fund results)
- **`layout/`**: Layout and navigation components
- **`Header.tsx`**: Main navigation header

#### `src/lib/` - Utility Libraries
- `api.ts`: API client functions for backend communication
- `utils.ts`: Helper functions

#### `src/types/` - TypeScript Types
- Type definitions matching backend schemas

#### `src/hooks/` - Custom React Hooks
- Reusable hooks for chat state, fund data, etc.

---

### Documentation (`/docs`)

- **`PROJECT_STRUCTURE.md`**: This file - complete project structure
- **`BACKEND_STRUCTURE.md`**: Backend folder organization and purposes
- **`FRONTEND_STRUCTURE.md`**: Frontend folder organization and purposes
- **`DATA_FLOW.md`**: ASCII-based end-to-end data flow diagrams
- **`DATA_FLOW_DIAGRAMS.md`**: Visual Mermaid diagrams for data flow
- **`DEEP_ARCHITECTURE.md`**: Detailed technical architecture documentation
- **`BACKEND_DOCUMENTATION.md`**: Comprehensive backend file documentation
- **`FRONTEND_DOCUMENTATION.md`**: Comprehensive frontend file documentation

---

### Infrastructure (`/infra`)

- Docker configurations
- Infrastructure setup scripts

---

### Evaluation (`/evaluation`)

- Evaluation results and metrics
- Test query datasets

---

## Key Files Reference

### Backend Entry Points
- **`backend/app/main.py`**: FastAPI application, startup/shutdown lifecycle
- **`backend/scripts/ingest_data.py`**: Data ingestion script
- **`backend/scripts/evaluate.py`**: RAG evaluation script

### Frontend Entry Points
- **`frontend/src/app/layout.tsx`**: Root layout component
- **`frontend/src/app/page.tsx`**: Homepage
- **`frontend/src/app/chat/page.tsx`**: Chat interface

### Configuration Files
- **`backend/requirements.txt`**: Python dependencies
- **`backend/app/config.py`**: Application configuration
- **`frontend/package.json`**: Node.js dependencies
- **`docker-compose.yml`**: Docker Compose setup

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Embeddings**: BGE-M3 (sentence-transformers)
- **Vector Store**: ChromaDB (in-process)
- **Lexical Search**: BM25 (rank-bm25)
- **LLM**: Claude API (Anthropic)
- **Reranking**: Cohere API (optional)
- **Database**: SQLite (SQLModel ORM)
- **Cache**: In-memory (TTL-based)

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components + Radix UI primitives
- **State Management**: React Query (TanStack Query)

---

For detailed information on each component, see:
- [Backend Structure](BACKEND_STRUCTURE.md)
- [Frontend Structure](FRONTEND_STRUCTURE.md)
- [Deep Architecture](DEEP_ARCHITECTURE.md)
- [Data Flow](DATA_FLOW.md)
