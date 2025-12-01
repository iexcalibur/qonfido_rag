# Deep Architecture

Comprehensive technical architecture documentation covering all subsystems, design decisions, and implementation details.

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐      │
│  │  Next.js Web    │  │  Mobile App     │  │  API Clients        │      │
│  │  Application    │  │  (Future)       │  │  (External)         │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘      │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ HTTP/REST
┌───────────────────────────────▼──────────────────────────────────────────┐
│                           API GATEWAY LAYER                               │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Application                           │    │
│  │  ├─ Request Validation (Pydantic)                               │    │
│  │  ├─ Authentication/Authorization (if implemented)                │    │
│  │  ├─ Rate Limiting (if implemented)                              │    │
│  │  └─ CORS Middleware                                             │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                        APPLICATION LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    RAG Pipeline Orchestrator                     │    │
│  │                                                                  │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │    │
│  │  │  Query     │→ │  Retrieve  │→ │  Rerank    │→ │ Generate │ │    │
│  │  │  Processing│  │  Documents │  │  Results   │  │  Answer  │ │    │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                         RETRIEVAL LAYER                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Lexical Search  │  │  Semantic Search │  │  Hybrid Search       │  │
│  │  (BM25)          │  │  (Vector)        │  │  (RRF Fusion)        │  │
│  │                  │  │                  │  │                      │  │
│  │  - Tokenization  │  │  - Embedding     │  │  - Parallel Exec     │  │
│  │  - TF-IDF        │  │  - Similarity    │  │  - RRF Algorithm     │  │
│  │  - Ranking       │  │  - Ranking       │  │  - Result Fusion     │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                         DATA LAYER                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  CSV Files   │  │  Vector Store│  │  BM25 Index  │  │  Cache      │ │
│  │  (FAQs,      │  │  (ChromaDB)  │  │  (In-Memory) │  │  (Redis/    │ │
│  │   Funds)     │  │              │  │              │  │   In-Memory)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│  ┌──────────────┐                                                       │
│  │  Database    │                                                       │
│  │  (PostgreSQL/│                                                       │
│  │   SQLite)    │                                                       │
│  └──────────────┘                                                       │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                      EXTERNAL SERVICES LAYER                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Claude API      │  │  Cohere API      │  │  Embedding Model     │  │
│  │  (Anthropic)     │  │  (Reranking)     │  │  (HuggingFace)       │  │
│  │                  │  │                  │  │                      │  │
│  │  - Generation    │  │  - Reranking     │  │  - BGE-M3            │  │
│  │  - Sonnet/Opus   │  │  - Relevance     │  │  - Sentence          │  │
│  │  - Answer        │  │  - Scoring       │  │    Transformers      │  │
│  │    Synthesis     │  │                  │  │                      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Core Subsystems

### 1. Data Ingestion System

**Purpose:** Transform raw CSV data into indexed, searchable documents.

#### Components

**DataLoader** (`core/ingestion/loader.py`)
- **Responsibility:** Load and parse CSV files
- **Input:** CSV files (faqs.csv, funds.csv)
- **Output:** Structured data models (FAQItem, FundData)

**Key Features:**
- Flexible column name matching (handles variations)
- Missing data handling
- Type conversion (strings → numbers)
- Data validation via Pydantic models

**Text Conversion:**
- FundData → Rich text description:
  ```
  "Fund Name: XYZ Fund
   Fund House: ABC AMC
   Performance: 3-year CAGR: 12.50%, 5-year CAGR: 15.20%
   Risk Metrics: Sharpe Ratio: 1.25, Volatility: 8.50%
   Risk Level: Moderate
   AUM: ₹1000.50 Cr"
  ```

**Embedder** (`core/ingestion/embedder.py`)
- **Responsibility:** Generate vector embeddings
- **Model:** BGE-M3 (default, 1024 dimensions)
- **Features:**
  - Lazy model loading
  - Batch processing
  - Embedding caching (24hr TTL)
  - Fallback to smaller model if primary fails

**Output:** Document embeddings (numpy arrays, shape: [num_docs, 1024])

---

### 2. Retrieval System

**Purpose:** Find relevant documents based on user queries.

#### 2.1 Lexical Search (BM25)

**Implementation:** `core/retrieval/lexical.py`

**Algorithm:** BM25 (Best Matching 25)
- TF-IDF based ranking
- Handles term frequency and inverse document frequency
- Good for exact keyword matching

**Process:**
1. Tokenize query and documents
2. Build BM25 index (term frequencies)
3. Score documents for query
4. Rank by score
5. Return top-k results

**Strengths:**
- Fast execution
- Good for exact matches
- Handles fund names and technical terms well

**Limitations:**
- Cannot handle semantic similarity
- Misses paraphrased queries

---

#### 2.2 Semantic Search (Vector)

**Implementation:** `core/retrieval/semantic.py`

**Vector Store:** ChromaDB
- In-process (no server needed)
- Cosine similarity search
- HNSW indexing for fast retrieval

**Process:**
1. Generate query embedding
2. Vector similarity search (cosine distance)
3. Rank by similarity score
4. Return top-k results

**Strengths:**
- Handles semantic similarity
- Works with paraphrased queries
- Understands context and concepts

**Limitations:**
- Slower than BM25
- Requires embedding computation

---

#### 2.3 Hybrid Search

**Implementation:** `core/retrieval/hybrid.py`

**Algorithm:** Reciprocal Rank Fusion (RRF)
- Combines ranked lists from lexical + semantic
- Formula: `RRF_score = Σ (1 / (k + rank_i))`
- k = 60 (tunable constant)

**Process:**
1. Run lexical and semantic searches in parallel (ThreadPoolExecutor)
2. Get ranked lists from each
3. Assign RRF scores to documents appearing in either list
4. Combine scores: `(1-α) * lexical_RRF + α * semantic_RRF`
5. Sort by combined score
6. Return top-k results

**Parallel Execution:**
- Both searches run simultaneously
- ~40-50% faster than sequential
- Uses ThreadPoolExecutor (2 workers)

**Strengths:**
- Best of both worlds (keyword + semantic)
- Outperforms either method alone
- Faster with parallel execution

**Trade-offs:**
- More complex implementation
- Requires both indexes

---

#### 2.4 Reranking (Optional)

**Implementation:** `core/retrieval/reranker.py`

**Service:** Cohere Rerank API
- Two-stage retrieval pattern
- Cross-encoder model for accuracy
- Optional component (graceful fallback)

**Process:**
1. Retrieve candidates (top-k * 3)
2. Send query + documents to Cohere API
3. Get relevance scores
4. Reorder by rerank scores
5. Return top-k reranked results

**Strengths:**
- More accurate than single-stage retrieval
- Better ranking quality

**Trade-offs:**
- Adds latency (API call)
- Requires API key
- Additional cost

---

### 3. Generation System

**Purpose:** Generate natural language answers from retrieved context.

#### Components

**LLMGenerator** (`core/generation/llm.py`)
- **Model:** Claude (Anthropic API)
- **Default:** claude-3-opus-20240229
- **Configuration:**
  - Max tokens: 1024
  - Temperature: 0.3 (lower = more deterministic)

**Prompt Engineering:**
- System prompt: Defines assistant role and behavior
- Context formatting: Structured context with source attribution
- User message: Query + formatted context

**Process:**
1. Format retrieved documents as context
2. Build prompt with system + user message
3. Call Claude API
4. Extract generated text
5. Return answer string

**Prompt Templates** (`core/generation/prompts.py`):
- Different templates for FAQ vs numerical queries
- Instructions for including metrics
- Source attribution requirements

---

### 4. Orchestration Layer

**Purpose:** Coordinate all subsystems in the RAG pipeline.

#### RAGPipeline (`core/orchestration/pipeline.py`)

**Responsibilities:**
- Pipeline initialization
- Query processing coordination
- Caching management
- Response assembly

**Key Methods:**

**`initialize()`**
- Load data from CSV
- Generate embeddings
- Build lexical and semantic indexes
- Ready for queries

**`process()`**
- End-to-end query processing:
  1. Check query cache
  2. Embed query
  3. Retrieve documents
  4. Rerank (optional)
  5. Generate answer
  6. Classify query type
  7. Extract fund info
  8. Build response
  9. Cache result

**Query Classification:**
- Analyzes query keywords and result sources
- Categories: "faq", "numerical", "hybrid"
- Used for response formatting

**Fund Information Extraction:**
- Extracts fund metrics from result metadata
- Falls back to full fund cache if metadata incomplete
- Limits to top 5 funds

---

### 5. Caching System

**Purpose:** Improve performance by avoiding redundant computations.

#### Components

**EmbeddingCache** (`services/cache.py`)
- **TTL:** 24 hours
- **Key:** SHA-256 hash of text
- **Value:** NumPy array (embedding vector)
- **Purpose:** Avoid recomputing embeddings for same text

**QueryCache** (`services/cache.py`)
- **TTL:** 5 minutes
- **Key:** MD5 hash of (query + mode + top_k + source_filter)
- **Value:** Serialized QueryResponse
- **Purpose:** Instant responses for repeated queries

**Implementation:**
- Redis cache (production) with automatic fallback to in-memory cache (development)
- Thread-safe in-memory cache with RLock and LRU eviction
- Automatic expiration cleanup
- Case-insensitive query normalization for cache keys
- Reads REDIS_URL from environment variables

**Cache Stats:**
- Track cache hits/misses
- Monitor cache size
- Exposed via pipeline.cache_stats

---

### 6. API Layer

**Purpose:** RESTful API endpoints for client interaction.

#### FastAPI Application (`main.py`)

**Features:**
- OpenAPI/Swagger documentation
- Request validation (Pydantic)
- Error handling
- CORS middleware
- Lifespan management

#### Endpoints

**`POST /api/v1/query`**
- Main RAG query endpoint
- Input: QueryRequest (query, search_mode, top_k, rerank)
- Output: QueryResponse (answer, funds, sources, confidence)

**`GET /api/v1/funds`**
- List all funds with optional filtering
- Query params: category, risk_level, limit

**`GET /api/v1/funds/{id}`**
- Get fund details by ID

**`GET /api/v1/health`**
- Health check endpoint
- Returns: status, version, environment

**`GET /api/v1/search-modes`**
- List available search modes with descriptions

---

## 🔧 Design Decisions

### Technology Choices

#### Why ChromaDB over Qdrant/FAISS?
- **Simplicity:** No server process needed (in-process)
- **Development speed:** Faster local setup
- **Sufficient scale:** Good for MVP scale
- **Trade-off:** Less scalable than Qdrant, but simpler

#### Why BGE-M3 over OpenAI embeddings?
- **Cost:** Free (local model)
- **Privacy:** No data sent to external API
- **Hybrid support:** Dense embeddings work with hybrid search
- **Trade-off:** Larger model size, slower initial load

#### Why BM25 over TF-IDF only?
- **Better ranking:** BM25 is improved TF-IDF
- **Handles term saturation:** Better for repeated terms
- **Standard:** Industry standard for lexical search
- **Trade-off:** Slightly more complex

#### Why RRF over other fusion methods?
- **Simplicity:** Easy to implement
- **Effectiveness:** Works well in practice
- **No training:** No model needed
- **Trade-off:** Less sophisticated than learned fusion

#### Why Redis with Automatic Fallback?
- **Production:** Redis provides persistent, distributed caching
- **Development:** Automatic fallback to in-memory cache (no setup needed)
- **Reliability:** System works even if Redis is unavailable
- **Best of both worlds:** Production scalability with development simplicity
- **Trade-off:** Requires Redis setup for production (but optional for dev)

---

## 📐 Architectural Patterns

### 1. Layered Architecture

```
API Layer (Request/Response)
    ↓
Application Layer (Business Logic)
    ↓
Domain Layer (Core Components)
    ↓
Infrastructure Layer (External Services)
```

**Benefits:**
- Clear separation of concerns
- Easy to test
- Easy to swap implementations

### 2. Dependency Injection

- Global getter functions (`get_pipeline()`, `get_embedder()`, etc.)
- Lazy initialization
- Singleton pattern

**Trade-off:** Could use FastAPI dependency injection for better testability

### 3. Pipeline Pattern

- Sequential processing stages
- Each stage transforms input
- Clear flow: Query → Retrieve → Generate → Response

**Benefits:**
- Easy to understand
- Easy to add/remove stages
- Good for debugging

### 4. Strategy Pattern

- Multiple retrieval strategies (Lexical, Semantic, Hybrid)
- Swappable at runtime
- Same interface, different implementations

**Benefits:**
- Easy to add new strategies
- Easy to compare strategies
- Flexible configuration

---

## 🔐 Security Considerations

### API Key Management
- Environment variables (not in code)
- Pydantic SecretStr (no logging of keys)
- Validation on startup

### Input Validation
- Pydantic schemas validate all inputs
- Query length limits
- Type checking

### Error Handling
- Don't expose internal errors to clients
- Log errors internally
- Return safe error messages

### CORS Configuration
- Currently: `allow_origins=["*"]`
- **Production:** Restrict to specific domains

---

## 📊 Performance Characteristics

### Latency Breakdown

| Stage | Time (ms) | Notes |
|-------|-----------|-------|
| Query Embedding (cache hit) | ~10 | Cached |
| Query Embedding (cache miss) | ~50-100 | BGE-M3 |
| Lexical Search | ~5-20 | BM25 |
| Semantic Search | ~50-150 | ChromaDB |
| Hybrid Search (parallel) | ~50-150 | Both in parallel |
| Reranking | ~200-500 | Cohere API call |
| LLM Generation | ~1000-3000 | Claude API |
| **Total (cached query)** | **~50** | Query cache hit |
| **Total (first query)** | **~2000-4000** | Full pipeline |

### Scalability Considerations

**Current Limitations:**
- In-memory indexes (not distributed)
- Single instance (no load balancing)
- In-process ChromaDB (not shared)

**Scaling Options:**
1. **Horizontal Scaling:**
   - Multiple API instances behind load balancer
   - Shared vector store (ChromaDB server or Qdrant)
   - Shared cache (Redis)

2. **Optimization:**
   - Async/await for I/O operations
   - Connection pooling
   - Batch processing

3. **Caching:**
   - Aggressive caching (longer TTLs)
   - CDN for static assets
   - Database query caching

---

## 🧪 Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on core logic

### Integration Tests
- Test component interactions
- Test API endpoints
- Use test fixtures

### Evaluation Tests
- Test end-to-end queries
- Measure accuracy metrics
- Compare search modes

---

## 🔄 Extension Points

### Adding New Retrieval Methods
1. Implement searcher interface
2. Add to SearchMode enum
3. Integrate into pipeline.process()

### Adding New Data Sources
1. Extend DataLoader
2. Create new data model
3. Update document format

### Adding New LLM Providers
1. Implement generator interface
2. Add configuration
3. Update pipeline

### Adding Authentication
1. Add FastAPI security dependencies
2. Implement token validation
3. Protect endpoints

---

For data flow details, see [Data Flow](./DATA_FLOW.md).  
For project structure, see [Project Structure](./PROJECT_STRUCTURE.md).  
For implementation details, see [Backend Documentation](./BACKEND_DOCUMENTATION.md) and [Frontend Documentation](./FRONTEND_DOCUMENTATION.md).

