# Qonfido RAG - Project Structure

```
qonfido-rag/
│
├── 📄 README.md                          # Main documentation
├── 📄 docker-compose.yml                 # One-command setup
├── 📄 .env.example                       # Environment variables template
├── 📄 .gitignore                         # Git ignore rules
├── 📄 .pre-commit-config.yaml            # Code quality hooks
├── 📄 Makefile                           # Convenience commands
│
├── 📁 backend/                           # Python FastAPI Backend
│   ├── 📄 pyproject.toml                 # Python dependencies (Poetry)
│   ├── 📄 requirements.txt               # Pip requirements (alternative)
│   ├── 📄 Dockerfile                     # Backend container
│   ├── 📄 .env.example                   # Backend env template
│   │
│   ├── 📁 app/                           # Main application
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                    # FastAPI app entry point
│   │   ├── 📄 config.py                  # Settings & configuration
│   │   │
│   │   ├── 📁 api/                       # API Layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 deps.py                # Dependency injection
│   │   │   ├── 📁 v1/                    # API version 1
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 router.py          # Main router
│   │   │   │   ├── 📄 query.py           # Query endpoints
│   │   │   │   ├── 📄 funds.py           # Fund data endpoints
│   │   │   │   └── 📄 health.py          # Health check endpoints
│   │   │   └── 📁 schemas/               # Pydantic schemas
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 query.py           # Query request/response
│   │   │       ├── 📄 fund.py            # Fund schemas
│   │   │       └── 📄 common.py          # Shared schemas
│   │   │
│   │   ├── 📁 core/                      # Core Business Logic
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📁 ingestion/             # Data Ingestion Pipeline
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 loader.py          # CSV loaders
│   │   │   │   ├── 📄 transformer.py     # Data transformation
│   │   │   │   ├── 📄 chunker.py         # Text chunking
│   │   │   │   └── 📄 embedder.py        # Embedding generation
│   │   │   │
│   │   │   ├── 📁 retrieval/             # Retrieval Layer
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 base.py            # Base retriever interface
│   │   │   │   ├── 📄 semantic.py        # Semantic search (Qdrant)
│   │   │   │   ├── 📄 lexical.py         # BM25 lexical search
│   │   │   │   ├── 📄 hybrid.py          # Hybrid search + RRF
│   │   │   │   └── 📄 reranker.py        # Cohere reranking
│   │   │   │
│   │   │   ├── 📁 generation/            # Generation Layer
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 llm.py             # Claude API wrapper
│   │   │   │   ├── 📄 prompts.py         # Prompt templates
│   │   │   │   └── 📄 structured.py      # Instructor structured output
│   │   │   │
│   │   │   └── 📁 orchestration/         # LangGraph Orchestration
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 graph.py           # Main LangGraph workflow
│   │   │       ├── 📄 nodes.py           # Graph nodes
│   │   │       ├── 📄 classifier.py      # Query classifier
│   │   │       └── 📄 state.py           # Graph state definitions
│   │   │
│   │   ├── 📁 db/                        # Database Layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 session.py             # Database session
│   │   │   ├── 📄 models.py              # SQLModel models
│   │   │   └── 📄 repositories.py        # Data access layer
│   │   │
│   │   ├── 📁 services/                  # Service Layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 vector_store.py        # Qdrant service
│   │   │   ├── 📄 cache.py               # Redis cache service
│   │   │
│   │   └── 📁 utils/                     # Utilities
│   │       ├── 📄 __init__.py
│   │       ├── 📄 logging.py             # Logging configuration
│   │       └── 📄 helpers.py             # Helper functions
│   │
│   ├── 📁 data/                          # Data Directory
│   │   ├── 📁 raw/                       # Raw CSV files
│   │   │   ├── 📄 mutual_fund_faqs.csv
│   │   │   └── 📄 fund_performance.csv
│   │   └── 📁 processed/                 # Processed data
│   │       └── 📄 .gitkeep
│   │
│   ├── 📁 scripts/                       # Utility Scripts
│   │   ├── 📄 ingest_data.py             # Data ingestion script
│   │   ├── 📄 seed_db.py                 # Database seeding
│   │   └── 📄 evaluate.py                # Ragas evaluation
│   │
│   ├── 📁 tests/                         # Backend Tests
│   │   ├── 📄 __init__.py
│   │   ├── 📄 conftest.py                # Pytest fixtures
│   │   ├── 📁 unit/                      # Unit tests
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 test_retrieval.py
│   │   │   ├── 📄 test_generation.py
│   │   │   └── 📄 test_orchestration.py
│   │   ├── 📁 integration/               # Integration tests
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 test_api.py
│   │   └── 📁 evaluation/                # RAG Evaluation
│   │       ├── 📄 __init__.py
│   │       ├── 📄 test_queries.json      # Test query set
│   │       └── 📄 test_rag_quality.py    # Ragas metrics
│   │
│   └── 📁 notebooks/                     # Jupyter Notebooks (exploration)
│       ├── 📄 01_data_exploration.ipynb
│       ├── 📄 02_embedding_analysis.ipynb
│       └── 📄 03_retrieval_comparison.ipynb
│
├── 📁 frontend/                          # Next.js Frontend
│   ├── 📄 package.json                   # Node dependencies
│   ├── 📄 package-lock.json              # Lock file
│   ├── 📄 tsconfig.json                  # TypeScript config
│   ├── 📄 tailwind.config.ts             # Tailwind config
│   ├── 📄 postcss.config.js              # PostCSS config
│   ├── 📄 next.config.js                 # Next.js config
│   ├── 📄 Dockerfile                     # Frontend container
│   ├── 📄 .env.example                   # Frontend env template
│   │
│   ├── 📁 src/
│   │   ├── 📁 app/                       # Next.js App Router
│   │   │   ├── 📄 layout.tsx             # Root layout
│   │   │   ├── 📄 page.tsx               # Home page
│   │   │   ├── 📄 globals.css            # Global styles
│   │   │   ├── 📁 chat/                  # Chat page
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📁 funds/                 # Funds explorer
│   │   │   │   ├── 📄 page.tsx           # Funds list
│   │   │   │   └── 📁 [fundId]/          # Fund detail
│   │   │   │       └── 📄 page.tsx
│   │   │   ├── 📁 compare/               # Fund comparison
│   │   │   │   └── 📄 page.tsx
│   │   │       └── 📄 page.tsx
│   │   │
│   │   ├── 📁 components/                # React Components
│   │   │   ├── 📁 ui/                    # shadcn/ui components
│   │   │   │   ├── 📄 button.tsx
│   │   │   │   ├── 📄 card.tsx
│   │   │   │   ├── 📄 input.tsx
│   │   │   │   ├── 📄 select.tsx
│   │   │   │   ├── 📄 badge.tsx
│   │   │   │   ├── 📄 dialog.tsx
│   │   │   │   ├── 📄 tabs.tsx
│   │   │   │   └── 📄 tooltip.tsx
│   │   │   │
│   │   │   ├── 📁 layout/                # Layout components
│   │   │   │   ├── 📄 Header.tsx
│   │   │   │   ├── 📄 Sidebar.tsx
│   │   │   │   ├── 📄 Footer.tsx
│   │   │   │   └── 📄 MainLayout.tsx
│   │   │   │
│   │   │   ├── 📁 chat/                  # Chat components
│   │   │   │   ├── 📄 ChatInterface.tsx  # Main chat UI
│   │   │   │   ├── 📄 MessageBubble.tsx  # Message display
│   │   │   │   ├── 📄 SourceCard.tsx     # Source citations
│   │   │   │   ├── 📄 SearchModeToggle.tsx # Lexical/Semantic/Hybrid
│   │   │   │   └── 📄 QueryInput.tsx     # Input with submit
│   │   │   │
│   │   │   ├── 📁 funds/                 # Fund components
│   │   │   │   ├── 📄 FundCard.tsx       # Fund summary card
│   │   │   │   ├── 📄 FundTable.tsx      # Funds data table
│   │   │   │   ├── 📄 FundMetrics.tsx    # CAGR, Sharpe, etc.
│   │   │   │   └── 📄 FundComparison.tsx # Side-by-side compare
│   │   │   │
│   │   │   └── 📁 charts/                # Data visualization
│   │   │       ├── 📄 PerformanceChart.tsx
│   │   │       ├── 📄 RiskReturnScatter.tsx
│   │   │       └── 📄 MetricsRadar.tsx
│   │   │
│   │   ├── 📁 lib/                       # Utility libraries
│   │   │   ├── 📄 api.ts                 # API client (axios/fetch)
│   │   │   ├── 📄 utils.ts               # Helper functions
│   │   │   └── 📄 cn.ts                  # className utility
│   │   │
│   │   ├── 📁 hooks/                     # Custom React hooks
│   │   │   ├── 📄 useQuery.ts            # TanStack Query wrapper
│   │   │   ├── 📄 useChat.ts             # Chat state management
│   │   │   └── 📄 useFunds.ts            # Funds data hook
│   │   │
│   │   ├── 📁 types/                     # TypeScript types
│   │   │   ├── 📄 api.ts                 # API response types
│   │   │   ├── 📄 fund.ts                # Fund types
│   │   │   └── 📄 chat.ts                # Chat types
│   │   │
│   │   └── 📁 providers/                 # React providers
│   │       ├── 📄 QueryProvider.tsx      # TanStack Query provider
│   │       └── 📄 ThemeProvider.tsx      # Dark/Light theme
│   │
│   └── 📁 public/                        # Static assets
│       ├── 📄 favicon.ico
│       └── 📁 images/
│           └── 📄 logo.svg
│
├── 📁 docs/                              # Documentation
│   ├── 📄 ARCHITECTURE.md                # Architecture decisions
│   ├── 📄 API.md                         # API documentation
│   ├── 📄 DEPLOYMENT.md                  # Deployment guide
│   └── 📄 EVALUATION.md                  # RAG evaluation results
│
├── 📁 infra/                             # Infrastructure configs
│   ├── 📁 docker/                        # Docker configs
│   │   ├── 📄 qdrant.conf                # Qdrant configuration
│   │   └── 📄 redis.conf                 # Redis configuration
│   └── 📁 scripts/                       # Infra scripts
│       ├── 📄 init-db.sh                 # Database initialization
│       └── 📄 wait-for-it.sh             # Service health check
│
└── 📁 evaluation/                        # Evaluation artifacts
    ├── 📄 test_queries.json              # Test query dataset
    ├── 📄 ground_truth.json              # Expected answers
    └── 📄 results/                       # Evaluation results
        └── 📄 .gitkeep
```

## Directory Purposes

### Backend (`/backend`)
- **app/api**: REST API endpoints and request/response schemas
- **app/core**: Core business logic (ingestion, retrieval, generation, orchestration)
- **app/db**: Database models and data access
- **app/services**: External service integrations (ChromaDB, Redis, Cache)
- **scripts**: CLI tools for data ingestion and evaluation
- **tests**: Comprehensive test suite

### Frontend (`/frontend`)
- **app**: Next.js 14 App Router pages
- **components**: Reusable React components (ui, layout, feature-specific)
- **lib**: Utility functions and API client
- **hooks**: Custom React hooks for data fetching
- **types**: TypeScript type definitions

### Documentation (`/docs`)
- Architecture decisions and rationale
- API documentation
- Deployment instructions
- Evaluation methodology and results

### Infrastructure (`/infra`)
- Docker configurations for services
- Shell scripts for setup and initialization
