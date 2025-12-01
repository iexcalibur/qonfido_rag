Based on the comprehensive project files you uploaded, specifically the architecture documentation and the codebase itself, here is a breakdown of what you need to know to explain the Qonfido RAG project confidently.

Since you have the docs/ARCHITECTURE_AND_DESIGN_DECISIONS.md file, you effectively have a "cheat sheet" for the interview. That document was written to justify every major technical choice. Study it closely.

1. High-Level Project Summary
What is it? A Financial Intelligence RAG (Retrieval-Augmented Generation) system. It allows users to ask natural language questions about mutual funds (e.g., "Which funds have the best Sharpe ratio?") and get answers backed by data and FAQs.

Key Stack:

Backend: FastAPI (Python).

Frontend: Next.js 16 (React/TypeScript).

Database/Storage: ChromaDB (Vector Store), In-Memory Cache, CSV files.

AI/ML: BGE-M3 (Embeddings), Claude 3 Opus (LLM), Cohere (Reranking).

2. Critical Technical Concepts & Interview Questions
The interviewer will likely drill down into why you made specific choices. Here are the expected questions and the answers derived from your code.

A. The "Hybrid Search" Implementation
Question: "How does your retrieval system work? Why didn't you just use vector search?"

Answer: You implemented Hybrid Search using Reciprocal Rank Fusion (RRF).

Logic: Financial queries need both exact keyword matching (e.g., "Axis Bluechip Fund") and semantic understanding (e.g., "safe funds").

Lexical: You used BM25 for exact keyword matches.

Semantic: You used ChromaDB with BGE-M3 embeddings for meaning-based search.

Fusion: You combined them using RRF (ranking position based) rather than just adding scores, which avoids needing to normalize disparate score scales.

Optimization: You ran these searches in parallel using ThreadPoolExecutor to reduce latency by ~40%.

B. Handling Numerical Data in RAG
Question: "LLMs and Embeddings are bad at math and raw numbers. How did you handle structured financial data like CAGR or Sharpe Ratios?"

Answer: You used a "Numerical-to-Text" ingestion strategy.

Instead of just embedding raw numbers, your loader.py script converts structured row data into descriptive text sentences before embedding them.

Example: A row {"sharpe": 1.25} becomes text: "Fund X has a Sharpe Ratio of 1.25...". This allows the vector model to semantically find "good risk-adjusted returns."

C. Smart Persistence & Startup Time
Question: "Ingesting data takes time. Does your app re-index everything every time it restarts?"

Answer: No, you implemented Hash-Based Smart Persistence.

On startup, the system calculates an MD5 hash of the CSV data files and the configuration.

It compares this hash to a saved state file (index.state).

If the hash matches, it loads the existing ChromaDB index from disk (instant startup). If it differs, it triggers a re-index. This ensures data freshness without sacrificing development speed.

D. Caching Strategy
Question: "How do you handle latency? LLMs are slow."

Answer: You implemented a Multi-Level Caching strategy.

Embedding Cache: Caches the vector representation of queries (using SHA-256 of text) to avoid re-running the embedding model (24h TTL).

Query Cache: Caches the final RAG response for identical queries (5m TTL) for instant answers.

Decision: You stuck with In-Memory caching for the MVP to keep the architecture simple (no Redis dependency yet), but structured the code to swap it easily.

E. Frontend-Backend Integration
Question: "How does the frontend talk to the backend? How do you handle slow responses?"

Answer:

The frontend uses Next.js with API Rewrites (next.config.js) to proxy requests to the FastAPI backend, avoiding CORS issues in development.

You use custom hooks (useChat, useFunds) for state management.

The chat interface handles loading states and renders markdown responses.

3. Preparation Plan
To go from knowing 20% to 100%, perform these specific tasks:

Read the "Decisions" Document: The file docs/ARCHITECTURE_AND_DESIGN_DECISIONS.md is essentially your interview script. Read it three times. It explains why you chose ChromaDB over Qdrant, why BGE-M3, etc.

Understand the Data Flow: Look at docs/DATA_FLOW.md. Trace the path of a user query:

Query -> API -> Pipeline -> Embedding -> Hybrid Search (Parallel) -> Reranking (Cohere) -> LLM Generation -> Response.

Check pipeline.py: This is the "brain" of your backend. Open backend/app/core/orchestration/pipeline.py and read the process method. This is where the logic lives.

4. Prompts to Use with your AI Assistant
Use these prompts to have your AI explain the code to you in detail:

Prompt 1 (General Architecture):

"I have the file docs/DEEP_ARCHITECTURE.md. Act as a Senior Engineer. Walk me through the 'RAG Pipeline' section step-by-step. Explain what 'Hybrid Search with RRF Fusion' means in simple terms and why it is better than just vector search."

Prompt 2 (Code Logic):

"Look at backend/app/core/orchestration/pipeline.py. Explain the initialize method. How does the hash-based change detection work? Why is calculating an MD5 hash of the CSV files important here?"

Prompt 3 (Frontend):

"Explain how frontend/src/hooks/index.ts manages the chat state. specifically the useChat hook. How does it handle the API request and update the message list?"

Prompt 4 (Mock Interview):

"Act as a hiring manager interviewing me for a Founding ML Engineer role. Ask me tough questions about the scalability of using ChromaDB in-process and In-Memory caching as seen in backend/app/services/cache.py. Critique my answers."