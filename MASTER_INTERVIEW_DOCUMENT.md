# Qonfido RAG - Master Interview Document

**Complete Technical Analysis & Interview Preparation Guide**

---

## Table of Contents

1. [Project Structure Summary](#1-project-structure-summary)
2. [File-by-File Analysis](#2-file-by-file-analysis)
3. [End-to-End RAG Architecture](#3-end-to-end-rag-architecture)
4. [Interview Questions & Answers](#4-interview-questions--answers)
5. [Failure Points & Improvements](#5-failure-points--improvements)
6. [Human-Speak Explanation](#6-human-speak-explanation)
7. [Quick Reference](#7-quick-reference)

---

# 1. Project Structure Summary

## High-Level Tree Structure

```
qonfido_rag/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   │   ├── v1/           # Version 1 API routes
│   │   │   └── schemas/      # Pydantic models
│   │   ├── core/             # Core RAG logic
│   │   │   ├── ingestion/    # Data loading & embedding
│   │   │   ├── retrieval/    # Search components
│   │   │   ├── generation/   # LLM & prompts
│   │   │   └── orchestration/# Main RAG pipeline
│   │   ├── services/         # Services (cache, vector store)
│   │   ├── db/              # Database models (SQLModel)
│   │   ├── utils/           # Utilities
│   │   ├── config.py        # Settings & configuration
│   │   └── main.py          # FastAPI app entry point
│   ├── data/                # Data storage
│   │   ├── raw/            # Source CSV files
│   │   └── index.state     # Persistence hash
│   ├── chroma_db/          # ChromaDB vector store
│   ├── scripts/            # Utility scripts
│   └── requirements.txt    # Python dependencies
│
├── frontend/                  # Next.js 16 React frontend
│   ├── src/
│   │   ├── app/            # Next.js app router pages
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities & API client
│   │   └── types/          # TypeScript types
│   └── package.json
│
├── infra/                    # Infrastructure configs
│   └── scripts/            # Deployment scripts
│
├── docs/                    # Architecture documentation
└── docker-compose.yml       # Docker orchestration
```

## Component Detection

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript/React
- **Styling**: Tailwind CSS
- **State Management**: React Query + Custom Hooks

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **API**: RESTful with OpenAPI docs
- **Validation**: Pydantic v2

### Infrastructure
- **Vector DB**: ChromaDB (in-process, persistent)
- **Cache**: In-memory (upgradeable to Redis)
- **Containerization**: Docker Compose

### RAG Components

#### 1. **Ingestion** (`backend/app/core/ingestion/`)
- `loader.py`: CSV parsing, data transformation
- `embedder.py`: BGE-M3 embeddings with caching

#### 2. **Indexing**
- Lexical: BM25 index (in-memory)
- Semantic: ChromaDB vector store (persistent)
- State: Hash-based change detection

#### 3. **Retrieval** (`backend/app/core/retrieval/`)
- `lexical.py`: BM25 keyword search
- `semantic.py`: Vector similarity search
- `hybrid.py`: RRF fusion with parallel execution
- `reranker.py`: Cohere reranking (optional)

#### 4. **Generation** (`backend/app/core/generation/`)
- `llm.py`: Claude 3 Opus API client
- `prompts.py`: Prompt templates

#### 5. **Orchestration** (`backend/app/core/orchestration/`)
- `pipeline.py`: Main RAG pipeline coordinator

#### 6. **Services**
- `cache.py`: Multi-level caching (embeddings + queries)
- `vector_store.py`: ChromaDB wrapper

---

# 2. File-by-File Analysis

## Backend Core Files

### `backend/app/main.py`

- **Purpose**: FastAPI application entry point and lifespan management
- **Why needed**: Orchestrates startup/shutdown, pre-initializes pipeline, loads funds cache
- **What breaks if removed**: Application won't start, no API endpoints, no initialization
- **Key logic**:
  - `lifespan()`: Async context manager for startup/shutdown
  - Pre-loads funds cache on startup
  - Pre-initializes RAG pipeline (loads model, builds indexes)
  - CORS middleware configuration
- **Dependencies**: `config.py`, `pipeline.py`, FastAPI, logging
- **Interview explanation**: "This is the FastAPI application bootstrap. It handles startup lifecycle - pre-loading data, initializing the RAG pipeline so first query is fast, and setting up middleware. The lifespan manager ensures graceful startup/shutdown."
- **Improvements**: Add health check endpoints, startup readiness probe, graceful shutdown handlers

---

### `backend/app/config.py`

- **Purpose**: Centralized configuration using Pydantic Settings
- **Why needed**: Type-safe config, environment variable management, single source of truth
- **What breaks if removed**: No configuration loading, API keys missing, defaults not applied
- **Key logic**:
  - `Settings` class: All config values with defaults
  - `@lru_cache` on `get_settings()`: Singleton pattern
  - Property methods for computed paths (faqs_path, funds_path)
  - SecretStr for API keys (prevents accidental logging)
- **Dependencies**: Pydantic Settings, Path
- **Interview explanation**: "Centralized config management. Uses Pydantic Settings for validation, supports .env files, and caches the instance. API keys are SecretStr to prevent accidental exposure in logs. All paths and model names are configurable."
- **Improvements**: Add config validation, environment-specific defaults, schema export for docs

---

### `backend/app/core/orchestration/pipeline.py`

- **Purpose**: Main RAG pipeline orchestrator - coordinates all components
- **Why needed**: Single entry point for query processing, manages initialization, caching
- **What breaks if removed**: No way to process queries, entire RAG system unusable
- **Key logic**:
  - `_get_current_state_hash()`: MD5 hash of CSV files + config for change detection
  - `initialize()`: Smart persistence - skips re-indexing if hash matches
  - `process()`: Full RAG flow - query cache check → embed → retrieve → rerank → generate
  - `_classify_query()`: Simple keyword-based query type detection
  - `_extract_fund_info()`: Extracts structured fund data from results
  - `_calculate_confidence()`: Average score from top results
- **Dependencies**: All core modules (ingestion, retrieval, generation, services)
- **Interview explanation**: "The brain of the RAG system. It orchestrates the full pipeline - checks cache, generates query embedding, runs hybrid search in parallel, optionally reranks, passes context to LLM, then formats the response. The hash-based persistence means we skip expensive re-indexing if data hasn't changed - startup goes from 2-4 minutes to 5-10 seconds."
- **Improvements**: Add async batch processing, query routing based on complexity, A/B testing support, metrics collection

---

### `backend/app/core/ingestion/loader.py`

- **Purpose**: Load and transform CSV data into document format for indexing
- **Why needed**: Converts structured fund data to semantic text, handles flexible CSV columns
- **What breaks if removed**: No data loading, pipeline can't index documents
- **Key logic**:
  - `FAQItem.to_document()`: Combines Q&A into single text
  - `FundData.text_for_embedding`: **Critical** - converts structured metrics to descriptive text
    - Example: `{"sharpe": 1.25}` → `"Fund X has Sharpe Ratio: 1.25..."`
  - `DataLoader`: Flexible column matching (handles various CSV formats)
  - `_get_numeric_value()`: Handles percentage strings, commas
- **Dependencies**: Pandas, Pydantic
- **Interview explanation**: "This is where we solve the numerical embedding problem. Instead of embedding raw numbers that models struggle with, we convert fund metrics into rich semantic descriptions. A fund with Sharpe 1.25 becomes 'Fund X has excellent risk-adjusted returns with Sharpe Ratio of 1.25'. This enables semantic queries like 'safe funds' to find high Sharpe ratios."
- **Improvements**: Add data validation, schema validation, incremental loading, error recovery

---

### `backend/app/core/ingestion/embedder.py`

- **Purpose**: Generate embeddings using sentence-transformers with caching
- **Why needed**: Converts text to vectors for semantic search, caches expensive computations
- **What breaks if removed**: No embeddings, semantic search fails, hybrid search broken
- **Key logic**:
  - Lazy model loading: Downloads BGE-M3 on first use (~2.3GB)
  - `embed_texts()`: Batch embedding with progress bar, cache-aware
  - `embed_query()`: Single query embedding with cache check
  - Fallback to all-MiniLM-L6-v2 if BGE-M3 fails
  - Batch cache retrieval: Gets cached + computes only missing embeddings
- **Dependencies**: sentence-transformers, numpy, cache service
- **Interview explanation**: "The embedding engine. Uses BGE-M3 (1024-dim) for high-quality embeddings. Implements caching at the text level - same text never gets embedded twice. Batch processing with progress feedback. The cache saves significant compute time and API costs since embedding is expensive."
- **Improvements**: Add GPU support detection, batch size auto-tuning, embedding quality metrics, model versioning

---

### `backend/app/core/retrieval/lexical.py`

- **Purpose**: BM25 keyword-based search for exact term matching
- **Why needed**: Handles specific queries like "Axis Bluechip Fund", complements semantic search
- **What breaks if removed**: No exact keyword matching, hybrid search degraded
- **Key logic**:
  - `_tokenize()`: Lowercase, remove punctuation, split words
  - `index_documents()`: Builds BM25Okapi index from tokenized docs
  - `search()`: BM25 scoring, source filtering, top-k retrieval
- **Dependencies**: rank-bm25
- **Interview explanation**: "Classic BM25 search - great for exact keyword matches. If someone searches 'Axis Bluechip Fund', this finds it even if semantic search misses it. Tokenization is simple - lowercase and split. This complements semantic search which might miss exact names."
- **Improvements**: Add stemming/lemmatization, custom tokenizer, query expansion, phrase matching

---

### `backend/app/core/retrieval/semantic.py`

- **Purpose**: Vector similarity search using ChromaDB
- **Why needed**: Handles conceptual queries, semantic understanding
- **What breaks if removed**: No semantic search, only exact keyword matching
- **Key logic**:
  - `_initialize()`: Lazy ChromaDB client initialization with persistence
  - `index_documents()`: Stores embeddings + metadata in ChromaDB
  - `search()`: Cosine similarity search with metadata filtering
  - `document_count`: Property for health checks
- **Dependencies**: ChromaDB, numpy
- **Interview explanation**: "Vector search using ChromaDB. Stores embeddings in a persistent collection with metadata for filtering. Uses cosine similarity - ChromaDB handles the HNSW indexing automatically. The lazy initialization means we don't connect until needed, and persistence means indexes survive restarts."
- **Improvements**: Add index tuning, metadata indexing, similarity threshold, batch queries

---

### `backend/app/core/retrieval/hybrid.py`

- **Purpose**: Combines lexical + semantic search using Reciprocal Rank Fusion (RRF)
- **Why needed**: Best of both worlds - exact matches + semantic understanding
- **What breaks if removed**: Only single-mode search, degraded accuracy
- **Key logic**:
  - `search()`: Runs lexical + semantic in parallel using ThreadPoolExecutor
  - RRF scoring: `score = (1-α) * (1/(k+lex_rank)) + α * (1/(k+sem_rank))`
  - Merges results by document ID, combines metadata
  - Sorts by combined RRF score
- **Dependencies**: lexical.py, semantic.py, ThreadPoolExecutor
- **Interview explanation**: "This is our hybrid search engine. Runs BM25 and vector search in parallel for 40-50% latency reduction. Uses Reciprocal Rank Fusion - a rank-based combination that doesn't require score normalization. RRF naturally handles cases where one method finds relevant docs the other misses. The alpha parameter controls the blend."
- **Improvements**: Add adaptive alpha based on query type, learn optimal k parameter, result deduplication, weighted fusion

---

### `backend/app/core/retrieval/reranker.py`

- **Purpose**: Rerank search results using Cohere API for improved accuracy
- **Why needed**: Cross-encoder reranking improves precision, optional but valuable
- **What breaks if removed**: Slightly lower accuracy, but system still works (graceful degradation)
- **Key logic**:
  - Lazy Cohere client initialization
  - `rerank()`: Sends query + documents to Cohere, gets relevance scores
  - Returns reranked results with original + new scores
  - Fallback: Returns original results if API fails
- **Dependencies**: Cohere API
- **Interview explanation**: "Optional reranking step. Takes top results from hybrid search and reranks them using Cohere's cross-encoder model. Cross-encoders see query + document together, so they're more accurate than independent embeddings. If Cohere is down or key missing, we gracefully fall back to hybrid results - system never breaks."
- **Improvements**: Add local reranker option, batch reranking, cache rerank results, confidence threshold

---

### `backend/app/core/generation/llm.py`

- **Purpose**: Generate answers using Claude 3 Opus API
- **Why needed**: Converts retrieved context into natural language answers
- **What breaks if removed**: No answer generation, only raw retrieved documents
- **Key logic**:
  - Lazy Anthropic client initialization
  - `generate()`: Formats context, constructs prompt, calls Claude API
  - `_format_context()`: Adds metadata, source attribution
  - `_get_default_system_prompt()`: Financial assistant persona
- **Dependencies**: Anthropic API
- **Interview explanation**: "The LLM generator. Uses Claude 3 Opus for high-quality responses. Formats retrieved documents as context with metadata - includes fund names and metrics for transparency. The system prompt sets the persona as a financial assistant. Temperature is low (0.3) for factual accuracy."
- **Improvements**: Add streaming responses, token usage tracking, prompt versioning, few-shot examples, structured outputs

---

### `backend/app/core/generation/prompts.py`

- **Purpose**: Prompt templates for different query types
- **Why needed**: Specialized prompts improve answer quality for different query types
- **What breaks if removed**: Generic prompts, potentially lower quality answers
- **Key logic**:
  - `FAQ_PROMPT`: For conceptual questions
  - `NUMERICAL_PROMPT`: For fund metrics queries
  - `HYBRID_PROMPT`: For mixed queries
  - `get_prompt_template()`: Routes to appropriate template
- **Dependencies**: None (pure functions)
- **Interview explanation**: "Prompt templates tuned for different query types. FAQ prompts focus on explanations, numerical prompts emphasize metrics, hybrid prompts combine both. This helps Claude generate better-formatted, more relevant answers."
- **Improvements**: Add prompt testing framework, A/B testing, dynamic prompt selection, few-shot examples

---

### `backend/app/services/cache.py`

- **Purpose**: Multi-level caching system for embeddings and query results
- **Why needed**: Dramatically reduces latency and compute costs
- **What breaks if removed**: Every query re-embeds, no query caching, much slower
- **Key logic**:
  - `InMemoryCache`: TTL-based cache with expiration cleanup
  - `EmbeddingCache`: Text hash → embedding mapping (24h TTL)
  - `QueryCache`: Query params → full response mapping (5m TTL)
  - Batch cache retrieval: Gets multiple embeddings at once
- **Dependencies**: hashlib, numpy
- **Interview explanation**: "Two-tier caching. Embedding cache saves expensive model inference - same text never embedded twice. Query cache saves full pipeline execution - repeated questions get instant responses. TTLs balance freshness vs performance. Hash-based keys ensure exact matches. In-memory for MVP but structured for Redis migration."
- **Improvements**: Add Redis backend, cache warming, cache invalidation webhooks, hit rate metrics, LRU eviction

---

### `backend/app/services/vector_store.py`

- **Purpose**: Service wrapper around ChromaDB with health checks
- **Why needed**: Abstraction layer, health monitoring, easier testing
- **What breaks if removed**: Direct ChromaDB usage, no health checks
- **Key logic**:
  - Wraps SemanticSearcher
  - `health_check()`: Returns document count, status
  - Delegates all operations to underlying searcher
- **Dependencies**: semantic.py
- **Interview explanation**: "Service wrapper for the vector store. Provides health check endpoint, abstracts ChromaDB details. Makes it easy to swap vector stores later - just change the implementation. Currently wraps our SemanticSearcher which uses ChromaDB."
- **Improvements**: Add connection pooling, retry logic, metrics collection, swap vector store easily

---

### `backend/app/api/v1/router.py`

- **Purpose**: API router configuration - aggregates all endpoints
- **Why needed**: Centralized route registration, version management
- **What breaks if removed**: Routes not registered, endpoints unreachable
- **Key logic**:
  - `api_router`: FastAPI APIRouter instance
  - Includes all endpoint routers (query, funds, health)
  - Prefix: `/api/v1`
- **Dependencies**: All v1 endpoint modules
- **Interview explanation**: "Main API router. Aggregates all endpoint modules under `/api/v1` prefix. Makes versioning easy - can add v2 router later. Clean separation of concerns - each endpoint module focuses on one domain."
- **Improvements**: Add rate limiting, request ID middleware, API versioning strategy

---

### `backend/app/api/v1/query.py`

- **Purpose**: RAG query endpoint - main API entry point
- **Why needed**: REST API for processing queries
- **What breaks if removed**: No way to query via API, frontend can't work
- **Key logic**:
  - `query()`: POST endpoint, validates request, calls pipeline, returns response
  - `list_search_modes()`: GET endpoint for available search modes
  - Error handling: 400 for validation, 500 for server errors
- **Dependencies**: pipeline.py, schemas
- **Interview explanation**: "The main query endpoint. Takes a QueryRequest, validates it, passes to pipeline, returns QueryResponse. Includes error handling and logging. Also exposes available search modes. This is what the frontend calls."
- **Improvements**: Add request validation, rate limiting per user, query logging, analytics

---

### `backend/app/api/schemas/query.py`

- **Purpose**: Pydantic models for query API - request/response validation
- **Why needed**: Type safety, automatic validation, OpenAPI schema generation
- **What breaks if removed**: No request validation, no type hints, broken OpenAPI docs
- **Key logic**:
  - `SearchMode`: Enum for search modes
  - `QueryRequest`: Input validation (query length, top_k bounds)
  - `QueryResponse`: Output structure with answer, sources, funds, confidence
  - `SourceDocument`: Citation format
  - `FundInfo`: Structured fund data
- **Dependencies**: Pydantic
- **Interview explanation**: "API contract definition. Pydantic models provide automatic validation - invalid requests rejected before processing. Also generates OpenAPI schema automatically. Ensures frontend/backend stay in sync with types."
- **Improvements**: Add more validation rules, example values, response variants

---

### `backend/app/api/schemas/fund.py`

- **Purpose**: Pydantic models for fund-related endpoints
- **Why needed**: Type-safe fund data structures, validation, API contract
- **What breaks if removed**: Fund endpoints broken, no type safety for fund data
- **Key logic**:
  - `FundSummary`: Lightweight fund info for list views
  - `FundDetail`: Complete fund information with all metrics
  - `FundListResponse`: Paginated fund list
  - `FundCompareRequest/Response`: Fund comparison models
- **Dependencies**: Pydantic
- **Interview explanation**: "Fund schema definitions. Separates summary (list views) from detail (full info). Includes all financial metrics - CAGR, Sharpe, volatility, etc. Used by funds endpoints for consistent data structures."
- **Improvements**: Add computed fields (returns, ratios), validation rules, example data

---

### `backend/app/api/schemas/common.py`

- **Purpose**: Shared Pydantic models used across endpoints
- **Why needed**: DRY principle, consistent response formats
- **What breaks if removed**: Code duplication, inconsistent responses
- **Key logic**:
  - `HealthResponse`: Health check format
  - `MessageResponse`: Simple message wrapper
  - `PaginationParams/Response`: Pagination utilities
- **Dependencies**: Pydantic
- **Interview explanation**: "Common schemas shared across endpoints. Avoids duplication, ensures consistency. HealthResponse for status checks, pagination models for list endpoints."
- **Improvements**: Add more common models (error responses, metadata), versioning

---

### `backend/app/api/v1/funds.py`

- **Purpose**: Fund data retrieval and comparison endpoints
- **Why needed**: Allows browsing funds, filtering, comparison - supports frontend fund pages
- **What breaks if removed**: No way to list/browse funds, frontend fund pages broken
- **Key logic**:
  - `get_funds()`: Loads funds from CSV, caches in-memory
  - `list_funds()`: GET with category/risk filtering, pagination
  - `get_fund()`: GET single fund by ID
  - `compare_funds()`: POST to compare 2-5 funds side-by-side
  - `get_fund_metrics_summary()`: Aggregate statistics
- **Dependencies**: loader.py, fund schemas
- **Interview explanation**: "Fund browsing endpoints. Loads funds from CSV into memory cache on first request. Supports filtering by category/risk, fund comparison, and aggregate metrics. Simple in-memory cache for MVP - would move to DB for production."
- **Improvements**: Add database backend, pagination, sorting, advanced filtering, caching strategy

---

### `backend/app/api/v1/health.py`

- **Purpose**: Health and readiness check endpoints
- **Why needed**: Kubernetes/Docker health probes, monitoring, deployment checks
- **What breaks if removed**: No health checks, harder to monitor, deployment issues
- **Key logic**:
  - `health_check()`: Returns API status, version, service statuses
  - `readiness_check()`: Simple ready/not-ready for probes
- **Dependencies**: schemas/common.py, config.py
- **Interview explanation**: "Health check endpoints. Used by Kubernetes for liveness/readiness probes, monitoring tools, load balancers. Returns API status and service health. Simple but critical for production operations."
- **Improvements**: Add actual service health checks (vector store, cache, external APIs), detailed status reporting, metrics

---

### `backend/app/utils/logging.py`

- **Purpose**: Logging configuration setup
- **Why needed**: Centralized logging, consistent format across app
- **What breaks if removed**: No structured logging, harder debugging
- **Key logic**: Configures Python logging with levels, formats
- **Dependencies**: Python logging
- **Interview explanation**: "Logging setup. Configures log levels, formats. Critical for debugging in production - structured logs help trace issues through the pipeline."
- **Improvements**: Add structured logging (JSON), log aggregation integration, log sampling

---

### `backend/scripts/ingest_data.py`

- **Purpose**: Standalone script to ingest data and build indexes
- **Why needed**: Allows pre-building indexes before server starts, testing ingestion
- **What breaks if removed**: Must rely on server startup for indexing, slower first run
- **Key logic**: Creates pipeline, loads data, initializes indexes, saves state
- **Dependencies**: pipeline.py, loader.py
- **Interview explanation**: "Data ingestion script. Can run independently to build indexes before server starts. Useful for testing, pre-warming, CI/CD. Builds both lexical and semantic indexes."
- **Improvements**: Add incremental ingestion, validation checks, progress reporting

---

## Frontend Core Files

### `frontend/src/lib/api.ts`

- **Purpose**: API client for backend communication
- **Why needed**: Centralized HTTP client, type-safe API calls
- **What breaks if removed**: Frontend can't communicate with backend
- **Key logic**: fetch wrapper, error handling, type-safe request/response
- **Dependencies**: types/index.ts
- **Interview explanation**: "Frontend API client. Wraps fetch with error handling, type safety. Makes API calls from React components. Uses TypeScript types matching backend schemas."
- **Improvements**: Add retry logic, request cancellation, caching, interceptors

---

### `frontend/src/lib/utils.ts`

- **Purpose**: Frontend utility functions
- **Why needed**: Shared helpers (formatting, parsing, etc.)
- **What breaks if removed**: Missing utility functions, code duplication
- **Key logic**: Format numbers, parse dates, etc.
- **Dependencies**: None
- **Interview explanation**: "Utility functions for formatting, parsing. Shared across components to avoid duplication."
- **Improvements**: Add more formatters, date utilities, validation helpers

---

### `frontend/src/types/index.ts`

- **Purpose**: TypeScript type definitions matching backend schemas
- **Why needed**: Type safety, IntelliSense, compile-time checks
- **What breaks if removed**: No type checking, potential runtime errors
- **Key logic**: Defines all API types, component props types
- **Dependencies**: None (pure types)
- **Interview explanation**: "TypeScript types matching backend. Ensures frontend/backend stay in sync. Provides autocomplete and compile-time error checking."
- **Improvements**: Generate types from OpenAPI schema automatically

---

## Configuration Files

### `docker-compose.yml`

- **Purpose**: Multi-container Docker orchestration
- **Why needed**: Easy local development, production deployment
- **What breaks if removed**: No containerized setup, manual service management
- **Key logic**: Defines services (backend, frontend, postgres, redis), networks, volumes
- **Dependencies**: Docker
- **Interview explanation**: "Docker Compose config. Orchestrates all services - backend, frontend, databases. Includes health checks, volume mounts, environment variables. One command to start everything."
- **Improvements**: Add production overrides, secrets management, resource limits

---

### `Makefile`

- **Purpose**: Convenience commands for development workflow
- **Why needed**: Simplifies common tasks (setup, dev, test, ingest)
- **What breaks if removed**: Must remember complex commands, inconsistent workflows
- **Key logic**: Wraps common commands in simple targets
- **Dependencies**: bash, Python, Node
- **Interview explanation**: "Makefile for developer convenience. Wraps complex commands - `make dev` starts both servers, `make ingest` runs ingestion. Reduces cognitive load and ensures consistent workflows."
- **Improvements**: Add more targets, validation checks, better error messages

---

# 3. End-to-End RAG Architecture

## A. Data Flow (Step-by-Step)

### 1. **Data Ingestion**
- **Files**: `scripts/ingest_data.py`, `core/ingestion/loader.py`
- **Process**:
  - Load CSV files (faqs.csv, funds.csv)
  - Parse with pandas, flexible column matching
  - Convert structured data to semantic text
  - Create document objects with metadata
- **Output**: List of document dictionaries

### 2. **Preprocessing**
- **Files**: `core/ingestion/loader.py`
- **Process**:
  - FAQ: Combine question + answer into single text
  - Funds: Convert metrics to descriptive sentences
  - Normalize text, handle missing values
  - Generate unique document IDs
- **Output**: Clean, normalized documents

### 3. **Embedding Generation**
- **Files**: `core/ingestion/embedder.py`, `services/cache.py`
- **Process**:
  - Check embedding cache (24h TTL)
  - Batch embed uncached texts with BGE-M3
  - Normalize embeddings (L2 normalization)
  - Store in cache for future use
- **Output**: NumPy array of embeddings (N x 1024)

### 4. **Storage**
- **Vector DB**: ChromaDB (`core/retrieval/semantic.py`)
  - Store embeddings + metadata
  - Persistent storage on disk
  - HNSW index for fast similarity search
- **Lexical Index**: In-memory BM25 (`core/retrieval/lexical.py`)
  - Tokenized documents
  - BM25Okapi index
- **State File**: `data/index.state` (`pipeline.py`)
  - MD5 hash of data files + config
  - Used for change detection

### 5. **Retrieval Pipeline** (Query Time)
- **Files**: `core/retrieval/hybrid.py`, `core/orchestration/pipeline.py`
- **Process**:
  - Check query cache (5m TTL)
  - Generate query embedding
  - **Parallel execution**:
    - Lexical search (BM25) - Thread 1
    - Semantic search (ChromaDB) - Thread 2
  - Combine results using RRF (Reciprocal Rank Fusion)
  - Return top-k documents

### 6. **Reranking** (Optional)
- **Files**: `core/retrieval/reranker.py`
- **Process**:
  - Send query + documents to Cohere API
  - Cross-encoder reranks by relevance
  - Returns top-k reranked results
  - Falls back gracefully if API unavailable

### 7. **LLM Reasoning**
- **Files**: `core/generation/llm.py`, `core/generation/prompts.py`
- **Process**:
  - Format retrieved documents as context
  - Select prompt template (FAQ/Numerical/Hybrid)
  - Construct system + user prompts
  - Call Claude 3 Opus API
  - Extract answer from response

### 8. **Response Formatting**
- **Files**: `core/orchestration/pipeline.py`
- **Process**:
  - Classify query type (FAQ/numerical/hybrid)
  - Extract fund information from results
  - Calculate confidence score
  - Format sources with citations
  - Cache response (if enabled)
- **Output**: `QueryResponse` with answer, sources, funds, confidence

## B. Architecture Diagram (ASCII)

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────────┐
│        Next.js Frontend                 │
│  - Chat Interface                       │
│  - Fund Lists                           │
│  - React Query Cache                    │
└──────┬──────────────────────────────────┘
       │
       │ API Request
       ▼
┌─────────────────────────────────────────┐
│      FastAPI Backend                    │
│  ┌──────────────────────────────────┐  │
│  │   API Router (/api/v1/query)     │  │
│  └──────┬───────────────────────────┘  │
│         │                               │
│         ▼                               │
│  ┌──────────────────────────────────┐  │
│  │   RAG Pipeline (pipeline.py)     │  │
│  │                                   │  │
│  │  1. Check Query Cache ───────┐   │  │
│  │  2. Embed Query              │   │  │
│  │  3. Hybrid Search            │   │  │
│  │     ├─ Lexical (BM25)        │   │  │
│  │     └─ Semantic (Vector)     │   │  │
│  │  4. RRF Fusion               │   │  │
│  │  5. Rerank (Cohere)          │   │  │
│  │  6. LLM Generation           │   │  │
│  │  7. Format Response          │   │  │
│  └───────────────────────────────┘   │
└───────────────────────────────────────┘
       │
       │ Reads
       ▼
┌─────────────────────────────────────────┐
│         Storage Layer                   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │  ChromaDB    │  │  BM25 Index  │   │
│  │  (Vector DB) │  │  (In-Memory) │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Embed Cache  │  │ Query Cache  │   │
│  │  (24h TTL)   │  │  (5m TTL)    │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐                      │
│  │  index.state │                      │
│  │  (Hash)      │                      │
│  └──────────────┘                      │
└─────────────────────────────────────────┘

Ingestion Flow (One-Time):
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ CSV Files│ ───> │  Loader  │ ───> │ Embedder │ ───> │  Indexes │
│          │      │          │      │ (BGE-M3) │      │          │
└──────────┘      └──────────┘      └──────────┘      └──────────┘
                           │
                           ▼
                    Numerical → Text
                    {"sharpe": 1.25}
                    → "Fund has Sharpe Ratio: 1.25..."
```

## C. File-to-Pipeline Mapping

| Pipeline Component | Files |
|-------------------|-------|
| **Data Ingestion** | `scripts/ingest_data.py`, `core/ingestion/loader.py` |
| **Embedding** | `core/ingestion/embedder.py` |
| **Vector Storage** | `core/retrieval/semantic.py`, `services/vector_store.py` |
| **Lexical Index** | `core/retrieval/lexical.py` |
| **Hybrid Search** | `core/retrieval/hybrid.py` |
| **Reranking** | `core/retrieval/reranker.py` |
| **LLM Generation** | `core/generation/llm.py`, `core/generation/prompts.py` |
| **Pipeline Orchestration** | `core/orchestration/pipeline.py` |
| **Caching** | `services/cache.py` |
| **API Layer** | `api/v1/query.py`, `api/schemas/query.py` |

---

# 4. Interview Questions & Answers

## Architecture Questions

### Q: Why did you choose a hybrid search approach instead of just vector search?

**A**: Financial queries need both exact keyword matching and semantic understanding. For example, "Axis Bluechip Fund" requires exact matching (lexical), while "safe funds with good returns" needs semantic understanding. Hybrid search using RRF (Reciprocal Rank Fusion) combines both - BM25 handles exact matches, vector search handles concepts. We run both searches in parallel for 40-50% latency reduction. RRF is rank-based, so it doesn't require score normalization between different scoring systems.

---

### Q: Why ChromaDB instead of Qdrant, Pinecone, or Weaviate?

**A**: For MVP, ChromaDB offers simplicity - in-process Python library, no separate server to manage, built-in persistence. It's sufficient for our scale (thousands of documents). We can swap it later if needed - our `VectorStoreService` abstraction makes migration easy. For production at larger scale, we'd evaluate Qdrant or Pinecone for better performance and features.

---

### Q: Why BGE-M3 for embeddings instead of OpenAI embeddings or other models?

**A**: BGE-M3 is free, open-source, and performs excellently on benchmarks. It's multilingual (important for Indian market), has 1024 dimensions (good balance of quality vs. storage), and runs locally (no API costs, no rate limits). OpenAI embeddings are great but add cost and latency. We can swap models easily - the `Embedder` class abstracts the model details.

---

### Q: Explain your caching strategy and why you chose it.

**A**: Two-tier caching. **Embedding cache (24h TTL)**: Same text never embedded twice - saves expensive model inference. **Query cache (5m TTL)**: Full pipeline results cached - repeated questions get instant responses. In-memory for MVP simplicity, but structured for Redis migration. Cache keys use SHA-256 hashes for exact matching. First query is 2-4s, cached queries are ~50ms - 100x faster.

---

### Q: How do you handle numerical data in RAG? Embeddings struggle with numbers.

**A**: We convert structured metrics to semantic text during ingestion. Instead of embedding `{"sharpe": 1.25}`, we create text like "Fund X has excellent risk-adjusted returns with Sharpe Ratio of 1.25". This enables semantic queries like "safe funds" to find high Sharpe ratios through meaning, not exact numbers. This numerical-to-text transformation is the key innovation that makes semantic search work for financial data.

---

## Design Decisions

### Q: Why is reranking optional? What happens if Cohere API fails?

**A**: Graceful degradation. Reranking improves precision but isn't required. If Cohere API is down or key missing, we return hybrid search results directly. System never breaks - we log a warning and continue. This improves developer experience and production resilience.

---

### Q: Explain your hash-based persistence strategy.

**A**: On startup, we calculate MD5 hash of CSV files + embedding model config. Compare to saved hash in `index.state`. If match, load existing ChromaDB from disk (5-10s startup). If different, re-index (2-4min). This gives fast development cycles - data changes trigger re-index automatically, no manual cache invalidation. If persistence corrupted, we fall back to re-indexing.

---

### Q: Why in-memory cache instead of Redis from the start?

**A**: Simplicity for MVP. No external dependencies, easier local development. The cache interface is abstracted - swapping to Redis just means changing the `InMemoryCache` implementation. We prioritized getting to market fast, with clear upgrade path for production.

---

### Q: Why FastAPI instead of Flask or Django?

**A**: FastAPI gives async support out of the box, automatic OpenAPI docs, Pydantic validation, and excellent performance. Our pipeline is I/O bound (API calls, embeddings), so async helps. Pydantic models provide type safety and validation automatically. The OpenAPI docs help frontend developers.

---

### Q: Why Next.js App Router instead of Pages Router?

**A**: App Router is the modern Next.js pattern - better for React Server Components, streaming, and layout sharing. It's the future of Next.js, so we built for longevity. The chat interface benefits from App Router's improved data fetching patterns.

---

## Vector DB & Indexing

### Q: How does ChromaDB index work? What algorithm does it use?

**A**: ChromaDB uses HNSW (Hierarchical Navigable Small World) for approximate nearest neighbor search. It builds a graph where similar vectors are connected, allowing fast traversal. It's approximate - trades some accuracy for speed. For our scale, it's more than accurate enough. ChromaDB handles the index construction and persistence automatically.

---

### Q: Why did you choose cosine similarity over dot product or Euclidean distance?

**A**: Cosine similarity measures angle between vectors, which works well for normalized embeddings. It ignores magnitude, focusing on direction - perfect for semantic similarity where we care about meaning, not vector length. ChromaDB uses cosine by default for normalized embeddings, which matches our embedding normalization.

---

### Q: How do you handle metadata filtering in ChromaDB?

**A**: ChromaDB supports metadata filtering in the `where` clause. We store source type (faq/fund), category, fund_name, etc. as metadata. Queries can filter by metadata before similarity search - useful for "only search FAQs" or "only Large Cap funds". This combines semantic search with structured filtering.

---

## Reranking

### Q: What's the difference between bi-encoder and cross-encoder reranking?

**A**: Bi-encoder (our initial search) encodes query and documents separately, then compares embeddings. Fast but less accurate. Cross-encoder (Cohere reranker) sees query + document together, makes a relevance judgment. More accurate but slower - can't pre-compute document embeddings. We use both - fast bi-encoder for retrieval, accurate cross-encoder for reranking top results.

---

### Q: Why Cohere reranker specifically?

**A**: Cohere's rerank model is state-of-the-art, easy API integration, and works well for financial/technical content. Alternatives exist (Jina, custom models), but Cohere is reliable and requires no training. We can swap it easily - the `Reranker` class abstracts the implementation.

---

## LLM & Generation

### Q: Why Claude 3 Opus instead of GPT-4 or open-source models?

**A**: Claude Opus provides excellent quality for financial content, handles long contexts well, and has good safety guardrails (important for financial advice). Temperature is low (0.3) for factual accuracy. We can swap models - the `LLMGenerator` class abstracts API details. For production, we'd evaluate cost vs. quality tradeoffs.

---

### Q: How do you prevent hallucination in financial advice?

**A**: Multiple strategies: (1) Context-only prompting - "answer ONLY from provided context", (2) System prompt explicitly says "never give specific investment advice", (3) Source attribution in responses, (4) Low temperature (0.3) for factual responses, (5) Confidence scores from retrieval quality. The RAG architecture helps - if context doesn't contain answer, model should say so.

---

### Q: How do you handle prompt engineering for different query types?

**A**: We have three prompt templates - FAQ (conceptual), Numerical (metrics-focused), Hybrid (combined). The pipeline classifies query type using keyword matching, then selects appropriate template. FAQ prompts emphasize explanation, numerical prompts emphasize metrics with formatting. This helps Claude generate better-formatted answers.

---

## Evaluation & Quality

### Q: How do you evaluate RAG quality? Do you use RAGAS?

**A**: We have an evaluation script (`scripts/evaluate.py`) that can use RAGAS metrics - faithfulness, answer relevancy, context precision, etc. For MVP, we also do manual evaluation on key queries. In production, we'd track user feedback, answer quality scores, and retrieval metrics. The evaluation suite compares different search modes (lexical vs semantic vs hybrid).

---

### Q: How do you measure retrieval quality?

**A**: Multiple metrics: (1) Precision at k - are top results relevant?, (2) Recall - did we find all relevant docs?, (3) MRR (Mean Reciprocal Rank) - where is first relevant result?, (4) Coverage - what % of corpus is retrieved over time? We track these in evaluation, would add production monitoring.

---

## Optimization & Performance

### Q: How did you optimize latency?

**A**: Multiple optimizations: (1) Parallel hybrid search (40-50% faster), (2) Multi-level caching (100x faster for cache hits), (3) Hash-based persistence (avoids re-indexing), (4) Batch embedding processing, (5) Lazy loading of models. First query is 2-4s, cached queries are ~50ms. We could add more - streaming responses, async batch processing, model quantization.

---

### Q: How would you scale this to handle 1000x more documents?

**A**: (1) Vector DB: Move to Qdrant/Pinecone with horizontal scaling, (2) Cache: Redis cluster with sharding, (3) Embedding: GPU batch processing, model quantization, (4) Retrieval: Distributed search, approximate search tuning, (5) LLM: Response streaming, caching, batch generation, (6) Infrastructure: Kubernetes, load balancing, CDN for static assets. Current architecture supports this - just swap implementations.

---

### Q: What's your latency vs accuracy tradeoff?

**A**: For retrieval: We fetch 3x more documents initially (fetch_k = top_k * 3), then rerank to top-k. This improves recall while keeping latency manageable. For embeddings: We use high-quality model (BGE-M3) for accuracy, cache aggressively for latency. For LLM: Low temperature (0.3) prioritizes accuracy over creativity. We could reduce latency (smaller models, fewer docs) but prefer accuracy for financial domain.

---

# 5. Failure Points & Improvements

## What Can Go Wrong

### 1. **Vector Store Corruption**
- **Risk**: ChromaDB persistence files corrupted
- **Impact**: Cannot load indexes, must re-index
- **Mitigation**: Hash-based change detection falls back to re-indexing automatically

### 2. **Embedding Model Download Failure**
- **Risk**: First-time model download fails or is slow
- **Impact**: Pipeline initialization fails
- **Mitigation**: Fallback to smaller model (all-MiniLM-L6-v2), retry logic

### 3. **API Rate Limiting**
- **Risk**: Anthropic/Cohere API rate limits hit
- **Impact**: Queries fail
- **Mitigation**: Add retry with exponential backoff, request queuing, rate limit monitoring

### 4. **Memory Issues**
- **Risk**: Large embedding model + cache + indexes exceed memory
- **Impact**: OOM errors, crashes
- **Mitigation**: Model quantization, cache size limits, LRU eviction, separate embedding service

### 5. **Cache Stampede**
- **Risk**: Many requests for same uncached query simultaneously
- **Impact**: Multiple expensive computations
- **Mitigation**: Request deduplication, lock-based single computation

### 6. **Data Quality Issues**
- **Risk**: CSV files have missing/invalid data
- **Impact**: Poor retrieval quality, incorrect answers
- **Mitigation**: Data validation in loader, schema validation, error reporting

### 7. **Embedding Drift**
- **Risk**: Model produces different embeddings after update
- **Impact**: Existing indexes become inconsistent
- **Mitigation**: Version embeddings, model versioning, re-index on model change

## How to Scale

### Short Term (10x documents)
1. **Vector DB**: Keep ChromaDB, optimize index parameters
2. **Cache**: Move to Redis for shared cache across instances
3. **Embedding**: GPU acceleration, batch size tuning
4. **Infrastructure**: Horizontal scaling with load balancer

### Medium Term (100x documents)
1. **Vector DB**: Migrate to Qdrant with distributed mode
2. **Embedding Service**: Separate microservice with GPU cluster
3. **Caching**: Redis cluster with consistent hashing
4. **Retrieval**: Distributed search, approximate search tuning
5. **Monitoring**: Full observability stack (Prometheus, Grafana)

### Long Term (1000x documents)
1. **Architecture**: Microservices (ingestion, retrieval, generation)
2. **Vector DB**: Managed service (Pinecone/Qdrant Cloud) or self-hosted cluster
3. **LLM**: Multiple providers, fallbacks, streaming responses
4. **Infrastructure**: Kubernetes, auto-scaling, multi-region
5. **Advanced**: Query routing, A/B testing, personalization

## Why This Design is Good

1. **Modular**: Each component is isolated, easy to test and swap
2. **Graceful Degradation**: Optional components (reranker) don't break system
3. **Developer Experience**: Fast startup, clear errors, good documentation
4. **Performance**: Caching, parallel search, smart persistence
5. **Extensibility**: Easy to add new search modes, models, features
6. **Type Safety**: Pydantic + TypeScript ensure correctness
7. **Observability**: Logging, health checks, structured responses

## Best-Practice Improvements

### Immediate (Next Sprint)
1. **Error Handling**: More specific error types, better error messages
2. **Logging**: Structured JSON logging, request IDs, trace context
3. **Testing**: Unit tests for all components, integration tests for pipeline
4. **Documentation**: API docs, deployment guides, troubleshooting

### Short Term (Next Month)
1. **Monitoring**: Metrics (latency, error rates, cache hit rates)
2. **Redis Cache**: Migrate from in-memory to Redis
3. **Validation**: Data quality checks, schema validation
4. **Security**: API authentication, rate limiting, input sanitization

### Medium Term (Next Quarter)
1. **Streaming**: Stream LLM responses for better UX
2. **Evaluation**: Automated RAG quality monitoring
3. **A/B Testing**: Test different retrieval strategies
4. **Optimization**: Model quantization, batch optimization

### Long Term (Future)
1. **Advanced RAG**: Query rewriting, multi-hop retrieval, self-RAG
2. **Personalization**: User-specific retrieval, preference learning
3. **Multi-modal**: Support images, charts, PDFs
4. **Fine-tuning**: Fine-tune embedding model on financial domain

---

# 6. Human-Speak Explanation

## Simple English Overview

This is a financial search system. Users ask questions like "Which funds have the best returns?" and get answers backed by data.

**How it works:**

1. **Load the data**: We read CSV files with fund information and FAQs
2. **Make it searchable**: Convert text to numbers (embeddings) that capture meaning
3. **Store it**: Save these numbers in a database for fast searching
4. **Search when asked**: When a question comes in, search for relevant information
5. **Generate answer**: Use AI to write a natural answer from the found information

**The clever parts:**

- **Hybrid search**: Uses two methods - exact word matching AND meaning matching. Combines both for best results.
- **Smart caching**: If we've seen this question before, answer instantly. If we've embedded this text before, reuse it.
- **Fast startup**: If data hasn't changed, skip expensive setup steps.
- **Graceful failures**: If optional services fail, system still works.

**Why it's good:**

- Fast: Cached queries answer in milliseconds
- Accurate: Finds relevant information using meaning, not just keywords
- Reliable: Handles failures gracefully
- Extensible: Easy to add new features or swap components

## 90-Second Project Explanation

"I built a RAG system for financial intelligence. Users ask natural language questions about mutual funds, and the system retrieves relevant data and generates answers.

The architecture has four layers: ingestion, indexing, retrieval, and generation. During ingestion, we load CSV files and convert structured fund metrics into semantic text - this is key because embedding models struggle with raw numbers. We generate embeddings using BGE-M3 and store them in ChromaDB for vector search, plus build a BM25 index for keyword search.

At query time, we run both searches in parallel and combine results using Reciprocal Rank Fusion - this gives us exact matches plus semantic understanding. We optionally rerank with Cohere for better precision, then pass the context to Claude 3 Opus to generate a natural answer.

The system includes multi-level caching - embedding cache for expensive model inference, query cache for instant repeated answers. Hash-based persistence means we skip re-indexing if data hasn't changed, reducing startup from minutes to seconds.

Performance: First query is 2-4 seconds, cached queries are 50 milliseconds. The hybrid search approach provides better accuracy than either method alone, and graceful degradation ensures the system works even if optional services fail."

## 30-Second Elevator Pitch

"I built a RAG system that answers questions about mutual funds using hybrid search - combining keyword and semantic matching for accuracy. Key innovations: converting numerical metrics to semantic text for better search, parallel hybrid retrieval for speed, and multi-level caching that makes repeated queries 100x faster. The system handles structured financial data alongside FAQs, with graceful degradation and smart persistence for fast development cycles."

---

# 7. Quick Reference

## Key Metrics

| Metric | Value |
|--------|-------|
| First Query Latency | 2-4 seconds |
| Cached Query Latency | ~50ms |
| Embedding Cache Hit | ~10ms |
| Startup (No Changes) | 5-10 seconds |
| Startup (Re-index) | 2-4 minutes |
| Parallel vs Sequential | 40-50% faster |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 16 (TypeScript) |
| Embeddings | BGE-M3 (1024-dim) |
| Vector DB | ChromaDB |
| LLM | Claude 3 Opus |
| Reranker | Cohere |
| Lexical Search | BM25 |

## Key Files Cheat Sheet

| Purpose | File |
|---------|------|
| Main Pipeline | `backend/app/core/orchestration/pipeline.py` |
| Hybrid Search | `backend/app/core/retrieval/hybrid.py` |
| Data Loading | `backend/app/core/ingestion/loader.py` |
| Embeddings | `backend/app/core/ingestion/embedder.py` |
| LLM Generation | `backend/app/core/generation/llm.py` |
| Query Endpoint | `backend/app/api/v1/query.py` |
| Caching | `backend/app/services/cache.py` |

## Common Interview Questions Checklist

- [ ] Why hybrid search?
- [ ] Why ChromaDB?
- [ ] Why BGE-M3?
- [ ] How do you handle numerical data?
- [ ] Explain caching strategy
- [ ] Hash-based persistence?
- [ ] Why optional reranking?
- [ ] How do you prevent hallucinations?
- [ ] How would you scale this?
- [ ] Latency vs accuracy tradeoffs?

---

**End of Master Interview Document**

*This document provides comprehensive coverage of the Qonfido RAG project for senior-level interviews. Review each section, practice explaining key concepts, and be ready to dive deep into any component.*

