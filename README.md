# Qonfido RAG - AI Financial Co-Pilot

A Retrieval-Augmented Generation (RAG) system for financial data, built for the Qonfido AI Co-Pilot assignment.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![Claude](https://img.shields.io/badge/Claude-API-purple)

## 🎯 Overview

This system enables natural language queries about mutual funds, combining:
- **Textual Knowledge**: FAQs and financial concepts
- **Quantitative Data**: Fund performance metrics (CAGR, Sharpe ratio, volatility, etc.)

Users can ask questions like:
- *"Which funds have the best Sharpe ratio?"*
- *"What is an index fund?"*
- *"Show me low-risk funds with good returns"*

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

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Python 3.12+ | REST API server |
| **Embeddings** | BGE-M3 (sentence-transformers) | 1024-dim dense vectors |
| **Vector Store** | ChromaDB | Semantic similarity search |
| **Lexical Search** | BM25 (rank-bm25) | Keyword matching |
| **Hybrid Search** | RRF Fusion | Combines lexical + semantic |
| **Reranking** | Cohere API | Two-stage retrieval (optional) |
| **LLM** | Claude API (Anthropic) | Answer generation |
| **Frontend** | Next.js 16 + Tailwind CSS | Modern web interface |
| **Cache** | In-Memory (TTL-based) | Embedding + query caching |

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Anthropic API Key ([Get one here](https://console.anthropic.com/))
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

### Access

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

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

## 🔧 Key Features

### 1. Hybrid Search
- **Lexical (BM25)**: Exact keyword matching
- **Semantic (Vector)**: Conceptual similarity
- **RRF Fusion**: Combines both for optimal results
- **Parallel Retrieval**: 40-50% faster than sequential

### 2. Multi-Level Caching
- **Embedding Cache**: 24hr TTL, avoids recomputing embeddings
- **Query Cache**: 5min TTL, instant responses for repeated queries

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

## 📁 Project Structure

```
qonfido-rag/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── data/        # CSV data files
│   └── scripts/     # Utility scripts
├── frontend/        # Next.js frontend
│   └── src/         # Source code
└── docs/            # Documentation
```

For detailed structure, see:
- [Backend Structure](docs/backend-structure.md)
- [Frontend Structure](docs/frontend-structure.md)

## 📚 Documentation

- **[Data Flow](docs/data-flow.md)** - End-to-end RAG pipeline diagram
- **[Deep Architecture](docs/deep-architecture.md)** - Technical architecture details
- **[Backend Structure](docs/backend-structure.md)** - Backend organization
- **[Frontend Structure](docs/frontend-structure.md)** - Frontend organization

## ⚙️ Configuration

Key environment variables:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
COHERE_API_KEY=...              # For reranking
EMBEDDING_MODEL=BAAI/bge-m3     # Embedding model
CLAUDE_MODEL=claude-3-opus-20240229
DATA_DIR=data/raw
FAQS_FILE=faqs.csv
FUNDS_FILE=funds.csv
```

See `.env.example` for full configuration options.

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
