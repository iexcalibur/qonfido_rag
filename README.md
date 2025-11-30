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

## 🛠️ Tech Stack

| Layer | Component | Technology |
|-------|-----------|------------|
| **Frontend** | Framework | **Next.js 16** (App Router) |
| | Styling | **Tailwind CSS** + Radix UI |
| | State | React Query + Custom Hooks |
| **Backend** | API | **FastAPI** + Pydantic |
| | Embeddings | **BGE-M3** (1024-dim) |
| | Vector Store | **ChromaDB** (In-Process) |
| | LLM | **Anthropic Claude 3** |
| **Data** | Storage | SQLite + CSV |
| | Cache | In-Memory (TTL-based) |

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

Standard embedding models struggle with raw numbers. We solve this by converting structured fund metrics into rich semantic text descriptions during ingestion.

- *Raw:* `{"sharpe": 1.25, "cagr": 15.2}`
- *Indexed:* `"Fund X has a 3-year CAGR of 15.2% and a Sharpe Ratio of 1.25..."`

This enables semantic search over numerical data, allowing queries like *"funds with excellent risk-adjusted returns"* to find funds with high Sharpe ratios.

### 2. ⚡ Parallel Hybrid Search

We employ a **ThreadPoolExecutor** strategy to run BM25 (Lexical) and ChromaDB (Semantic) searches simultaneously, reducing retrieval latency by **40-50%** compared to sequential execution.

### 3. 🚀 Active Caching Layer

The system features a multi-layer, fully integrated caching system enabled by default:

- **Embedding Cache (24h TTL):** Hashes text inputs to prevent redundant model inference.
- **Query Cache (5m TTL):** Instant responses for repeated questions.

This means second queries are **100x faster** (~50ms vs ~2-4s).

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

Detailed documentation:
- [Backend Architecture](docs/BACKEND_DOCUMENTATION.md)
- [Frontend Architecture](docs/FRONTEND_DOCUMENTATION.md)
- [Data Flow Diagrams](docs/DATA_FLOW_DIAGRAMS.md)


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
