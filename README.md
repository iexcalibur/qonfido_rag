# Qonfido RAG - AI Financial Co-Pilot

A Retrieval-Augmented Generation (RAG) system for financial data, built for the Qonfido AI Co-Pilot assignment.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![Claude](https://img.shields.io/badge/Claude-API-purple)


## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js 16)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Home      │  │  AI Chat    │  │    Fund Explorer        │  │
│  │  (Cosmic)   │  │  (Glass UI) │  │    (Grid + Filters)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     RAG Pipeline                          │   │
│  │  ┌─────────┐  ┌───────────┐  ┌─────────┐  ┌───────────┐  │   │
│  │  │ Embed   │→ │ Retrieve  │→ │ Rerank  │→ │ Generate  │  │   │
│  │  │ (BGE-M3)│  │ (Hybrid)  │  │(Cohere) │  │ (Claude)  │  │   │
│  │  └─────────┘  └───────────┘  └─────────┘  └───────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ BM25 Index   │  │ ChromaDB     │  │ In-Memory Cache      │   │
│  │ (Lexical)    │  │ (Semantic)   │  │ (Embeddings+Queries) │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Core RAG Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Embeddings** | BGE-M3 (sentence-transformers) | 1024-dim dense vectors |
| **Vector Store** | ChromaDB (in-process) | Semantic similarity search |
| **Lexical Search** | BM25 (rank-bm25) | Keyword matching |
| **Hybrid Search** | RRF + Parallel Retrieval | Best of both worlds, 40-50% faster |
| **Reranking** | Cohere Rerank API | Two-stage retrieval (optional) |
| **Generation** | Claude API (Anthropic) | Answer generation |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Python 3.12+ | REST API |
| **Database** | SQLite (SQLModel ORM) | Metadata storage |
| **Cache** | In-Memory (TTL-based) | Embedding + Query caching |
| **Frontend** | Next.js 16 + Tailwind CSS | Modern UI with App Router |

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (3.12 recommended)
- Node.js 20+ (20.0.0+ recommended)
- npm 10+ (10.0.0+ recommended)
- Anthropic API Key (required)
- Cohere API Key (optional, for reranking)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Place your CSV files
cp /path/to/faqs.csv data/raw/
cp /path/to/funds.csv data/raw/

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Run development server
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📡 API Endpoints

### Query Endpoint
```bash
POST /api/v1/query
Content-Type: application/json

{
  "query": "Which funds have the best Sharpe ratio?",
  "search_mode": "hybrid",  // "lexical" | "semantic" | "hybrid"
  "top_k": 5,
  "rerank": true
}
```

### Response
```json
{
  "answer": "Based on the fund data, the top funds by Sharpe ratio are...",
  "query_type": "numerical",
  "funds": [
    {
      "fund_name": "Axis Bluechip Fund",
      "sharpe_ratio": 1.85,
      "cagr_3yr": 15.2,
      "risk_level": "Moderate"
    }
  ],
  "sources": [...],
  "confidence": 0.85,
  "search_mode": "hybrid"
}
```

### Other Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/funds` | GET | List all funds |
| `/api/v1/funds/{id}` | GET | Fund details |
| `/api/v1/search-modes` | GET | Available search modes |

## 📊 Evaluation

Run the evaluation script to measure RAG quality:

```bash
cd backend

# Evaluate hybrid search (default)
python -m scripts.evaluate

# Compare all modes
python -m scripts.evaluate --mode all --verbose

# Save results to file
python -m scripts.evaluate --output results.json
```

### Evaluation Metrics
- **Pass Rate**: % of queries with acceptable answers
- **Keyword Coverage**: Expected terms found in answer
- **Source Quality**: Correct source type retrieved
- **Type Accuracy**: Query type classification accuracy
- **Latency**: Response time per query

## 📁 Project Structure

```
qonfido-rag/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Configuration management
│   │   │
│   │   ├── api/                       # REST API Layer
│   │   │   ├── __init__.py
│   │   │   ├── schemas/               # Pydantic request/response models
│   │   │   │   ├── common.py          # Shared schemas (Health, Pagination)
│   │   │   │   ├── fund.py            # Fund-related schemas
│   │   │   │   └── query.py           # Query request/response schemas
│   │   │   └── v1/                    # API version 1
│   │   │       ├── router.py          # Main API router
│   │   │       ├── query.py           # Main RAG query endpoint
│   │   │       ├── funds.py           # Fund explorer endpoints
│   │   │       └── health.py          # Health check endpoint
│   │   │
│   │   ├── core/                      # Core Business Logic
│   │   │   ├── ingestion/             # Data Ingestion & Processing
│   │   │   │   ├── loader.py          # CSV data loading (FAQs, Funds)
│   │   │   │   └── embedder.py        # Embedding generation (BGE-M3)
│   │   │   ├── retrieval/             # Search & Retrieval
│   │   │   │   ├── lexical.py         # BM25 keyword search
│   │   │   │   ├── semantic.py        # ChromaDB vector search
│   │   │   │   ├── hybrid.py          # Hybrid search (RRF + Parallel)
│   │   │   │   └── reranker.py        # Cohere reranking
│   │   │   ├── generation/            # LLM Response Generation
│   │   │   │   ├── llm.py             # Claude API integration
│   │   │   │   └── prompts.py         # Prompt templates
│   │   │   └── orchestration/         # RAG Pipeline Orchestration
│   │   │       └── pipeline.py        # Main RAG pipeline coordinator
│   │   │
│   │   ├── db/                        # Database Layer
│   │   │   ├── models.py              # SQLModel database models
│   │   │   ├── repositories.py        # Data access layer
│   │   │   └── session.py             # Database connection management
│   │   │
│   │   ├── services/                  # External Service Integrations
│   │   │   ├── cache.py               # In-memory caching service
│   │   │   └── vector_store.py        # Vector store wrapper
│   │   │
│   │   └── utils/                     # Utility Functions
│   │       ├── helpers.py             # Common utility functions
│   │       └── logging.py             # Logging configuration
│   │
│   ├── data/
│   │   ├── raw/                       # Raw CSV files
│   │   │   ├── faqs.csv               # Mutual fund FAQs
│   │   │   └── funds.csv              # Fund performance data
│   │   └── processed/                 # Processed data (if any)
│   │
│   ├── scripts/                       # Utility Scripts
│   │   ├── ingest_data.py             # Data ingestion script
│   │   ├── seed_db.py                 # Database seeding
│   │   ├── evaluate.py                # RAG evaluation script
│   │   └── test_query.py              # Query testing script
│   │
│   ├── tests/                         # Test Suite
│   │   ├── unit/                      # Unit tests
│   │   ├── integration/               # Integration tests
│   │   └── evaluation/                # Evaluation tests
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── test_backend.py                # Backend test runner
│   └── venv/                          # Virtual environment (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js App Router (Pages)
│   │   │   ├── layout.tsx             # Root layout component
│   │   │   ├── page.tsx               # Homepage (Landing page)
│   │   │   ├── globals.css            # Global styles
│   │   │   ├── chat/
│   │   │   │   └── page.tsx           # Chat interface page
│   │   │   └── funds/
│   │   │       ├── page.tsx           # Fund Explorer (list)
│   │   │       └── [fundId]/
│   │   │           └── page.tsx       # Fund detail page
│   │   │
│   │   ├── components/                # React Components
│   │   │   ├── Header.tsx             # Main navigation header
│   │   │   ├── chat/                  # Chat-related components
│   │   │   │   ├── ChatInput.tsx      # Chat input with search mode
│   │   │   │   ├── ChatMessage.tsx    # Individual chat message
│   │   │   │   ├── CitationChip.tsx   # Source citation badge
│   │   │   │   ├── FundAnalysisResults.tsx  # Fund metrics grid
│   │   │   │   ├── FundInsightCard.tsx      # Individual fund card
│   │   │   │   ├── FundMetricsUtils.ts      # Metric utility functions
│   │   │   │   ├── MetricCard.tsx     # Generic metric card
│   │   │   │   ├── WelcomeMessage.tsx # Welcome screen
│   │   │   │   └── index.ts           # Component exports
│   │   │   └── layout/                # Layout components
│   │   │       ├── ConditionalLayout.tsx  # Conditional layout wrapper
│   │   │       ├── Header.tsx         # Alternative header
│   │   │       ├── Sidebar.tsx        # Sidebar navigation
│   │   │       └── index.ts           # Component exports
│   │   │
│   │   ├── lib/                       # Utility Libraries
│   │   │   ├── api.ts                 # API client functions
│   │   │   └── utils.ts               # Utility functions
│   │   │
│   │   ├── types/                     # TypeScript Type Definitions
│   │   │   └── index.ts               # All type definitions
│   │   │
│   │   └── hooks/                     # Custom React Hooks
│   │       └── index.ts               # Custom hooks (useChat, useFunds, etc.)
│   │
│   ├── package.json                   # Dependencies & scripts
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.ts             # Tailwind CSS configuration
│   ├── next.config.js                 # Next.js configuration
│   ├── postcss.config.js              # PostCSS configuration
│   └── next-env.d.ts                  # Next.js TypeScript declarations
│
├── docs/                              # Documentation
│   ├── BACKEND_DOCUMENTATION.md       # Detailed backend file documentation
│   ├── FRONTEND_DOCUMENTATION.md      # Detailed frontend file documentation
│   ├── BACKEND_ANALYSIS.md            # Backend implementation analysis
│   ├── PROJECT_OBJECTIVE.md           # Project objectives
│   ├── PROJECT_STRUCTURE.md           # Project structure documentation
│   └── ARCHITECTURE_MAPPING.md        # Architecture mapping
│
├── evaluation/
│   └── results/                       # Evaluation results
│
├── infra/                             # Infrastructure
│   ├── docker/                        # Docker configurations
│   └── scripts/                       # Infrastructure scripts
│
├── docker-compose.yml                 # Docker Compose configuration
├── Makefile                           # Make commands
├── package.json                       # Root package.json
├── start.sh                           # Startup script
├── start.ps1                          # PowerShell startup script
└── README.md                          # This file
```

## ⚙️ Configuration

### Environment Variables

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
COHERE_API_KEY=...           # For reranking (optional)
EMBEDDING_MODEL=BAAI/bge-m3  # Default embedding model
CLAUDE_MODEL=claude-3-opus-20240229  # Claude model for generation
DATA_DIR=data
FAQS_FILE=faqs.csv
FUNDS_FILE=funds.csv
```

## 🔧 Key Features

### 1. Flexible Data Loading
- Handles different CSV column names automatically
- Converts numerical metrics to searchable text
- Supports missing data gracefully

### 2. Hybrid Search with Parallel Retrieval
- BM25 for exact keyword matching
- ChromaDB for semantic similarity
- RRF fusion for optimal ranking
- **40-50% faster** with parallel execution

### 3. Multi-Level Caching
- **Embedding Cache**: Avoids recomputing embeddings (24hr TTL)
- **Query Cache**: Instant response for repeated queries (5min TTL)
- Hash-based keys for efficient lookup

### 4. Production-Ready API
- Comprehensive error handling
- Request validation with Pydantic
- OpenAPI documentation
- Health checks

## 📈 Performance

| Metric | Value |
|--------|-------|
| First Query | ~2-4s (includes LLM) |
| Cached Query | ~50ms |
| Embedding Cache Hit | ~10ms |
| Parallel vs Sequential | ~40% faster |

## 🧪 Testing

```bash
cd backend

# Run evaluation
python -m scripts.evaluate --verbose

# Compare all search modes
python -m scripts.evaluate --mode all

# Test specific query
python -m scripts.test_query "What is a mutual fund?"
```

## 📝 What I Learned

### RAG Best Practices
1. **Hybrid search** (BM25 + semantic) consistently outperforms either alone
2. **RRF fusion** is simple but effective for combining ranked lists
3. **Parallel retrieval** is an easy win for latency
4. **Caching embeddings** is essential for production

### Technical Decisions
- **ChromaDB** over Qdrant: Simpler setup, good for MVP
- **In-memory cache** over Redis: Good for development, easy to migrate later
- **SQLite** over PostgreSQL: Zero config, sufficient for this scale

## 📄 License

This project was created for the Qonfido AI Co-Pilot assignment.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) - Claude API
- [Cohere](https://cohere.com) - Reranking API
- [ChromaDB](https://trychroma.com) - Vector Store
- [Sentence Transformers](https://sbert.net) - Embeddings