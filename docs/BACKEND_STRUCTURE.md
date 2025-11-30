# Backend Structure

Overview of the backend folder organization and component responsibilities.

## 📁 Directory Structure

```
backend/
├── app/                          # Main application package
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   │
│   ├── api/                     # REST API Layer
│   │   ├── schemas/             # Request/Response models
│   │   └── v1/                  # Version 1 API endpoints
│   │
│   ├── core/                    # Core Business Logic
│   │   ├── ingestion/           # Data loading & embedding
│   │   ├── retrieval/           # Search implementations
│   │   ├── generation/          # LLM integration
│   │   └── orchestration/       # Pipeline coordination
│   │
│   ├── db/                      # Database Layer
│   ├── services/                # External service integrations
│   └── utils/                   # Utility functions
│
├── data/                        # Data files
│   ├── raw/                     # Raw CSV files (FAQs, Funds)
│   └── processed/               # Processed data (if any)
│
├── scripts/                     # Utility scripts
├── tests/                       # Test suite
└── requirements.txt             # Python dependencies
```

---

## 📦 Core Components

### `app/` - Main Application

#### `main.py`
- FastAPI application instance
- Application lifespan management (startup/shutdown)
- CORS middleware configuration
- Route registration

**Key Responsibilities:**
- Initialize RAG pipeline on startup
- Load fund data cache
- Configure API routes

#### `config.py`
- Centralized configuration management
- Environment variable loading via Pydantic Settings
- Default values and validation
- Configuration properties (API keys, model settings, paths)

---

### `app/api/` - REST API Layer

#### `api/schemas/`
Request and response models using Pydantic:

- **`common.py`**: Shared schemas (Health, Pagination, Error)
- **`query.py`**: Query request/response models (QueryRequest, QueryResponse, SearchMode)
- **`fund.py`**: Fund-related schemas (FundInfo, FundDetail)

**Purpose:** Type-safe request/response validation and serialization

#### `api/v1/`
Version 1 API endpoints:

- **`router.py`**: Main API router combining all endpoint routers
- **`query.py`**: RAG query endpoint (`POST /api/v1/query`)
- **`funds.py`**: Fund explorer endpoints (`GET /api/v1/funds`, `/funds/{id}`)
- **`health.py`**: Health check endpoint (`GET /api/v1/health`)

**Purpose:** RESTful API endpoints with request validation and error handling

---

### `app/core/` - Core Business Logic

#### `core/ingestion/`
Data loading and processing:

- **`loader.py`**:
  - Loads FAQs and fund data from CSV files
  - Flexible column name matching
  - Converts data to structured models (`FAQItem`, `FundData`)
  - Converts numerical fund metrics to searchable text

- **`embedder.py`**:
  - Embedding generation using sentence-transformers
  - BGE-M3 model (1024 dimensions, default)
  - Batch processing with progress bars
  - Embedding caching integration

**Purpose:** Transform raw CSV data into indexed, searchable documents

#### `core/retrieval/`
Search and retrieval implementations:

- **`lexical.py`**:
  - BM25 keyword-based search
  - Tokenization and indexing
  - Ranked results by keyword relevance

- **`semantic.py`**:
  - ChromaDB vector similarity search
  - Cosine similarity ranking
  - Metadata filtering support

- **`hybrid.py`**:
  - Combines lexical + semantic search
  - Reciprocal Rank Fusion (RRF) algorithm
  - Parallel retrieval for performance

- **`reranker.py`**:
  - Cohere reranking API integration
  - Two-stage retrieval (retrieve → rerank)
  - Optional component (graceful fallback)

**Purpose:** Multiple retrieval strategies for finding relevant documents

#### `core/generation/`
LLM response generation:

- **`llm.py`**:
  - Claude API integration
  - Context formatting
  - Response generation with prompts

- **`prompts.py`**:
  - Prompt templates for different query types
  - System prompts
  - Context formatting rules

**Purpose:** Generate natural language answers from retrieved context

#### `core/orchestration/`
RAG pipeline coordination:

- **`pipeline.py`**:
  - Main `RAGPipeline` class
  - Orchestrates: ingestion → retrieval → reranking → generation
  - Query caching
  - Query type classification
  - Fund information extraction

**Purpose:** End-to-end query processing pipeline

---

### `app/db/` - Database Layer

- **`models.py`**: SQLModel database models
- **`repositories.py`**: Data access layer (if used)
- **`session.py`**: Database connection management

**Purpose:** Persistent data storage (currently minimal usage)

---

### `app/services/` - External Services

- **`cache.py`**:
  - In-memory caching service
  - Embedding cache (24hr TTL)
  - Query cache (5min TTL)
  - TTL-based expiration

- **`vector_store.py`**: Vector store wrapper (if used)

**Purpose:** Caching and external service abstractions

---

### `app/utils/` - Utilities

- **`helpers.py`**: Common utility functions
- **`logging.py`**: Logging configuration and setup

**Purpose:** Shared utility functions and configurations

---

## 📂 Supporting Directories

### `data/`
- **`raw/`**: Raw CSV files (`faqs.csv`, `funds.csv`)
- **`processed/`**: Processed data (currently empty)

**Purpose:** Data file storage

### `scripts/`
Utility scripts for development and operations:

- **`ingest_data.py`**: Data ingestion and indexing
- **`seed_db.py`**: Database seeding
- **`evaluate.py`**: RAG evaluation and metrics
- **`test_query.py`**: Query testing tool

**Purpose:** Command-line tools for common operations

### `tests/`
Test suite organization:
- **`unit/`**: Unit tests
- **`integration/`**: Integration tests
- **`evaluation/`**: Evaluation tests

**Purpose:** Automated testing

---

## 🔄 Data Flow Through Backend

1. **Startup** (`main.py`):
   - Load configuration
   - Initialize RAG pipeline
   - Index documents

2. **Request** (`api/v1/query.py`):
   - Validate request schema
   - Call pipeline.process()

3. **Pipeline** (`core/orchestration/pipeline.py`):
   - Check query cache
   - Embed query
   - Retrieve documents
   - Rerank (optional)
   - Generate answer
   - Return response

4. **Response** (`api/v1/query.py`):
   - Serialize response
   - Return JSON

---

## 🎯 Design Principles

### Separation of Concerns
- **API Layer**: Request/response handling
- **Core Layer**: Business logic
- **Services Layer**: External integrations
- **Utils Layer**: Shared utilities

### Modularity
- Each component is self-contained
- Clear interfaces between components
- Easy to test and extend

### Configuration
- Centralized configuration in `config.py`
- Environment variable support
- Sensible defaults

### Error Handling
- Graceful degradation (e.g., reranker fallback)
- Comprehensive logging
- Clear error messages

---

## 📝 Key Files Reference

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `main.py` | Application entry | `create_app()`, `lifespan()` |
| `config.py` | Configuration | `Settings` |
| `api/v1/query.py` | Query endpoint | `query()` |
| `core/orchestration/pipeline.py` | Pipeline coordinator | `RAGPipeline` |
| `core/ingestion/loader.py` | Data loading | `DataLoader`, `FAQItem`, `FundData` |
| `core/ingestion/embedder.py` | Embeddings | `Embedder` |
| `core/retrieval/lexical.py` | BM25 search | `LexicalSearcher` |
| `core/retrieval/semantic.py` | Vector search | `SemanticSearcher` |
| `core/retrieval/hybrid.py` | Hybrid search | `HybridSearcher` |
| `core/generation/llm.py` | LLM generation | `LLMGenerator` |
| `services/cache.py` | Caching | `EmbeddingCache`, `QueryCache` |

---

For detailed technical architecture, see [Deep Architecture](deep-architecture.md).

