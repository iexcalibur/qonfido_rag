# 🚀 Qonfido RAG - Financial Intelligence System

A production-ready Retrieval-Augmented Generation (RAG) system for answering financial questions using both textual knowledge (FAQs) and quantitative data (fund performance metrics).

![Architecture](docs/images/architecture.png)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Minimum Requirements](#minimum-requirements)
- [Quick Start](#quick-start)
- [Manual Setup](#manual-setup)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Evaluation](#evaluation)
- [Trade-offs & Decisions](#trade-offs--decisions)
- [Future Improvements](#future-improvements)

---

## 🎯 Overview

Qonfido RAG is a **full-stack financial intelligence platform** that combines:

- **Hybrid Search**: Lexical (BM25) + Semantic (Dense Vectors) + Reranking
- **Intelligent Query Routing**: LangGraph-powered orchestration
- **Structured Responses**: JSON outputs with source citations
- **Modern Dashboard**: Next.js 14 with real-time visualizations

---

## ✨ Features

### Core RAG Capabilities
- ✅ Hybrid search (BM25 + Semantic + RRF fusion)
- ✅ Query classification (FAQ vs Numerical vs Hybrid)
- ✅ Cohere Rerank for improved accuracy
- ✅ Structured JSON responses with Instructor
- ✅ Source attribution and citations

### Dashboard Features
- ✅ Interactive chat interface
- ✅ Fund comparison and analytics
- ✅ Performance visualizations (CAGR, Sharpe, Volatility)
- ✅ Search mode toggle (Lexical/Semantic/Hybrid)
- ✅ Query trace viewer
- ✅ Dark/Light mode

### Production Features
- ✅ Redis caching (embeddings + queries)
- ✅ LangFuse observability
- ✅ Ragas evaluation metrics
- ✅ Docker Compose deployment
- ✅ Comprehensive test suite

---

## 🛠 Tech Stack

### Backend (Python)
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.115.6 | REST API |
| Pydantic | 2.10.4 | Validation |
| LangGraph | 0.2.60 | Query Orchestration |
| BGE-M3 | via FlagEmbedding 1.2.12 | Embeddings |
| Qdrant | 1.12.1 | Vector Store |
| Cohere | 5.13.4 | Reranking |
| Anthropic | 0.40.0 | Claude LLM |
| Instructor | 1.7.2 | Structured Outputs |
| PostgreSQL | 16+ | Metadata Storage |
| Redis | 7.2+ | Caching |
| LangFuse | 2.57.1 | Observability |

### Frontend (Node.js)
| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 20.0.0+ | Runtime |
| Next.js | 14.2.21 | React Framework |
| TypeScript | 5.7.2 | Type Safety |
| Tailwind CSS | 3.4.17 | Styling |
| shadcn/ui | Latest | UI Components |
| TanStack Query | 5.62.8 | Data Fetching |
| Recharts | 2.15.0 | Charts |
| Tremor | 3.18.4 | Dashboard Components |

### Infrastructure
| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 24.0+ | Containerization |
| Docker Compose | 2.20+ | Orchestration |
| Qdrant | 1.12.x | Vector Database |
| Redis | 7.2.x | Cache |
| PostgreSQL | 16.x | Database |

---

## 📦 Minimum Requirements

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disk | 20 GB | 50+ GB SSD |
| GPU | Not required | NVIDIA GPU (optional, for faster embeddings) |

### Software Requirements

```bash
# Verify your versions
python --version    # >= 3.11.0
node --version      # >= 20.0.0
npm --version       # >= 10.0.0
docker --version    # >= 24.0.0
docker compose version  # >= 2.20.0
```

### API Keys Required

| Service | Required | Purpose | Get Key |
|---------|----------|---------|---------|
| Anthropic | ✅ Yes | Claude LLM | https://console.anthropic.com |
| Cohere | ✅ Yes | Reranking | https://dashboard.cohere.com |
| LangFuse | ⚡ Optional | Observability | https://cloud.langfuse.com |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/qonfido-rag.git
cd qonfido-rag

# 2. Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Add your API keys to backend/.env
# ANTHROPIC_API_KEY=sk-ant-...
# COHERE_API_KEY=...

# 4. Start all services
docker compose up -d

# 5. Ingest data (first time only)
docker compose exec backend python scripts/ingest_data.py

# 6. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Qdrant Dashboard: http://localhost:6333/dashboard
```

### Option 2: Quick Start Script

```bash
# One-command setup
make setup

# Start development
make dev

# Run tests
make test
```

---

## 🔧 Manual Setup

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start PostgreSQL and Redis (if not using Docker)
# Ensure they're running on default ports

# Run database migrations
alembic upgrade head

# Ingest data
python scripts/ingest_data.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### Step 2: Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local with backend URL

# Start development server
npm run dev

# Access at http://localhost:3000
```

### Step 3: Start Infrastructure Services

```bash
# Using Docker for just infrastructure
docker compose up -d qdrant redis postgres

# Or install locally:
# - Qdrant: https://qdrant.tech/documentation/quick-start/
# - Redis: https://redis.io/docs/getting-started/
# - PostgreSQL: https://www.postgresql.org/download/
```

---

## 📚 API Documentation

### Core Endpoints

#### Query Endpoint
```http
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
  "answer": "Based on the fund performance data...",
  "sources": [
    {
      "type": "fund",
      "fund_name": "Axis Bluechip Fund",
      "relevance_score": 0.92,
      "metrics": {
        "sharpe_ratio": 1.45,
        "cagr_3yr": 12.5
      }
    }
  ],
  "query_type": "numerical",
  "confidence": 0.89,
  "trace_id": "abc123"
}
```

#### Fund Endpoints
```http
GET /api/v1/funds                    # List all funds
GET /api/v1/funds/{fund_id}          # Get fund details
GET /api/v1/funds/compare?ids=1,2,3  # Compare funds
GET /api/v1/funds/summary            # Analytics summary
```

#### Health Check
```http
GET /api/v1/health
```

**Full API documentation available at:** `http://localhost:8000/docs`

---

## 🏗 Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js Dashboard                           │
│  [Chat Interface] [Fund Explorer] [Comparison] [Traces]         │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LangGraph Query Router                      │    │
│  │  [Classify Query] → [Route] → [Retrieve] → [Generate]   │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐    │
│  │   Retrieval   │  │   Generation  │  │   Observability   │    │
│  │   ─────────   │  │   ──────────  │  │   ─────────────   │    │
│  │   BGE-M3      │  │   Claude API  │  │   LangFuse        │    │
│  │   Qdrant      │  │   Instructor  │  │   Tracing         │    │
│  │   BM25        │  │               │  │                   │    │
│  │   Cohere      │  │               │  │                   │    │
│  └───────────────┘  └───────────────┘  └───────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│    Qdrant     │    │  PostgreSQL   │    │    Redis      │
│   (Vectors)   │    │  (Metadata)   │    │   (Cache)     │
└───────────────┘    └───────────────┘    └───────────────┘
```

### Query Classification Strategy

| Query Type | Example | Retrieval Strategy |
|------------|---------|-------------------|
| FAQ | "What is an index fund?" | Semantic search on FAQs |
| Numerical | "Best Sharpe ratio funds" | Metadata filter + semantic |
| Hybrid | "Low risk funds with good returns explained" | Both sources + RRF |

### Hybrid Search: RRF (Reciprocal Rank Fusion)

```
Final_Score = Σ (1 / (k + rank_i))

Where:
- k = 60 (constant)
- rank_i = position in each result list
```

---

## 📊 Evaluation

### Ragas Metrics

| Metric | Score | Description |
|--------|-------|-------------|
| Faithfulness | 0.XX | Answer grounded in sources |
| Answer Relevancy | 0.XX | Answer addresses query |
| Context Precision | 0.XX | Retrieved docs are relevant |
| Context Recall | 0.XX | All relevant docs retrieved |

### Test Query Results

| Query Type | Precision@3 | Latency (p50) | Latency (p99) |
|------------|-------------|---------------|---------------|
| FAQ | 0.XX | XXms | XXms |
| Numerical | 0.XX | XXms | XXms |
| Hybrid | 0.XX | XXms | XXms |

Run evaluation:
```bash
cd backend
python scripts/evaluate.py
```

---

## ⚖️ Trade-offs & Decisions

### Why BGE-M3 over OpenAI Embeddings?
- **Pros**: Multi-vector (dense + sparse), self-hosted, no API costs
- **Cons**: Requires more compute, larger model size
- **Decision**: Better long-term scalability and hybrid search native support

### Why Qdrant over Pinecone/ChromaDB?
- **Pros**: Native hybrid search, self-hosted, excellent filtering
- **Cons**: More infrastructure to manage
- **Decision**: Production-ready features and no vendor lock-in

### Why LangGraph over basic chains?
- **Pros**: Complex routing, state management, easier debugging
- **Cons**: Learning curve, more code
- **Decision**: Better query classification and future extensibility

### Why Cohere Rerank?
- **Pros**: Significant accuracy improvement (10-15%), fast
- **Cons**: API dependency, cost
- **Decision**: Worth the cost for financial domain accuracy

---

## 🔮 Future Improvements

With more time, I would add:

1. **Fine-tuned Embeddings**: Train on financial corpus for better retrieval
2. **Cross-Encoder Reranking**: Replace Cohere with self-hosted model
3. **Streaming Responses**: Real-time generation with SSE
4. **Multi-turn Conversations**: Context-aware follow-up queries
5. **User Feedback Loop**: Learn from thumbs up/down
6. **A/B Testing**: Compare retrieval strategies
7. **Kubernetes Deployment**: Production-ready scaling

---

## 🤝 Contributing

```bash
# Install pre-commit hooks
pre-commit install

# Run tests before committing
make test

# Format code
make format
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Shubham**
- Role: Founding ML/AI Engineer Candidate
- Assignment: Qonfido Mini RAG Challenge

---

## 🙏 Acknowledgments

- Qonfido team for the interesting challenge
- Open source community for amazing tools
