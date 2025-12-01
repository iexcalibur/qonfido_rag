# Architecture & Design Decisions

This document provides a comprehensive overview of the Qonfido RAG system's architecture, design rationale, trade-off decisions, and scalability considerations.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Design Reasoning](#design-reasoning)
3. [Trade-off Decisions](#trade-off-decisions)
4. [Scalability Thinking](#scalability-thinking)
5. [Justification of Choices](#justification-of-choices)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  Next.js Frontend (React/TypeScript) + Tailwind CSS                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────────────┐
│                      API GATEWAY LAYER                               │
│  FastAPI Application (Python 3.12+)                                 │
│  ├─ Request Validation (Pydantic)                                   │
│  ├─ CORS Middleware                                                 │
│  └─ Lifespan Management                                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                   APPLICATION/ORCHESTRATION LAYER                    │
│  RAG Pipeline Orchestrator                                          │
│  ├─ Query Processing                                                │
│  ├─ Caching Management                                              │
│  ├─ Response Assembly                                               │
│  └─ State Management (Hash-based Persistence)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      RETRIEVAL LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Lexical      │  │ Semantic     │  │ Hybrid       │             │
│  │ (BM25)       │  │ (Vector)     │  │ (RRF Fusion) │             │
│  │ In-Memory/Redis│  │ ChromaDB     │  │ Parallel     │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  Optional: Cohere Reranker (Cross-Encoder)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      GENERATION LAYER                                │
│  Anthropic Claude API (Sonnet default, Opus fallback)              │
│  ├─ Prompt Engineering                                              │
│  ├─ Context Formatting                                              │
│  └─ Response Generation                                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                        DATA LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  │ CSV Files    │  │ Vector Store │  │ Redis/In-Mem │  │ PostgreSQL/ │
│  │ (FAQs/Funds) │  │ (ChromaDB)   │  │ Cache        │  │ SQLite      │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
└─────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

#### 1. **Layered Architecture**
- **Separation of Concerns**: Each layer has a distinct responsibility
- **Benefits**: Easy to test, maintain, and swap implementations
- **Flow**: Client → API → Application → Domain → Infrastructure

#### 2. **Pipeline Pattern**
- **Sequential Processing**: Query → Retrieve → Generate → Respond
- **Benefits**: Clear data flow, easy debugging, modular stages
- **Implementation**: `RAGPipeline` orchestrates all stages

#### 3. **Strategy Pattern**
- **Multiple Retrieval Strategies**: Lexical, Semantic, Hybrid
- **Runtime Selection**: User can choose search mode per query
- **Benefits**: Easy to add new strategies, A/B testing capability

#### 4. **Singleton Pattern**
- **Global Instances**: `get_pipeline()`, `get_embedder()`, etc.
- **Lazy Initialization**: Components loaded on first use
- **Trade-off**: Simpler than dependency injection, but less testable

---

## Design Reasoning

### 1. Why Hybrid Search?

**Problem**: Financial queries require both exact matching (fund names, metrics) and semantic understanding (concepts, descriptions).

**Solution**: Combine BM25 (lexical) and vector search (semantic) using Reciprocal Rank Fusion (RRF).

**Reasoning**:
- **Lexical (BM25)** excels at exact keyword matching (fund names, technical terms)
- **Semantic (Vector)** handles paraphrasing and conceptual queries
- **RRF Fusion** optimally combines both without training data
- **Parallel Execution** reduces latency by 40-50%

**Evidence**: Hybrid search consistently outperforms either method alone in evaluation.

---

### 2. Why ChromaDB over Qdrant/FAISS?

**Decision**: Use ChromaDB in-process (no server needed)

**Reasoning**:
- **Simplicity**: No external service to manage, faster local development
- **Sufficient Scale**: Handles MVP scale (thousands of documents) efficiently
- **Persistence**: Built-in persistence with minimal configuration
- **Trade-off**: Less scalable than distributed Qdrant, but simpler for MVP

**Migration Path**: Can swap to Qdrant server mode when scaling horizontally.

---

### 3. Why In-Process Embeddings (BGE-M3) over API?

**Decision**: Use local BGE-M3 model instead of OpenAI/Cohere embedding APIs

**Reasoning**:
- **Cost**: Free (no per-request charges)
- **Privacy**: Data never leaves the system
- **Latency**: No network round-trip for embeddings
- **Control**: Can fine-tune or swap models independently
- **Trade-off**: Larger model size (~2.3GB), slower initial load

**Performance**: Embedding cache (24hr TTL) makes subsequent embeddings instant.

---

### 4. Why Hash-Based Persistence?

**Problem**: Re-indexing takes 2-4 minutes. We don't want to rebuild on every startup.

**Solution**: Hash data files + config → store in `index.state` → skip re-indexing if unchanged.

**Reasoning**:
- **Fast Startup**: ~5-10 seconds if data unchanged vs 2-4 minutes
- **Data Integrity**: Automatically detects changes (CSV edits, model changes)
- **Developer Experience**: No manual cache invalidation needed
- **Robustness**: Falls back to re-indexing if persistence is corrupted

**Implementation**: MD5 hash of data files + embedding model config.

---

### 5. Why Multi-Level Caching?

**Decision**: Embedding cache (24hr) + Query cache (5min)

**Reasoning**:
- **Embedding Cache**: Prevents redundant model inference (expensive)
- **Query Cache**: Instant responses for repeated queries (100x faster)
- **TTL Selection**: 
  - Embeddings rarely change → long TTL (24hr)
  - Queries may need fresh data → short TTL (5min)

**Performance Impact**:
- First query: ~2-4s
- Cached query: ~50ms (100x improvement)

---

### 6. Why Parallel Hybrid Retrieval?

**Problem**: Sequential lexical + semantic search doubles latency.

**Solution**: Use `ThreadPoolExecutor` to run both searches simultaneously.

**Reasoning**:
- **Performance**: 40-50% faster than sequential
- **Efficiency**: Both searches are I/O bound (BM25 is CPU, but fast)
- **Simplicity**: ThreadPoolExecutor handles thread management

**Implementation**: 2-worker thread pool for lexical + semantic searches.

---

## Trade-off Decisions

### 1. **Simplicity vs. Scalability**

| Choice | Simple | Scalable | Decision |
|--------|--------|----------|----------|
| ChromaDB (in-process) | ✅ Easy setup | ❌ Single instance | **Chosen**: MVP focus |
| Qdrant (server) | ❌ More complex | ✅ Distributed | Future option |
| In-memory cache | ✅ No dependencies | ❌ Not distributed | **Chosen**: Development fallback |
| Redis cache | ⚠️ External service | ✅ Distributed | **Chosen**: Production (auto-fallback) |
| SQLite (async) | ✅ No dependencies | ❌ Single instance | **Chosen**: Development |
| PostgreSQL (async) | ⚠️ External service | ✅ Distributed | **Chosen**: Production |

**Justification**: Prioritize rapid development and MVP validation. Can scale horizontally later with minimal code changes.

---

### 2. **Cost vs. Performance**

| Choice | Cost | Performance | Decision |
|--------|------|-------------|----------|
| Local BGE-M3 | ✅ Free | ⚠️ ~50-100ms/embed | **Chosen**: Cost-effective |
| OpenAI embeddings | ❌ $0.10/1M tokens | ✅ ~200ms (with network) | Too expensive for MVP |
| Cohere reranking | ⚠️ Optional | ✅ Better ranking | **Optional**: Graceful fallback |

**Justification**: BGE-M3 provides excellent quality at zero cost. Reranking is optional and degrades gracefully if API key unavailable.

---

### 3. **Speed vs. Accuracy**

| Choice | Speed | Accuracy | Decision |
|--------|-------|----------|----------|
| Lexical only | ✅ Fast (~5-20ms) | ⚠️ Misses synonyms | Available option |
| Semantic only | ⚠️ Slower (~50-150ms) | ✅ Understands context | Available option |
| Hybrid (parallel) | ⚠️ ~50-150ms | ✅ Best accuracy | **Default**: Best balance |
| With reranking | ❌ ~200-500ms extra | ✅ Best accuracy | **Optional**: User choice |

**Justification**: Hybrid is the sweet spot. Reranking adds latency but improves accuracy for critical queries.

---

### 4. **Code Complexity vs. Features**

| Feature | Complexity | Value | Decision |
|---------|------------|-------|----------|
| Parallel retrieval | Low | High (40% faster) | **Implemented**: Worth it |
| Hash-based persistence | Medium | High (fast startup) | **Implemented**: Essential |
| Query classification | Low | Medium (UX) | **Implemented**: Low effort |
| Multi-modal search | High | Low (not needed) | **Rejected**: Out of scope |

**Justification**: Implemented features provide high value with manageable complexity. Avoided over-engineering.

---

### 5. **Development Speed vs. Production Readiness**

| Aspect | Development Choice | Production Needs | Migration Path |
|--------|-------------------|------------------|----------------|
| CORS | Allow all origins | Restrict domains | Environment config |
| Error messages | Detailed | Sanitized | Middleware wrapper |
| Logging | Console | Structured (JSON) | Logging service |
| Secrets | .env file | Secret manager | Environment variables |
| In-memory cache | Dict | Redis | **Implemented**: Auto-detection with fallback |
| Database | SQLite (async) | PostgreSQL (async) | **Implemented**: Environment-based selection |
| LLM Model | Sonnet (default) | Opus (fallback) | **Implemented**: Cost-effective with quality fallback |

**Justification**: Ship MVP fast, iterate based on feedback. Clear migration paths identified.

---

## Scalability Thinking

### Current Scale (MVP)

- **Documents**: ~100-1000 documents (FAQs + Funds)
- **Queries**: ~10-100 queries/minute
- **Users**: Single instance, no load balancing
- **Data Size**: ~10-50MB of embeddings

**Current Architecture Handles**: ✅ MVP scale comfortably

---

### Scaling Dimensions

#### 1. **Vertical Scaling (Current)**

**Approach**: Larger instance, more CPU/RAM

**Limits**:
- Single instance bottleneck
- ChromaDB in-process limited by instance size
- In-memory cache limited by RAM

**When to Use**: Up to ~10,000 documents, ~1000 queries/minute

---

#### 2. **Horizontal Scaling (Future)**

**Approach**: Multiple API instances + shared services

**Required Changes**:

```python
# Current (single instance)
ChromaDB (in-process) → ChromaDB Server or Qdrant
Redis/In-memory cache → Redis cluster (already supports Redis)
SQLite/PostgreSQL → PostgreSQL cluster (already supports PostgreSQL)
Single API instance → Multiple instances behind load balancer
```

**Architecture**:
```
┌─────────────┐     ┌──────────────┐
│ Load        │────▶│ API Instance │
│ Balancer    │     │   (x3)       │
└─────────────┘     └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
    │ Redis   │      │ Vector    │    │ PostgreSQL│
    │ Cluster │      │ Store     │    │ (Metadata)│
    │ (Cache) │      │ (Qdrant)  │    │           │
    └─────────┘      └───────────┘    └───────────┘
```

**Benefits**:
- Handle 100x more traffic
- Fault tolerance (instance failures)
- Geographic distribution

---

#### 3. **Data Scaling**

**Current**: CSV files loaded at startup

**Future Options**:
- **Streaming Ingestion**: Process data incrementally
- **Database Backend**: PostgreSQL for structured data, vector store for embeddings
- **Partitioning**: Split by fund category, date ranges
- **Sharding**: Distribute vector collections across instances

---

#### 4. **Query Performance Scaling**

**Current Optimizations**:
- ✅ Parallel hybrid retrieval (40-50% faster)
- ✅ Multi-level caching (100x for cache hits)
- ✅ Hash-based persistence (fast startup)

**Future Optimizations**:
- **Batch Processing**: Group multiple queries
- **Query Precomputation**: Pre-embed common queries
- **CDN Caching**: Cache responses at edge
- **Read Replicas**: Separate read/write workloads

---

### Scalability Milestones

| Users/Docs | Architecture | Changes Needed |
|------------|--------------|----------------|
| **< 1K docs, < 100 qpm** | Current (MVP) | ✅ None |
| **< 10K docs, < 1K qpm** | Vertical scaling | Larger instance |
| **< 100K docs, < 10K qpm** | Horizontal scaling | Redis + Qdrant server |
| **> 100K docs, > 10K qpm** | Distributed | Sharding + read replicas |

**Current Status**: ✅ Optimized for MVP scale, clear path to production scale.

---

## Justification of Choices

### Technology Stack Justifications

#### **FastAPI (Backend Framework)**

**Why**: 
- **Performance**: Async/await support, one of the fastest Python frameworks
- **Developer Experience**: Automatic OpenAPI docs, type validation with Pydantic
- **Modern**: Built for Python 3.6+, uses modern Python features
- **Ecosystem**: Large community, extensive middleware support

**Alternatives Considered**:
- Flask: Simpler but slower, no async support
- Django: Overkill for API-only, heavier framework
- Node.js/Express: Team Python expertise

**Decision**: ✅ FastAPI - Best balance of performance and DX

---

#### **BGE-M3 (Embedding Model)**

**Why**:
- **State-of-the-Art**: Top performer on MTEB leaderboard
- **Multilingual**: Handles English + other languages
- **Hybrid Support**: Dense embeddings work with hybrid search
- **Free**: No API costs, runs locally

**Alternatives Considered**:
- OpenAI `text-embedding-ada-002`: Excellent but $0.10/1M tokens
- `all-MiniLM-L6-v2`: Faster but lower quality
- Cohere embeddings: Good but API dependency

**Decision**: ✅ BGE-M3 - Best quality-to-cost ratio

---

#### **ChromaDB (Vector Store)**

**Why**:
- **Zero Configuration**: Works out of the box
- **Persistence**: Built-in with minimal setup
- **Python Native**: Seamless integration
- **Sufficient Scale**: Handles MVP needs

**Alternatives Considered**:
- **Qdrant**: Better for production scale, but requires server setup
- **FAISS**: Fast but no persistence, manual index management
- **Pinecone**: Managed service, but adds cost and dependency

**Decision**: ✅ ChromaDB - Simplest viable option for MVP

---

#### **BM25 (Lexical Search)**

**Why**:
- **Industry Standard**: Proven algorithm for keyword search
- **Fast**: ~5-20ms per query
- **Effective**: Excellent for exact matches (fund names, metrics)
- **Simple**: No training, works immediately

**Alternatives Considered**:
- **TF-IDF**: Simpler but less effective than BM25
- **Elasticsearch**: Overkill for MVP, requires separate service
- **Database LIKE queries**: Too slow, no ranking

**Decision**: ✅ BM25 - Perfect balance of simplicity and effectiveness

---

#### **Reciprocal Rank Fusion (RRF)**

**Why**:
- **No Training**: Works without labeled data
- **Effective**: Proven to combine rankings well
- **Simple**: Easy to implement and tune
- **Fast**: Minimal computation overhead

**Alternatives Considered**:
- **Weighted Sum**: Requires training data to tune weights
- **Learned Fusion**: More accurate but complex, needs training
- **Re-ranking Only**: Misses benefits of combining multiple signals

**Decision**: ✅ RRF - Best trade-off of simplicity and effectiveness

---

#### **Anthropic Claude (LLM)**

**Why**:
- **Quality**: Top-tier reasoning and generation quality
- **Context Handling**: Excellent with long contexts
- **Safety**: Built-in safety features, responsible AI
- **Availability**: Reliable API, good documentation

**Alternatives Considered**:
- **GPT-4**: Similar quality, but OpenAI's API has rate limits
- **Open Source (Llama)**: Free but requires infrastructure, lower quality
- **Gemini**: Good but less mature API

**Decision**: ✅ Claude - Best balance of quality and reliability

---

### Architectural Pattern Justifications

#### **Layered Architecture**

**Why**:
- **Separation of Concerns**: Each layer has clear responsibilities
- **Testability**: Easy to mock layers for unit tests
- **Maintainability**: Changes isolated to relevant layer
- **Flexibility**: Easy to swap implementations

**Alternative**: Monolithic code in single file

**Decision**: ✅ Layered - Industry best practice, long-term maintainability

---

#### **Pipeline Pattern**

**Why**:
- **Clear Flow**: Query → Retrieve → Generate → Respond
- **Modularity**: Easy to add/remove stages (e.g., reranking)
- **Debugging**: Clear data flow for troubleshooting
- **Extensibility**: Easy to add new stages (e.g., query expansion)

**Alternative**: Single function doing everything

**Decision**: ✅ Pipeline - Better code organization and extensibility

---

#### **Singleton Pattern (Global Instances)**

**Why**:
- **Simplicity**: Easy to use, no dependency injection complexity
- **Lazy Loading**: Components initialized on first use
- **Resource Efficiency**: Single instance of expensive components (embedder, model)

**Alternative**: Dependency injection with FastAPI

**Trade-off**: Less testable but simpler for MVP

**Decision**: ✅ Singleton - Simpler for MVP, can refactor to DI later

---

### Design Decision Justifications

#### **Parallel Hybrid Retrieval**

**Why**:
- **Performance**: 40-50% latency reduction vs sequential
- **Low Complexity**: `ThreadPoolExecutor` handles threading
- **No Downsides**: Both searches are independent

**Alternative**: Sequential execution

**Decision**: ✅ Parallel - Significant performance gain with minimal complexity

---

#### **Hash-Based Persistence**

**Why**:
- **User Experience**: Fast startup (5-10s vs 2-4min)
- **Robustness**: Automatically detects changes
- **Developer Experience**: No manual cache management

**Alternative**: Always re-index on startup

**Decision**: ✅ Hash-based - Essential for good developer experience

---

#### **Optional Reranking**

**Why**:
- **Flexibility**: Works with or without Cohere API
- **User Choice**: Can enable/disable per query
- **Cost Control**: Users can skip if latency/cost is concern

**Alternative**: Always rerank or never rerank

**Decision**: ✅ Optional - Best flexibility, graceful degradation

---

#### **Multi-Level Caching**

**Why**:
- **Performance**: 100x speedup for cache hits
- **Resource Efficiency**: Avoids redundant computation
- **User Experience**: Instant responses for repeated queries

**Alternative**: No caching

**Decision**: ✅ Multi-level - Essential for good performance

---

## Performance Characteristics

### Latency Breakdown

| Stage | Time (First Query) | Time (Cached) |
|-------|-------------------|---------------|
| Query Embedding | 50-100ms | ~10ms (cache) |
| Lexical Search | 5-20ms | 5-20ms |
| Semantic Search | 50-150ms | 50-150ms |
| Hybrid (Parallel) | 50-150ms | 50-150ms |
| Reranking (Optional) | 200-500ms | 200-500ms |
| LLM Generation | 1000-3000ms | 1000-3000ms |
| **Total (First)** | **~2000-4000ms** | - |
| **Total (Cached Query)** | - | **~50ms** |

### Throughput

- **Sustained**: ~10-20 queries/second per instance
- **Burst**: ~50 queries/second (with caching)
- **Bottleneck**: LLM generation (~1000-3000ms per query)

### Resource Usage

- **Memory**: ~2-4GB (embedding model + indexes + cache)
- **CPU**: Moderate (embedding generation, BM25 search)
- **Storage**: ~100-500MB (embeddings + ChromaDB)

---

## Future Enhancements

### Short Term (Next Sprint)

1. ✅ **Redis Integration**: Already implemented with automatic fallback
2. ✅ **PostgreSQL Support**: Already implemented with async operations
3. ✅ **Query Normalization**: Already implemented for better cache hits
4. **Structured Logging**: JSON logs for production monitoring
3. **Rate Limiting**: Protect API from abuse
4. **Metrics/Telemetry**: Prometheus metrics, OpenTelemetry tracing

### Medium Term (Next Quarter)

1. **Horizontal Scaling**: Load balancer + multiple instances
2. **Qdrant Migration**: Move to Qdrant server for distributed vector store
3. **Query Analytics**: Track query patterns, A/B test search strategies
4. **Fine-tuning**: Fine-tune BGE-M3 on financial domain data

### Long Term (Next Year)

1. **Multi-modal**: Support images, charts, PDFs
2. **Real-time Updates**: Stream new data without full re-indexing
3. **Personalization**: User-specific query routing and ranking
4. **Federated Search**: Query multiple data sources simultaneously

---

## Conclusion

The Qonfido RAG architecture prioritizes:

1. **Developer Experience**: Fast iteration, clear code structure
2. **Performance**: Multi-level caching, parallel execution
3. **Flexibility**: Optional features, multiple search modes
4. **Cost Efficiency**: Free embeddings, optional paid features
5. **Scalability Path**: Clear migration path to production scale

Every design decision was made with:
- **Trade-offs understood**: We know what we're giving up
- **Migration paths identified**: We know how to scale later
- **User needs prioritized**: MVP features first, nice-to-haves later

The architecture is **production-ready for MVP scale** and has a **clear path to enterprise scale** when needed.

---

## References

- [Backend Documentation](./BACKEND_DOCUMENTATION.md)
- [Deep Architecture](./DEEP_ARCHITECTURE.md)
- [Data Flow](./DATA_FLOW.md) - Visual flow diagrams
- [Project Structure](./PROJECT_STRUCTURE.md)

