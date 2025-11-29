# Qonfido RAG - Architecture to Folder Mapping

```
Architecture Diagram                 →  Folder Structure
═══════════════════════════════════════════════════════════════════════════════

🖥️ FRONTEND LAYER (Next.js 14 Dashboard)
├── Next.js 14                       →  frontend/src/app/
├── TypeScript                       →  frontend/tsconfig.json
├── Tailwind CSS                     →  frontend/tailwind.config.ts
├── shadcn/ui                        →  frontend/src/components/ui/
├── TanStack Query                   →  frontend/src/providers/
└── Tremor/Recharts                  →  frontend/src/components/charts/

⚡ API GATEWAY (FastAPI Backend)
├── FastAPI                          →  backend/app/api/v1/
├── Pydantic v2                      →  backend/app/api/schemas/
├── SQLModel                         →  backend/app/db/
└── Redis                            →  backend/app/services/

🔀 ORCHESTRATION LAYER (Query Intelligence)
├── LangGraph                        →  backend/app/core/orchestration/
├── Query Classifier                 →  backend/app/core/orchestration/
└── Intent Detection                 →  backend/app/core/orchestration/

🔍 RETRIEVAL LAYER (Hybrid Search Engine)
├── BGE-M3                           →  backend/app/core/ingestion/
├── Qdrant                           →  backend/app/core/retrieval/
├── BM25                             →  backend/app/core/retrieval/
├── Cohere Rerank                    →  backend/app/core/retrieval/
└── RRF (Reciprocal Rank Fusion)     →  backend/app/core/retrieval/

🧠 GENERATION LAYER (LLM Response)
├── Claude API                       →  backend/app/core/generation/
├── Instructor                       →  backend/app/core/generation/
└── Prompt Templates                 →  backend/app/core/generation/

📂 DATA LAYER (CSV Files & Storage)
├── Raw CSV Files                    →  backend/data/raw/
│   ├── mutual_fund_faqs.csv
│   └── fund_performance.csv
├── Processed Data                   →  backend/data/processed/
├── PostgreSQL                       →  backend/app/db/
├── Qdrant                           →  backend/app/services/
└── Redis                            →  backend/app/services/

👁️ OBSERVABILITY LAYER (Monitoring & Evaluation)
├── Ragas                            →  backend/tests/evaluation/
└── Pytest                           →  backend/tests/

🐳 INFRASTRUCTURE (Deployment & DevOps)
├── Docker Compose                   →  docker-compose.yml
├── Pre-commit hooks                 →  .pre-commit-config.yaml
└── GitHub Actions                   →  .github/workflows/

═══════════════════════════════════════════════════════════════════════════════
```

## Complete Folder Tree

```
qonfido-rag/
│
├── 📄 README.md
├── 📄 docker-compose.yml
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 .pre-commit-config.yaml
├── 📄 Makefile
├── 📄 PROJECT_STRUCTURE.md
├── 📄 VERSION_COMPATIBILITY.md
├── 📄 ARCHITECTURE_MAPPING.md          ← This file
│
├── 📁 backend/
│   ├── 📄 requirements.txt
│   ├── 📄 Dockerfile
│   │
│   ├── 📁 app/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                  ← FastAPI entry point
│   │   ├── 📄 config.py                ← Settings & configuration
│   │   │
│   │   ├── 📁 api/                     ← ⚡ API GATEWAY
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 deps.py              ← Dependency injection
│   │   │   ├── 📁 v1/
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 router.py        ← Main router
│   │   │   │   ├── 📄 query.py         ← Query endpoints
│   │   │   │   ├── 📄 funds.py         ← Fund endpoints
│   │   │   │   └── 📄 health.py        ← Health checks
│   │   │   └── 📁 schemas/
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 query.py         ← Query request/response
│   │   │       ├── 📄 fund.py          ← Fund schemas
│   │   │       └── 📄 common.py        ← Shared schemas
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── 📄 __init__.py
│   │   │   │
│   │   │   ├── 📁 ingestion/           ← 🔍 RETRIEVAL (Embeddings)
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 loader.py        ← CSV loaders
│   │   │   │   ├── 📄 transformer.py   ← Data transformation
│   │   │   │   ├── 📄 chunker.py       ← Text chunking
│   │   │   │   └── 📄 embedder.py      ← BGE-M3 embeddings
│   │   │   │
│   │   │   ├── 📁 retrieval/           ← 🔍 RETRIEVAL LAYER
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 base.py          ← Base retriever interface
│   │   │   │   ├── 📄 semantic.py      ← Qdrant semantic search
│   │   │   │   ├── 📄 lexical.py       ← BM25 lexical search
│   │   │   │   ├── 📄 hybrid.py        ← Hybrid search + RRF
│   │   │   │   └── 📄 reranker.py      ← Cohere reranking
│   │   │   │
│   │   │   ├── 📁 generation/          ← 🧠 GENERATION LAYER
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 llm.py           ← Claude API wrapper
│   │   │   │   ├── 📄 prompts.py       ← Prompt templates
│   │   │   │   └── 📄 structured.py    ← Instructor structured output
│   │   │   │
│   │   │   └── 📁 orchestration/       ← 🔀 ORCHESTRATION LAYER
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 graph.py         ← LangGraph workflow
│   │   │       ├── 📄 nodes.py         ← Graph nodes
│   │   │       ├── 📄 classifier.py    ← Query classifier
│   │   │       └── 📄 state.py         ← Graph state definitions
│   │   │
│   │   ├── 📁 db/                      ← 💾 DATA LAYER (PostgreSQL)
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 session.py           ← Database session
│   │   │   ├── 📄 models.py            ← SQLModel models
│   │   │   └── 📄 repositories.py      ← Data access layer
│   │   │
│   │   ├── 📁 services/                ← 💾 DATA LAYER (Qdrant, Redis) + 👁️ OBSERVABILITY
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 vector_store.py      ← ChromaDB service
│   │   │   └── 📄 cache.py             ← Redis cache service
│   │   │
│   │   └── 📁 utils/
│   │       ├── 📄 __init__.py
│   │       ├── 📄 logging.py           ← Logging configuration
│   │       └── 📄 helpers.py           ← Helper functions
│   │
│   ├── 📁 data/                        ← 📂 DATA LAYER (CSV Files)
│   │   ├── 📁 raw/                     ← PUT YOUR CSV FILES HERE
│   │   │   ├── 📄 mutual_fund_faqs.csv
│   │   │   └── 📄 fund_performance.csv
│   │   └── 📁 processed/               ← Cached/processed data
│   │
│   ├── 📁 scripts/
│   │   ├── 📄 ingest_data.py           ← Data ingestion script
│   │   ├── 📄 seed_db.py               ← Database seeding
│   │   └── 📄 evaluate.py              ← Ragas evaluation
│   │
│   ├── 📁 tests/                       ← 👁️ OBSERVABILITY (Pytest)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 conftest.py
│   │   ├── 📁 unit/
│   │   ├── 📁 integration/
│   │   └── 📁 evaluation/              ← 👁️ OBSERVABILITY (Ragas)
│   │       └── 📄 test_rag_quality.py
│   │
│   └── 📁 notebooks/
│       └── 📄 exploration.ipynb
│
├── 📁 frontend/                        ← 🖥️ FRONTEND LAYER
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json                ← TypeScript config
│   ├── 📄 tailwind.config.ts           ← Tailwind config
│   ├── 📄 next.config.js
│   ├── 📄 Dockerfile
│   │
│   └── 📁 src/
│       ├── 📁 app/                     ← Next.js 14 App Router
│       │   ├── 📄 layout.tsx
│       │   ├── 📄 page.tsx
│       │   ├── 📁 chat/
│       │   ├── 📁 funds/
│       │   │   └── 📁 [fundId]/
│       │   ├── 📁 compare/
│       │   └── 📁 traces/
│       │
│       ├── 📁 components/
│       │   ├── 📁 ui/                  ← shadcn/ui components
│       │   ├── 📁 layout/
│       │   ├── 📁 chat/
│       │   ├── 📁 funds/
│       │   └── 📁 charts/              ← Tremor/Recharts
│       │
│       ├── 📁 lib/
│       ├── 📁 hooks/
│       ├── 📁 types/
│       └── 📁 providers/               ← TanStack Query provider
│
├── 📁 docs/
│   └── 📁 images/
│
├── 📁 infra/                           ← 🐳 INFRASTRUCTURE
│   ├── 📁 docker/
│   └── 📁 scripts/
│
├── 📁 evaluation/
│   └── 📁 results/
│
└── 📁 .github/                         ← 🐳 INFRASTRUCTURE (CI/CD)
    └── 📁 workflows/
        └── 📄 ci.yml
```

## Quick Reference: Where to Find What

| What You Need | Where to Find It |
|---------------|------------------|
| Put CSV files | `backend/data/raw/` |
| FastAPI endpoints | `backend/app/api/v1/` |
| BM25 search | `backend/app/core/retrieval/lexical.py` |
| Semantic search | `backend/app/core/retrieval/semantic.py` |
| Hybrid search + RRF | `backend/app/core/retrieval/hybrid.py` |
| Cohere reranking | `backend/app/core/retrieval/reranker.py` |
| BGE-M3 embeddings | `backend/app/core/ingestion/embedder.py` |
| Claude integration | `backend/app/core/generation/llm.py` |
| LangGraph workflow | `backend/app/core/orchestration/graph.py` |
| Query classifier | `backend/app/core/orchestration/classifier.py` |
| Next.js pages | `frontend/src/app/` |
| React components | `frontend/src/components/` |
| Docker setup | `docker-compose.yml` |
| Environment vars | `.env.example` |
