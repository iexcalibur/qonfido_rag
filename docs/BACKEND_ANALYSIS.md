# Backend Implementation Analysis

## Comparison: README Documentation vs. Actual Implementation

This document analyzes the backend folder to compare what's documented in the README (lines 321-337) with what's actually implemented.

---

## 📋 Summary Table

| Component | README Claims | Actual Implementation | Status |
|-----------|---------------|----------------------|--------|
| **Query Router** | LangGraph Query Router | Simple RAGPipeline class | ❌ Different |
| **Query Classification** | [Classify Query] → [Route] → [Retrieve] → [Generate] | Manual classification + direct pipeline | ⚠️ Partial |
| **BGE-M3** | BGE-M3 embeddings | ✅ BAAI/bge-m3 (1024 dim) | ✅ Implemented |
| **Qdrant** | Qdrant vector store | ChromaDB (in-process) | ❌ Different |
| **BM25** | BM25 lexical search | ✅ rank-bm25 library | ✅ Implemented |
| **Cohere** | Cohere reranking | ✅ Cohere rerank-english-v3.0 | ✅ Implemented |
| **Claude API** | Claude API generation | ✅ Anthropic Claude (claude-3-opus-20240229) | ✅ Implemented |
| **Instructor** | Instructor library | ❌ Not implemented | ❌ Missing |
| **LangFuse** | LangFuse tracing | ✅ Service exists but may not be actively used | ⚠️ Partial |
| **PostgreSQL** | PostgreSQL (Metadata) | SQLite (default) with PostgreSQL support | ⚠️ Partial |
| **Redis** | Redis (Cache) | In-memory cache with Redis placeholder | ⚠️ Partial |

---

## 🔍 Detailed Analysis

### 1. Query Router & Classification

**README Claims:**
- LangGraph Query Router with flow: `[Classify Query] → [Route] → [Retrieve] → [Generate]`

**Actual Implementation:**
- ❌ **No LangGraph** - Uses a simple `RAGPipeline` class
- ✅ **Query Classification** - Implemented via `_classify_query()` method (keyword-based)
- ✅ **Routing** - Search mode selection (lexical/semantic/hybrid) based on user choice
- ✅ **Retrieval** - Implemented via searchers
- ✅ **Generation** - Implemented via LLMGenerator

**Location:** `backend/app/core/orchestration/pipeline.py`

**Implementation Details:**
```python
# Classification happens AFTER retrieval (not before routing)
def _classify_query(self, query: str, results: list) -> str:
    # Keyword-based classification (not ML-based)
    # Returns: "numerical", "faq", or "hybrid"
```

**Gap:** README mentions LangGraph, but no LangGraph code exists. Classification is simple keyword-based, not a sophisticated routing system.

---

### 2. Retrieval Components

#### 2.1 Embeddings - BGE-M3 ✅

**README Claims:** BGE-M3  
**Actual Implementation:** ✅ `BAAI/bge-m3` (1024 dimensions)

**Location:** `backend/app/core/ingestion/embedder.py`

**Status:** ✅ **Fully Implemented**
- Uses `sentence-transformers` library
- Default model: `BAAI/bge-m3`
- Fallback: `all-MiniLM-L6-v2` (384 dim)

---

#### 2.2 Vector Store - Qdrant ❌

**README Claims:** Qdrant  
**Actual Implementation:** ❌ **ChromaDB** (in-process, no server)

**Location:** `backend/app/core/retrieval/semantic.py`

**Status:** ❌ **Different Implementation**
- Uses ChromaDB instead of Qdrant
- Runs in-process (no separate server)
- Persists to local directory (`./chroma_db`)
- Supports both in-memory and persistent modes

**Why the difference:**
- ChromaDB is simpler (no server setup)
- Good for development and small-medium datasets
- Code comments indicate it's intentional

---

#### 2.3 Lexical Search - BM25 ✅

**README Claims:** BM25  
**Actual Implementation:** ✅ `rank-bm25` library

**Location:** `backend/app/core/retrieval/lexical.py`

**Status:** ✅ **Fully Implemented**
- Uses `rank_bm25.BM25Okapi`
- Tokenizes documents and queries
- Supports source filtering

---

#### 2.4 Hybrid Search - RRF ✅

**README Claims:** Hybrid search with RRF  
**Actual Implementation:** ✅ RRF (Reciprocal Rank Fusion)

**Location:** `backend/app/core/retrieval/hybrid.py`

**Status:** ✅ **Fully Implemented**
- Combines lexical + semantic results
- Uses RRF formula: `RRF_score = sum(1 / (k + rank_i))`
- Default `rrf_k = 60`

---

#### 2.5 Reranking - Cohere ✅

**README Claims:** Cohere  
**Actual Implementation:** ✅ Cohere Rerank API

**Location:** `backend/app/core/retrieval/reranker.py`

**Status:** ✅ **Fully Implemented**
- Uses Cohere `rerank-english-v3.0` model
- Two-stage retrieval: fast retrieval → accurate reranking
- Optional (requires API key)

---

### 3. Generation Components

#### 3.1 Claude API ✅

**README Claims:** Claude API  
**Actual Implementation:** ✅ Anthropic Claude

**Location:** `backend/app/core/generation/llm.py`

**Status:** ✅ **Fully Implemented**
- Model: `claude-3-opus-20240229`
- Uses Anthropic SDK
- Custom system prompts
- Context formatting

---

#### 3.2 Instructor ❌

**README Claims:** Instructor  
**Actual Implementation:** ❌ **Not found**

**Location:** Not present in codebase

**Status:** ❌ **Missing**
- No imports of `instructor` library
- No structured output parsing
- Simple string generation only

**Gap:** README mentions Instructor, but it's not implemented or used anywhere.

---

### 4. Observability

#### 4.1 LangFuse ⚠️

**README Claims:** LangFuse tracing  
**Actual Implementation:** ⚠️ Service exists but may not be actively used

**Location:** `backend/app/services/tracing.py`

**Status:** ⚠️ **Partially Implemented**
- Service class exists with full API
- Requires `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`
- Not called in pipeline execution
- Optional/conditional usage

**Gap:** Tracing service exists but is not integrated into the main pipeline flow.

---

### 5. Data Storage

#### 5.1 PostgreSQL ⚠️

**README Claims:** PostgreSQL (Metadata)  
**Actual Implementation:** ⚠️ SQLite by default, PostgreSQL supported

**Location:** `backend/app/db/session.py`

**Status:** ⚠️ **Partially Implemented**
- Default: SQLite (`sqlite:///./qonfido_rag.db`)
- Code supports PostgreSQL connection strings
- Uses SQLModel (works with both)
- Models defined but may not be actively used for query storage

**Gap:** README shows PostgreSQL, but implementation defaults to SQLite. PostgreSQL is supported but not the default.

---

#### 5.2 Redis ⚠️

**README Claims:** Redis (Cache)  
**Actual Implementation:** ⚠️ In-memory cache (Redis placeholder)

**Location:** `backend/app/services/cache.py`

**Status:** ⚠️ **Partially Implemented**
- Uses `InMemoryCache` class
- Comment says: "For production, replace with Redis"
- No actual Redis integration
- TTL-based expiration

**Gap:** README mentions Redis, but implementation uses in-memory cache. Redis is mentioned as a future improvement.

---

## 📊 Implementation Status Summary

### ✅ Fully Implemented (6/11)
1. ✅ BGE-M3 embeddings
2. ✅ BM25 lexical search
3. ✅ Cohere reranking
4. ✅ Claude API generation
5. ✅ Hybrid search with RRF
6. ✅ Query classification (simple keyword-based)

### ⚠️ Partially Implemented (3/11)
1. ⚠️ Query Router (exists but not LangGraph, simpler pipeline)
2. ⚠️ LangFuse (service exists but not actively used)
3. ⚠️ PostgreSQL (supported but defaults to SQLite)

### ❌ Different Implementation (2/11)
1. ❌ Qdrant → ChromaDB (intentional, simpler approach)
2. ❌ Redis → In-memory cache (placeholder for future)

### ❌ Missing (2/11)
1. ❌ LangGraph Query Router
2. ❌ Instructor library

---

## 🔧 Recommendations

### 1. Update README to Match Implementation
- Change "LangGraph Query Router" → "RAGPipeline with Query Classification"
- Change "Qdrant" → "ChromaDB (in-process vector store)"
- Change "PostgreSQL" → "SQLite (default) / PostgreSQL (optional)"
- Change "Redis" → "In-memory cache (Redis planned for production)"
- Remove or mark "Instructor" as optional/planned

### 2. Or Implement Missing Features
- Add LangGraph for sophisticated query routing
- Integrate Instructor for structured outputs
- Add Redis caching for production
- Actively integrate LangFuse tracing

### 3. Current Architecture is Valid
The actual implementation is simpler and more practical than the README suggests:
- ✅ ChromaDB is easier to set up than Qdrant
- ✅ SQLite is fine for development
- ✅ In-memory cache works for MVP
- ✅ Simple classification is sufficient for many use cases

---

## 📁 File Structure Reference

```
backend/app/
├── core/
│   ├── generation/
│   │   └── llm.py              # Claude API ✅
│   ├── ingestion/
│   │   └── embedder.py         # BGE-M3 ✅
│   ├── orchestration/
│   │   └── pipeline.py         # RAGPipeline (no LangGraph) ⚠️
│   └── retrieval/
│       ├── hybrid.py           # RRF ✅
│       ├── lexical.py          # BM25 ✅
│       ├── reranker.py         # Cohere ✅
│       └── semantic.py         # ChromaDB (not Qdrant) ❌
├── services/
│   ├── cache.py                # In-memory (not Redis) ⚠️
│   ├── tracing.py              # LangFuse service (unused) ⚠️
│   └── vector_store.py         # ChromaDB wrapper
└── db/
    └── session.py              # SQLite (not PostgreSQL) ⚠️
```

---

## ✅ Conclusion

**The backend is functional and well-implemented**, but the README documentation doesn't accurately reflect the actual implementation. The current architecture is:

- **Simpler** than documented (no LangGraph, ChromaDB instead of Qdrant)
- **Practical** for development and MVP (SQLite, in-memory cache)
- **Missing** some documented features (Instructor, LangGraph)
- **Extensible** (PostgreSQL/Redis support planned)

**Recommendation:** Update the README to match the actual implementation, or implement the missing features if they're essential for the product vision.

