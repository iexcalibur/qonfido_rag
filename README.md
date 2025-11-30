# Qonfido RAG - AI Financial Co-Pilot

A high-performance Retrieval-Augmented Generation (RAG) system built for financial intelligence. It combines semantic understanding with precise financial metrics to answer complex queries about mutual funds.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![Claude](https://img.shields.io/badge/Claude-Opus%2FSonnet-purple)

<img width="1325" height="806" alt="Screenshot 2025-11-30 at 10 27 15 AM" src="https://github.com/user-attachments/assets/15e32be4-edb2-4931-bc3a-e771ccba9e62" />
<img width="1325" height="807" alt="Screenshot 2025-11-30 at 10 27 27 AM" src="https://github.com/user-attachments/assets/2ee82400-c731-4d96-adc0-1bf44dda9c94" />
<img width="1326" height="810" alt="Screenshot 2025-11-30 at 10 27 42 AM" src="https://github.com/user-attachments/assets/646e5f65-5bfc-43dd-b93a-e8b24aa2f7a3" />
<img width="1324" height="807" alt="Screenshot 2025-11-30 at 10 28 00 AM" src="https://github.com/user-attachments/assets/a7e71a28-889a-457e-94dd-7c3b62726ffb" />
<img width="1325" height="806" alt="Screenshot 2025-11-30 at 10 28 17 AM" src="https://github.com/user-attachments/assets/0e730385-fa22-4708-8883-13fb9ec0f20e" />


## 🎯 Capabilities

This system goes beyond simple text matching by handling **structured financial data** alongside unstructured text.

- **📈 Quantitative Analysis**: "Which funds have a Sharpe ratio > 1.5 and low volatility?"

- **🧠 Conceptual Queries**: "What is the difference between a Flexi Cap and a Multi Cap fund?"

- **⚡ Hybrid Queries**: "Show me the best performing Large Cap funds and explain why they are safe."

## 🏗️ Architecture

### System Overview

The system follows a **layered architecture** pattern with clear separation of concerns:

```
Client Layer (Next.js) → API Gateway (FastAPI) → Application Layer (RAG Pipeline) 
  → Retrieval Layer (Hybrid Search) → Generation Layer (Claude) → Data Layer
```

### Architecture Flow

```mermaid
flowchart TB
    User[User] --> Frontend[Next.js Frontend]
    Frontend --> API[FastAPI Backend]
    
    subgraph "Initialization (Startup)"
        direction TB
        Init[Pipeline Initialize] --> HashCheck{Hash Check}
        HashCheck -->|Match| LoadPersist[Load from Persistent Store<br/>~5-10 seconds]
        HashCheck -->|Mismatch| ReIndex[Re-index & Save State<br/>~2-4 minutes]
        LoadPersist --> Ready[System Ready]
        ReIndex --> Ready
    end
    
    subgraph "RAG Pipeline (Query Processing)"
        direction TB
        API --> Cache{Query Cache}
        Cache -->|Hit| Return[Return Response<br/>~50ms]
        Cache -->|Miss| Pipeline[Process Query]
        
        Pipeline --> Embed[Embedder<br/>BGE-M3]
        
        subgraph "Parallel Retrieval"
            direction LR
            Embed --> Lexical[Lexical Search<br/>BM25 In-Memory]
            Embed --> Semantic[Semantic Search<br/>ChromaDB Persistent]
        end
        
        Lexical & Semantic --> RRF[RRF Fusion]
        RRF --> Rerank[Cohere Reranker]
        Rerank --> LLM[Claude Generation]
        LLM --> API
    end
    
    subgraph "Storage Layer"
        direction TB
        PersistDB[(ChromaDB<br/>Persistent Vector Store)]
        StateFile[State File<br/>data/index.state]
        EmbedCache[Embedding Cache<br/>24h TTL]
        QueryCache[Query Cache<br/>5m TTL]
    end
    
    Semantic -.->|Reads/Writes| PersistDB
    HashCheck -.->|Checks| StateFile
    Embed -.->|Uses| EmbedCache
    Cache -.->|Uses| QueryCache
    
    style LoadPersist fill:#c8e6c9
    style ReIndex fill:#fff9c4
    style PersistDB fill:#e1f5ff
    style StateFile fill:#f3e5f5
```

### Key Architectural Patterns

1. **Layered Architecture**: Separation of concerns (API → Application → Domain → Infrastructure)
2. **Pipeline Pattern**: Sequential processing (Query → Retrieve → Generate → Respond)
3. **Strategy Pattern**: Multiple retrieval strategies (Lexical, Semantic, Hybrid) selectable at runtime
4. **Singleton Pattern**: Global instances for expensive components (embedder, models)

### Design Decisions

#### Why Hybrid Search?
- **Lexical (BM25)**: Excellent for exact keyword matching (fund names, metrics)
- **Semantic (Vector)**: Handles paraphrasing and conceptual queries
- **RRF Fusion**: Combines both optimally without training data
- **Parallel Execution**: 40-50% latency reduction vs sequential

#### Why ChromaDB?
- **Simplicity**: No server needed (in-process), faster development
- **Sufficient Scale**: Handles MVP scale (thousands of documents) efficiently
- **Persistence**: Built-in with minimal configuration
- **Trade-off**: Less scalable than distributed Qdrant, but simpler for MVP

#### Why BGE-M3 (Local) over API?
- **Cost**: Free (no per-request charges)
- **Privacy**: Data never leaves the system
- **Latency**: No network round-trip
- **Trade-off**: Larger model size (~2.3GB), slower initial load

#### Why Hash-Based Persistence?
- **Fast Startup**: ~5-10 seconds if data unchanged vs 2-4 minutes to re-index
- **Automatic Detection**: Detects data/config changes via MD5 hash
- **Developer Experience**: No manual cache invalidation needed

#### Why Multi-Level Caching?
- **Embedding Cache (24hr)**: Prevents redundant model inference
- **Query Cache (5min)**: Instant responses for repeated queries (100x faster)
- **Performance Impact**: First query ~2-4s, cached query ~50ms

### Scalability

**Current Scale (MVP)**:
- Documents: ~100-1000 documents (FAQs + Funds)
- Queries: ~10-100 queries/minute
- Architecture: Single instance, vertical scaling

**Scaling Path**:
1. **Vertical Scaling**: Larger instance (up to ~10K docs, ~1K qpm)
2. **Horizontal Scaling**: Multiple instances + shared services (Redis, Qdrant server)
3. **Distributed**: Sharding + read replicas for enterprise scale

The architecture is **production-ready for MVP scale** with a **clear path to enterprise scale**.

📖 **For detailed architecture documentation, see [Architecture & Design Decisions](docs/ARCHITECTURE_AND_DESIGN_DECISIONS.md)**

## 🛠️ Tech Stack

### Technology Choices & Justifications

| Layer | Component | Technology | Rationale |
|-------|-----------|------------|-----------|
| **Frontend** | Framework | **Next.js 16** (App Router) | Modern React framework, excellent DX, SSR support |
| | Styling | **Tailwind CSS** + Radix UI | Utility-first CSS, accessible components |
| | State | React Query + Custom Hooks | Efficient data fetching, caching |
| **Backend** | API | **FastAPI** + Pydantic | High performance, async support, auto-docs |
| | Embeddings | **BGE-M3** (1024-dim) | Top quality, free, multilingual support |
| | Vector Store | **ChromaDB** (In-Process) | Simple setup, built-in persistence, Python-native |
| | LLM | **Anthropic Claude 3** | Top-tier quality, excellent context handling |
| | Lexical Search | **BM25** | Fast, proven algorithm, no training needed |
| | Reranking | **Cohere** (Optional) | Better ranking, graceful fallback if unavailable |
| **Data** | Storage | CSV + ChromaDB | Simple, sufficient for MVP |
| | Cache | In-Memory (TTL-based) | Fast, simple, upgradeable to Redis later |
| | Persistence | Hash-based state | Fast startup, automatic change detection |

**Design Philosophy**: Prioritize simplicity and developer experience for MVP, with clear migration paths for production scale.

## 🚀 Quick Start (Recommended)

The easiest way to run the project is using the included **Makefile**.

### Prerequisites

- Python 3.12+
- Node.js 20+
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

### 1. Setup Environment

```bash
# Install backend & frontend dependencies
make setup

# Create .env file and add your API keys
cp .env.example .env
# (Edit .env to add ANTHROPIC_API_KEY)
```

### 2. Ingest Data

Loads FAQs and Fund CSVs, generates embeddings, and builds the search indexes.

```bash
make ingest
```

### 3. Run Development Servers

Starts both FastAPI (Port 8000) and Next.js (Port 3000) concurrently.

```bash
make dev
```

### 4. Access the App

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## 💡 Key Innovations

### 1. 🔢 Numerical-to-Text Ingestion

**Problem**: Standard embedding models struggle with raw numbers, making it hard to search over structured financial metrics.

**Solution**: Convert structured fund metrics into rich semantic text descriptions during ingestion, enabling semantic search over numerical data.

- *Raw:* `{"sharpe": 1.25, "cagr": 15.2}`
- *Indexed:* `"Fund X has a 3-year CAGR of 15.2% and a Sharpe Ratio of 1.25..."`

**Impact**: Allows queries like *"funds with excellent risk-adjusted returns"* to find funds with high Sharpe ratios through semantic understanding.

---

### 2. ⚡ Parallel Hybrid Search with RRF Fusion

**Architecture**: Combines BM25 (lexical) and ChromaDB (semantic) search using Reciprocal Rank Fusion (RRF).

**Innovation**: 
- **Parallel Execution**: ThreadPoolExecutor runs both searches simultaneously
- **40-50% Latency Reduction**: vs sequential execution
- **Optimal Ranking**: RRF combines strengths of both methods without training data

**Why RRF?**: No training required, proven effectiveness, simple implementation.

---

### 3. 🚀 Multi-Level Caching System

**Design**: Two-tier caching strategy optimized for different use cases.

- **Embedding Cache (24h TTL):**
  - Hashes text inputs to prevent redundant model inference
  - Significant cost/performance savings (BGE-M3 inference is expensive)
  
- **Query Cache (5m TTL):**
  - Instant responses for repeated questions
  - Includes search mode and parameters in cache key

**Performance Impact**: 
- First query: ~2-4s
- Cached query: ~50ms (**100x faster**)
- Embedding cache hit: ~10ms

---

### 4. 🎯 Hash-Based Smart Persistence

**Innovation**: MD5 hash of data files + config to detect changes automatically.

**Benefits**:
- **Fast Startup**: ~5-10 seconds if data unchanged vs 2-4 minutes to re-index
- **Automatic Detection**: No manual cache invalidation needed
- **Robustness**: Falls back to re-indexing if persistence corrupted

**Implementation**: Stores hash in `data/index.state`, skips expensive embedding/indexing step if unchanged.

---

### 5. 🔄 Graceful Degradation

**Design Philosophy**: System works with optional components, degrades gracefully.

- **Cohere Reranking**: Optional, improves ranking but not required
- **API Keys**: Features work without optional keys (embedding cache, query cache still functional)
- **Error Handling**: Comprehensive error handling with safe fallbacks

**Benefit**: Better developer experience, easier setup, production resilience.

---

## 📡 API Usage

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

**Response:**
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

---

## 🔧 Key Features

### 1. Hybrid Search
- **Lexical (BM25)**: Exact keyword matching
- **Semantic (Vector)**: Conceptual similarity
- **RRF Fusion**: Combines both for optimal results
- **Parallel Retrieval**: 40-50% faster than sequential

### 2. Active Multi-Level Caching
- **Embedding Cache**: 24hr TTL, avoids recomputing embeddings (Active & Integrated)
- **Query Cache**: 5min TTL, instant responses for repeated queries (Active & Integrated)

### 3. Intelligent Query Handling
- Automatic query classification (FAQ vs numerical vs hybrid)
- Structured responses with fund metrics
- Source attribution for transparency

### 4. Production-Ready API
- Request validation with Pydantic
- Comprehensive error handling
- OpenAPI documentation
- Health checks

## 📊 Performance

| Metric | Value |
|--------|-------|
| First Query | ~2-4s (includes model loading) |
| Cached Query | ~50ms |
| Embedding Cache Hit | ~10ms |
| Parallel vs Sequential | ~40% faster |

## 📂 Project Structure

```
qonfido-rag/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── ingestion/      # Loader & Embedder logic
│   │   │   ├── retrieval/      # Lexical, Semantic & Hybrid search
│   │   │   ├── generation/     # LLM & Prompts
│   │   │   └── orchestration/  # Main RAG Pipeline
│   │   └── api/                # Routes & Schemas
│   └── data/raw/               # Source CSV files
├── frontend/
│   ├── src/
│   │   ├── app/chat/           # Chat interface logic
│   │   ├── components/         # Reusable UI components
│   │   └── hooks/              # Data fetching hooks
├── docs/                       # Detailed Architecture Docs
└── Makefile                    # Automation commands
```

### Detailed Documentation

- **[Architecture & Design Decisions](docs/ARCHITECTURE_AND_DESIGN_DECISIONS.md)** - Comprehensive architecture, design reasoning, trade-offs, and scalability
- [Backend Architecture](docs/BACKEND_DOCUMENTATION.md) - Backend implementation details
- [Frontend Architecture](docs/FRONTEND_DOCUMENTATION.md) - Frontend implementation details
- [Deep Architecture](docs/DEEP_ARCHITECTURE.md) - Technical deep-dive
- [Data Flow](docs/DATA_FLOW.md) - Visual flow diagrams (Mermaid)
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Complete project organization


## 🧪 Testing & Evaluation

We include a comprehensive evaluation suite to measure RAG quality.

```bash
# Run full evaluation suite
make evaluate

# Compare search modes (Hybrid vs Lexical vs Semantic)
python -m scripts.evaluate --mode all

# Test a single query manually
python -m scripts.test_query "What is the best fund for high risk?"
```

## ⚙️ Configuration (.env)

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (Features degrade gracefully if missing)
COHERE_API_KEY=...          # Enables Reranking step
EMBEDDING_MODEL=BAAI/bge-m3 # Can swap to 'all-MiniLM-L6-v2' for speed
CLAUDE_MODEL=claude-3-opus-20240229
```

---

## 📋 Manual Setup (Alternative)

If you prefer not to use the Makefile, you can set up manually:

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

# Ingest data
python scripts/ingest_data.py

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

## 🐛 Troubleshooting

**Model Download Takes Too Long**
- BGE-M3 model (~2.3GB) downloads on first run (one-time)
- Ensure stable internet connection

**No Documents Loaded**
- Verify CSV files exist in `backend/data/raw/`
- Check file names match settings (`faqs.csv`, `funds.csv`)

**Empty Search Results**
- Run data ingestion: `python -m scripts.ingest_data`
- Check indexes are built (look for "Indexed X documents" in logs)

**Slow Query Responses**
- First query includes model loading (one-time)
- Enable caching (already enabled by default)
- Use smaller embedding model: `EMBEDDING_MODEL=all-MiniLM-L6-v2`

See [Troubleshooting Guide](README.md#-troubleshooting) for more solutions.

## 📝 License

This project was created for the Qonfido AI Co-Pilot assignment.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) - Claude API
- [Cohere](https://cohere.com) - Reranking API
- [ChromaDB](https://trychroma.com) - Vector Store
- [Sentence Transformers](https://sbert.net) - Embeddings
