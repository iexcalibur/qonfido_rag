# 🎯 Project Objective

## Qonfido RAG - Financial Intelligence System

---

## 📋 Assignment Context

**Company:** Qonfido - Building an AI Co-Pilot for Money  
**Role:** Founding ML/AI Engineer  
**Assignment:** Option #1 - Mini RAG with Financial Data

---

## 🎯 Primary Objective

Build a **Retrieval-Augmented Generation (RAG) pipeline** that can answer financial questions by combining:

1. **Textual Knowledge** - FAQs and fund descriptions
2. **Quantitative Data** - Returns, risks, and performance metrics

---

## 📊 Input Datasets

| Dataset | Description | Source |
|---------|-------------|--------|
| `faqs.csv` | Frequently asked questions about mutual funds | Provided |
| `fund.csv` | Mutual fund performance metrics (CAGR, Sharpe, etc.) | Provided |

---

## ✅ Core Requirements

### 1. Data Preparation
- [ ] Ingest both CSV datasets
- [ ] Create embeddings for textual data (FAQs)
- [ ] Convert numerical fund data to text descriptions
  - Example: *"Fund A has 3yr CAGR of 12%, volatility 8%, Sharpe ratio 1.2"*
- [ ] Store all data in a unified index

### 2. Retrieval System
- [ ] **Lexical Search** - Keyword-based (BM25 / TF-IDF)
- [ ] **Semantic Search** - Embedding similarity (FAISS / Chroma / pgvector)
- [ ] Allow switching between retrieval modes for evaluation

### 3. Query Handling
- [ ] Handle mixed queries combining FAQs and numerical data
- [ ] Return structured responses with:
  - Short text answer
  - List of relevant funds with metrics
  - Source attribution

**Example Queries:**
- *"Which funds have the best Sharpe ratio in the last 3 years?"*
- *"What is an index fund?"*
- *"Show me low-risk funds with good returns"*

### 4. API Interface
- [ ] FastAPI endpoint with:
  - **Input:** User query (string) + retrieval mode flag (lexical/semantic)
  - **Output:** Final answer (string/JSON) + retrieved sources

---

## ⭐ Bonus Features (Optional but Impressive)

| Feature | Status | Description |
|---------|--------|-------------|
| Hybrid Search | [ ] | Combine lexical + semantic using RRF |
| Embedding Cache | [ ] | Cache embeddings for faster retrieval |
| Reranking | [ ] | Use Cohere Rerank for improved accuracy |
| Query Classification | [ ] | Route queries to appropriate retrieval strategy |
| Next.js Dashboard | [ ] | Full-stack UI for demo |
| Evaluation | [ ] | Ragas metrics for RAG quality |

---

## 🏗️ Our Implementation Approach

### Going Beyond Requirements (11/10 Strategy)

We're building a **production-grade system** that demonstrates founding engineer capabilities:

```
Required                          Our Implementation
─────────────────────────────────────────────────────
Simple FastAPI endpoint      →    Full REST API with schemas
Basic BM25 + Vector search   →    Hybrid search with RRF fusion
Return answer + sources      →    Structured JSON with Instructor
Optional caching             →    Redis caching layer
-                            →    LangGraph query orchestration
-                            →    Cohere reranking
-                            →    Next.js dashboard
-                            →    Ragas evaluation
-                            →    Docker deployment
```

---

## 📐 Success Criteria

### Must Have (Assignment Requirements)
- ✅ Ingest both datasets
- ✅ Lexical search (BM25)
- ✅ Semantic search (Vector embeddings)
- ✅ FastAPI endpoint
- ✅ Return answer + sources

### Should Have (Bonus Points)
- ✅ Hybrid search
- ✅ Embedding caching
- ✅ Clean code structure
- ✅ Comprehensive README

### Nice to Have (Wow Factor)
- ✅ Next.js dashboard
- ✅ Query classification
- ✅ Reranking
- ✅ Observability
- ✅ Evaluation metrics
- ✅ Docker setup

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                               │
│         "Which funds have the best Sharpe ratio?"               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY CLASSIFICATION                         │
│              FAQ | Numerical | Hybrid Intent                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RETRIEVAL LAYER                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   BM25      │    │  Semantic   │    │    Hybrid + RRF     │  │
│  │  (Lexical)  │ OR │  (Vector)   │ OR │  (Combined)         │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RERANKING                                 │
│                   Cohere Rerank v3                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GENERATION                                 │
│              Claude API + Instructor                            │
│           (Structured JSON Response)                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RESPONSE                                 │
│  {                                                              │
│    "answer": "Based on the data, these funds have...",          │
│    "funds": [                                                   │
│      { "name": "Axis Bluechip", "sharpe": 1.45, ... }           │
│    ],                                                           │
│    "sources": ["fund_12", "faq_5"],                             │
│    "confidence": 0.92                                           │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Deliverables

| Deliverable | Description |
|-------------|-------------|
| GitHub Repo / ZIP | Complete codebase |
| README.md | Setup instructions, architecture, trade-offs |
| Working API | FastAPI with query endpoint |
| Demo (Bonus) | Next.js dashboard |

---

## 🎯 Key Evaluation Criteria

Based on the assignment description, evaluators are looking for:

1. **Design** - Clean architecture, separation of concerns
2. **Code Quality** - Readable, maintainable, well-documented
3. **Trade-off Reasoning** - Why you chose specific technologies
4. **Creativity** - Going beyond basic requirements

---

## 💡 Trade-off Decisions

| Decision | Reasoning |
|----------|-----------|
| ChromaDB over Qdrant (dev) | No server needed, faster local setup |
| BGE-M3 over OpenAI | Free, no API costs, supports hybrid |
| LangGraph over simple chains | Better query routing, maintainable |
| Hybrid search default | Best accuracy for mixed queries |
| Instructor for outputs | Guaranteed structured JSON |

---

## 📅 Timeline

| Day | Focus |
|-----|-------|
| Day 1 | Backend core: Ingestion + Retrieval |
| Day 2 | Generation + API endpoints |
| Day 3 | Frontend dashboard |
| Day 4 | Testing, polish, documentation |

---

## 🏆 Goal

**Demonstrate that we can:**
- Build production-ready AI systems
- Make thoughtful technical decisions
- Deliver complete, working solutions
- Go beyond requirements with quality

---

*Built for Qonfido Founding ML/AI Engineer Role*
*By Shubham*
