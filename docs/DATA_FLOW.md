````markdown
# 📊 Qonfido RAG System - Data Flow Diagrams

> **Visual representation of data movement through the RAG system**  

> **Format:** Mermaid diagrams (render in GitHub, VS Code, or Mermaid Live Editor)

---

## 📋 Table of Contents

1. [High-Level System Overview](#1-high-level-system-overview)
2. [Backend RAG Pipeline Flow](#2-backend-rag-pipeline-flow)
3. [Hybrid Search Flow (Parallel Retrieval)](#3-hybrid-search-flow-parallel-retrieval)
4. [Frontend Chat Flow](#4-frontend-chat-flow)
5. [Fund Explorer Flow](#5-fund-explorer-flow)
6. [Data Ingestion & Indexing Flow](#6-data-ingestion--indexing-flow)
7. [Query Processing Flow (Detailed)](#7-query-processing-flow-detailed)
8. [Database & Cache Flow](#8-database--cache-flow)
9. [Complete End-to-End Flow](#9-complete-end-to-end-flow)
10. [Response Generation Flow](#10-response-generation-flow)

---

## 1. High-Level System Overview

```mermaid
flowchart TB
    subgraph Input ["📁 INPUT LAYER"]
        USER_QUERY["User Query<br/>Text Question"]
        CSV_FILES["CSV Files<br/>faqs.csv, funds.csv"]
    end

    subgraph Frontend ["🖥️ FRONTEND LAYER"]
        HOME["Homepage<br/>Landing Page"]
        CHAT["Chat Interface<br/>AI Co-Pilot"]
        FUNDS["Fund Explorer<br/>Browse & Filter"]
    end

    subgraph Backend ["⚙️ BACKEND LAYER"]
        API["REST API<br/>FastAPI"]
        
        subgraph RAG_PIPELINE ["RAG Pipeline"]
            INGEST["Ingestion<br/>Data Loading"]
            RETRIEVE["Retrieval<br/>Hybrid Search"]
            GENERATE["Generation<br/>Claude LLM"]
        end
        
        VALIDATE["Validation<br/>Pydantic Schemas"]
    end

    subgraph Storage ["💾 STORAGE LAYER"]
        CHROMADB[("ChromaDB<br/>Vector Store")]
        BM25_INDEX["BM25 Index<br/>Lexical Search"]
        CACHE["Redis/In-Memory Cache<br/>(Active & Integrated)"]
        DATABASE[("PostgreSQL/SQLite<br/>(Async, Optional)")]
    end

    subgraph External ["🌐 EXTERNAL SERVICES"]
        CLAUDE["Claude API<br/>Anthropic"]
        COHERE["Cohere API<br/>Reranking"]
        HUGGINGFACE["HuggingFace<br/>BGE-M3 Model"]
    end

    %% User flow
    USER_QUERY --> HOME
    HOME --> CHAT
    CHAT --> API
    FUNDS --> API

    %% Data ingestion
    CSV_FILES --> INGEST
    INGEST --> CHROMADB
    INGEST --> BM25_INDEX

    %% Query processing
    API --> RETRIEVE
    RETRIEVE --> CHROMADB
    RETRIEVE --> BM25_INDEX
    RETRIEVE --> CACHE
    RETRIEVE --> VALIDATE
    VALIDATE --> GENERATE
    GENERATE --> CLAUDE
    GENERATE --> COHERE

    %% Model loading
    INGEST --> HUGGINGFACE
    RETRIEVE --> HUGGINGFACE

    %% Response
    GENERATE --> API
    API --> CHAT
    API --> FUNDS

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef frontendStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef backendStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageStyle fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef externalStyle fill:#ffebee,stroke:#c62828,stroke-width:2px

    class USER_QUERY,CSV_FILES inputStyle
    class HOME,CHAT,FUNDS frontendStyle
    class API,INGEST,RETRIEVE,GENERATE,VALIDATE backendStyle
    class CHROMADB,BM25_INDEX,CACHE,DATABASE storageStyle
    class CLAUDE,COHERE,HUGGINGFACE externalStyle
````

-----

## 2\. Backend RAG Pipeline Flow

```mermaid
flowchart TD
    START([📥 User Query<br/>POST /api/v1/query]) --> INIT[Initialize Pipeline<br/>RAGPipeline.process]

    INIT --> EMBED[Generate Query Embedding<br/>BGE-M3 Model<br/>1024 dimensions]

    EMBED --> CACHE_CHECK{Check<br/>Embedding Cache?}

    CACHE_CHECK -->|Hit| CACHE_EMBED[Return Cached<br/>Embedding]
    CACHE_CHECK -->|Miss| GEN_EMBED[Generate New<br/>Embedding]
    GEN_EMBED --> SAVE_CACHE[Save to Cache<br/>24hr TTL]

    CACHE_EMBED --> SEARCH_MODE{Search<br/>Mode?}
    GEN_EMBED --> SEARCH_MODE
    SAVE_CACHE --> SEARCH_MODE

    SEARCH_MODE -->|Lexical| LEXICAL[Lexical Search<br/>BM25 Keyword]
    SEARCH_MODE -->|Semantic| SEMANTIC[Semantic Search<br/>ChromaDB Vector]
    SEARCH_MODE -->|Hybrid| HYBRID[Hybrid Search<br/>RRF Fusion + Parallel]

    LEXICAL --> BM25_SEARCH[Search BM25 Index<br/>rank-bm25]
    SEMANTIC --> VECTOR_SEARCH[Search ChromaDB<br/>Cosine Similarity]

    subgraph HybridProcess ["⚡ HYBRID SEARCH (Parallel)"]
        HYBRID --> PARALLEL[Run Lexical & Semantic<br/>Simultaneously<br/>ThreadPoolExecutor]
        PARALLEL --> LEX_RESULTS[Lexical Results]
        PARALLEL --> SEM_RESULTS[Semantic Results]
        LEX_RESULTS --> RRF[RRF Fusion<br/>Reciprocal Rank Fusion]
        SEM_RESULTS --> RRF
        RRF --> FUSED[Fused Results<br/>40-50% faster]
    end

    BM25_SEARCH --> RESULTS
    VECTOR_SEARCH --> RESULTS
    FUSED --> RESULTS

    RESULTS[Search Results<br/>Top K documents] --> RERANK_CHECK{Rerank<br/>Enabled?}

    RERANK_CHECK -->|Yes| RERANK[Cohere Rerank API<br/>Two-stage retrieval<br/>~$0.01/query]
    RERANK_CHECK -->|No| SKIP_RERANK[Skip Reranking]

    RERANK --> RERANKED[Top Reranked Results]
    SKIP_RERANK --> RESULTS_DIRECT

    RERANKED --> CLASSIFY[Classify Query Type<br/>FAQ / Numerical / Hybrid]
    RESULTS_DIRECT --> CLASSIFY

    CLASSIFY --> EXTRACT[Extract Fund Info<br/>From Results<br/>With Cache Fallback]

    EXTRACT --> FORMAT[Format Context<br/>For LLM<br/>Include Metadata]

    FORMAT --> PROMPT[Select Prompt Template<br/>Based on Query Type]

    PROMPT --> LLM_GEN[Generate Response<br/>Claude API<br/>claude-3-opus-20240229]

    LLM_GEN --> CONFIDENCE[Calculate Confidence<br/>Score<br/>0.0 - 1.0]

    CONFIDENCE --> BUILD[Build Response<br/>QueryResponse Schema]

    BUILD --> RETURN([📤 Return Response<br/>JSON Format])

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef processStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef hybridStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:3px
    classDef llmStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef outputStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef decisionStyle fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px

    class START inputStyle
    class INIT,EMBED,CACHE_CHECK,CLASSIFY,EXTRACT,FORMAT,PROMPT processStyle
    class HYBRID,PARALLEL,LEX_RESULTS,SEM_RESULTS,RRF,FUSED hybridStyle
    class LLM_GEN,CONFIDENCE llmStyle
    class RETURN outputStyle
    class SEARCH_MODE,RERANK_CHECK decisionStyle
```

-----

## 3\. Hybrid Search Flow (Parallel Retrieval)

```mermaid
flowchart TD
    START([Query + Embedding]) --> HYBRID_INIT[Initialize HybridSearcher<br/>use_parallel=True]

    HYBRID_INIT --> EXECUTOR[Create ThreadPoolExecutor<br/>max_workers=2]

    EXECUTOR --> PARALLEL_START[Start Parallel Execution<br/>Both searches simultaneously]

    subgraph ParallelExecution ["⚡ PARALLEL SEARCH"]
        direction TB
        
        PARALLEL_START --> THREAD1[Thread 1:<br/>Lexical Search]
        PARALLEL_START --> THREAD2[Thread 2:<br/>Semantic Search]
        
        THREAD1 --> BM25_RUN[Run BM25 Search<br/>rank-bm25 library<br/>Keyword matching]
        THREAD2 --> CHROMA_RUN[Run ChromaDB Search<br/>Cosine similarity<br/>Vector matching]
        
        BM25_RUN --> LEX_WAIT[Wait for<br/>Completion]
        CHROMA_RUN --> SEM_WAIT[Wait for<br/>Completion]
        
        LEX_WAIT --> LEX_RESULTS[Lexical Results<br/>Ranked by BM25 score]
        SEM_WAIT --> SEM_RESULTS[Semantic Results<br/>Ranked by similarity]
    end

    LEX_RESULTS --> WAIT_BOTH[Wait for Both<br/>Threads Complete]
    SEM_RESULTS --> WAIT_BOTH

    WAIT_BOTH --> BUILD_MAPS[Build Result Maps<br/>ID → Rank mapping]

    BUILD_MAPS --> UNIQUE_IDS[Get All Unique<br/>Document IDs]

    UNIQUE_IDS --> CALC_RRF[Calculate RRF Scores<br/>For each document]

    subgraph RRFFormula ["📐 RRF Formula"]
        direction LR
        RRF_FORMULA["RRF_score =<br/>(1-α) × 1/(k+lexical_rank) +<br/>α × 1/(k+semantic_rank)"]
        RRF_PARAMS[k=60, α=0.5<br/>Default values]
    end

    CALC_RRF --> RRF_FORMULA
    RRF_FORMULA --> RRF_PARAMS
    RRF_PARAMS --> MERGE[Merge Results<br/>Combine scores]

    MERGE --> SORT[Sort by RRF Score<br/>Descending order]

    SORT --> TOP_K[Return Top K<br/>Results]

    TOP_K --> OUTPUT([📤 Hybrid Search Results<br/>With both scores])

    %% Performance Note
    PARALLEL_START -.->|40-50% faster| OUTPUT

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef parallelStyle fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    classDef threadStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef rrfStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef outputStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px

    class START inputStyle
    class HYBRID_INIT,EXECUTOR,PARALLEL_START,WAIT_BOTH parallelStyle
    class THREAD1,THREAD2,BM25_RUN,CHROMA_RUN,LEX_WAIT,SEM_WAIT threadStyle
    class BUILD_MAPS,UNIQUE_IDS,CALC_RRF,RRF_FORMULA,RRF_PARAMS,MERGE,SORT rrfStyle
    class TOP_K,OUTPUT outputStyle
```

-----

## 4\. Frontend Chat Flow

```mermaid
flowchart TD
    START([User Opens<br/>/chat Page]) --> INIT[Initialize Chat Page<br/>Suspense Wrapper]

    INIT --> URL_CHECK{URL has<br/>query param?}

    URL_CHECK -->|Yes ?q=query| LOAD_QUERY["Load Query from URL<br/>useSearchParams"]
    URL_CHECK -->|No| WELCOME[Show Welcome Message<br/>WelcomeMessage Component]

    LOAD_QUERY --> CHECK_PROCESSED{Already<br/>Processed?}

    CHECK_PROCESSED -->|No| PREVENT_DOUBLE[Set hasProcessedQuery<br/>useRef flag]
    PREVENT_DOUBLE --> SEND_QUERY
    CHECK_PROCESSED -->|Yes| WELCOME

    WELCOME --> USER_INPUT[User Types Query<br/>ChatInput Component]

    USER_INPUT --> SEARCH_MODE{Select<br/>Search Mode?}
    SEARCH_MODE -->|Lexical| MODE_LEX[Set Mode: lexical]
    SEARCH_MODE -->|Semantic| MODE_SEM[Set Mode: semantic]
    SEARCH_MODE -->|Hybrid| MODE_HYB[Set Mode: hybrid]
    MODE_LEX & MODE_SEM & MODE_HYB --> SUBMIT

    USER_INPUT --> SUBMIT[User Submits<br/>Enter or Button]

    subgraph UseChatHook ["🪝 useChat Hook Logic"]
        direction TB
        SUBMIT --> SET_LOADING[Set isLoading = true]
        SET_LOADING --> ADD_USER_MSG[Add User Message<br/>to State]
        ADD_USER_MSG --> API_CALL[Call Backend API<br/>lib/api.ts → sendQuery]
        API_CALL --> LOADING[Show Loading State<br/>Loader2 Spinner]
        
        LOADING --> RESPONSE[Receive QueryResponse<br/>JSON]
        
        RESPONSE --> TRANSFORM[Transform Data<br/>Funds & Citations]
        TRANSFORM --> UPDATE_STATE[Update Messages State<br/>with AI Response]
    end

    subgraph MessageRendering ["🎨 MESSAGE RENDERING"]
        direction TB
        UPDATE_STATE --> RENDER_MSG[Render ChatMessage]
        
        RENDER_MSG --> CONTENT[Display Answer Text]
        RENDER_MSG --> FUND_GRID["FundAnalysisResults<br/>(Grid of FundInsightCard)"]
        
        FUND_GRID --> CARD_DETAILS[" Fund Card Metrics:<br/>• CAGR (Returns)<br/>• Sharpe Ratio (Progress Bar)<br/>• Volatility (Risk Label)"]
        
        RENDER_MSG --> CITATIONS["CitationChips<br/>(Source Badges with Score)"]
    end
    
    CARD_DETAILS --> DONE
    CITATIONS --> DONE

    DONE --> SCROLL_BOTTOM[Auto-scroll to Bottom<br/>scrollRef]

    SCROLL_BOTTOM --> END([✅ Complete])

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef processStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef hookStyle fill:#e1bee7,stroke:#4a148c,stroke-width:2px
    classDef renderStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef outputStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef loadingStyle fill:#424242,stroke:#212121,stroke-width:2px,color:#ffffff

    class START,USER_INPUT inputStyle
    class INIT,LOAD_QUERY,PREVENT_DOUBLE,CHECK_PROCESSED processStyle
    class SET_LOADING,ADD_USER_MSG,API_CALL,RESPONSE,TRANSFORM,UPDATE_STATE hookStyle
    class RENDER_MSG,CONTENT,FUND_GRID,CARD_DETAILS,CITATIONS renderStyle
    class END outputStyle
    class LOADING loadingStyle
```

-----

## 5\. Fund Explorer Flow

```mermaid
flowchart TD
    START([User Opens<br/>/funds Page]) --> INIT[Initialize Funds Page<br/>useState hooks]

    INIT --> LOAD_FUNDS["Fetch Funds from API<br/>getFunds()"]

    LOAD_FUNDS --> API_CALL[GET /api/v1/funds<br/>Backend API]

    API_CALL --> LOADING[Show Loading State<br/>Loader2 Spinner]

    LOADING --> RESPONSE["Receive FundListResponse<br/>funds[] + total"]

    RESPONSE --> SET_STATE[Set Funds State<br/>useState update]

    SET_STATE --> RENDER_UI[Render UI<br/>Fund Cards Grid]

    RENDER_UI --> USER_ACTION{User<br/>Action?}

    USER_ACTION -->|Search| SEARCH_INPUT[User Types<br/>in Search Box]

    USER_ACTION -->|Filter| FILTER_BUTTON[Click Filter<br/>Category Button]

    USER_ACTION -->|View Fund| FUND_CLICK[Click on<br/>Fund Card]

    USER_ACTION -->|Ask AI| ASK_AI_BUTTON[Click<br/>Ask AI Button]

    SEARCH_INPUT --> CLIENT_FILTER[Client-Side Filtering<br/>Real-time]

    subgraph ClientFiltering ["🔍 CLIENT-SIDE FILTERING"]
        direction TB
        CLIENT_FILTER --> SEARCH_TEXT[Search by:<br/>fund_name, category,<br/>fund_house]
        CLIENT_FILTER --> FILTER_CATEGORY[Filter by:<br/>Category match<br/>Large Cap, Hybrid, etc.]
        SEARCH_TEXT --> COMBINE[Combine Filters<br/>AND logic]
        FILTER_CATEGORY --> COMBINE
        COMBINE --> FILTERED[Filtered Results<br/>Array]
    end

    FILTER_BUTTON --> TOGGLE[Toggle Filter<br/>selectedFilter state]

    TOGGLE --> CLIENT_FILTER

    FILTERED --> UPDATE_GRID[Update Grid Display<br/>React Re-render]

    UPDATE_GRID --> DISPLAY_FUNDS[Display Fund Cards<br/>with Metrics]

    FUND_CLICK --> NAVIGATE["Navigate to<br/>/funds/[fundId]"]

    NAVIGATE --> DETAIL_PAGE[Fund Detail Page<br/>Load fund data]

    ASK_AI_BUTTON --> NAVIGATE_CHAT[Navigate to Chat<br/>/chat?q=Tell me about...]

    NAVIGATE_CHAT --> CHAT_PAGE[Chat Page<br/>Pre-filled Query]

    DISPLAY_FUNDS --> LOOP[Wait for Next<br/>User Action]

    LOOP --> USER_ACTION

    DETAIL_PAGE --> DETAIL_FLOW[Detail Page Flow<br/>See Diagram 9]

    CHAT_PAGE --> CHAT_FLOW[Chat Flow<br/>See Diagram 4]

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef apiStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef filterStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef renderStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef actionStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef decisionStyle fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px
    classDef loadingStyle fill:#424242,stroke:#212121,stroke-width:2px,color:#ffffff

    class START inputStyle
    class LOAD_FUNDS,API_CALL,RESPONSE,SET_STATE apiStyle
    class SEARCH_INPUT,CLIENT_FILTER,SEARCH_TEXT,FILTER_CATEGORY,COMBINE,FILTERED filterStyle
    class RENDER_UI,UPDATE_GRID,DISPLAY_FUNDS renderStyle
    class FUND_CLICK,ASK_AI_BUTTON,NAVIGATE,NAVIGATE_CHAT actionStyle
    class USER_ACTION decisionStyle
    class LOADING loadingStyle
```

-----

## 6\. Data Ingestion & Indexing Flow

```mermaid
flowchart TD
    START([Startup/<br/>Pipeline.initialize]) --> LOAD_CSV[Load CSV Files<br/>DataLoader.load_all]

    LOAD_CSV --> LOAD_FAQS[Load FAQs<br/>from faqs.csv]
    LOAD_FAQS --> PARSE_FAQS[Parse FAQ Rows<br/>FAQItem objects]
    PARSE_FAQS --> FAQ_DOCS[Create FAQ Documents<br/>Combine Q&A]

    LOAD_CSV --> LOAD_FUNDS[Load Funds<br/>from funds.csv]
    LOAD_FUNDS --> PARSE_FUNDS[Parse Fund Rows<br/>FundData objects]

    subgraph TextConversion ["🔤 CRITICAL: Numerical to Text"]
        PARSE_FUNDS --> PROP_ACCESS["Access Property:<br/>FundData.text_for_embedding"]
        PROP_ACCESS --> FORMAT_STR["Format String:<br/>'Fund X: 3yr CAGR 15.2%,<br/>Sharpe 1.25...'"]
        FORMAT_STR --> FUND_DOCS[Create Fund Documents<br/>Ready for Embedding]
    end

    FAQ_DOCS --> COMBINE[Combine All Documents<br/>FAQs + Funds]
    FUND_DOCS --> COMBINE

    COMBINE --> CLEAR_INDEXES[Clear Existing Indexes<br/>Fresh data from CSV]

    CLEAR_INDEXES --> CLEAR_CHROMA[Clear ChromaDB]
    CLEAR_INDEXES --> CLEAR_BM25[Clear BM25 Index]

    CLEAR_CHROMA --> GEN_EMBEDDINGS[Generate Embeddings<br/>BGE-M3 Model]
    
    GEN_EMBEDDINGS --> CHECK_CACHE{Check<br/>Cache?}
    CHECK_CACHE -->|Hit| USE_CACHED[Use Cached]
    CHECK_CACHE -->|Miss| GEN_NEW[Generate New]
    GEN_NEW --> SAVE_TO_CACHE[Save to Cache]

    USE_CACHED --> INDEX_SEMANTIC
    SAVE_TO_CACHE --> INDEX_SEMANTIC

    INDEX_SEMANTIC[Index in ChromaDB<br/>Vector Store] --> INDEX_LEXICAL
    INDEX_LEXICAL[Index in BM25<br/>Lexical Search] --> CACHE_FUNDS

    CACHE_FUNDS[Cache Funds Data<br/>In-Memory (Fast Access)] --> READY

    READY[✅ System Ready<br/>Accept Queries]

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef loadStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef criticalStyle fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px,stroke-dasharray: 5 5
    classDef processStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef indexStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef readyStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px

    class START inputStyle
    class LOAD_CSV,LOAD_FAQS,LOAD_FUNDS loadStyle
    class PARSE_FAQS,PARSE_FUNDS,FAQ_DOCS,FUND_DOCS,COMBINE processStyle
    class PROP_ACCESS,FORMAT_STR criticalStyle
    class CLEAR_INDEXES,INDEX_SEMANTIC,INDEX_LEXICAL indexStyle
    class READY readyStyle
```

-----

## 7\. Query Processing Flow (Detailed)

```mermaid
flowchart TD
    START([📥 POST /api/v1/query<br/>Request Body]) --> VALIDATE_REQ[Validate Request<br/>Pydantic Schema<br/>QueryRequest]

    VALIDATE_REQ --> INIT_PIPELINE[Get Pipeline Instance<br/>get_pipeline]

    INIT_PIPELINE --> EMBED_QUERY[Embed Query Text<br/>BGE-M3 Model<br/>1024-dim vector]

    EMBED_QUERY --> CACHE_CHECK{Check Cache<br/>Query Embedding?}

    CACHE_CHECK -->|Hit| CACHE_EMBED[Use Cached<br/>Embedding]
    CACHE_CHECK -->|Miss| GEN_EMBED[Generate Embedding<br/>BGE-M3.encode]
    GEN_EMBED --> SAVE_EMBED[Save to Cache<br/>TTL: 24hr]

    CACHE_EMBED --> MODE_CHECK{Search Mode<br/>from Request?}

    SAVE_EMBED --> MODE_CHECK

    MODE_CHECK -->|lexical| LEXICAL_FLOW[Lexical Flow]
    MODE_CHECK -->|semantic| SEMANTIC_FLOW[Semantic Flow]
    MODE_CHECK -->|hybrid| HYBRID_FLOW[Hybrid Flow<br/>See Diagram 3]

    subgraph LexicalFlow ["🔤 LEXICAL FLOW"]
        LEXICAL_FLOW --> TOKENIZE[Tokenize Query<br/>Word segmentation]
        TOKENIZE --> BM25_SEARCH[Search BM25 Index<br/>rank-bm25 library]
        BM25_SEARCH --> BM25_RANK[Rank by BM25 Score<br/>Higher = Better Match]
        BM25_RANK --> BM25_RESULTS[Return Top K Results]
    end

    subgraph SemanticFlow ["🧠 SEMANTIC FLOW"]
        SEMANTIC_FLOW --> CHROMA_QUERY[Query ChromaDB<br/>Collection]
        CHROMA_QUERY --> COSINE_SIM[Calculate Cosine<br/>Similarity]
        COSINE_SIM --> SIM_RANK[Rank by Similarity<br/>0.0 - 1.0]
        SIM_RANK --> SEM_RESULTS[Return Top K Results]
    end

    BM25_RESULTS --> RESULTS
    SEM_RESULTS --> RESULTS
    HYBRID_FLOW --> RESULTS

    RESULTS[Search Results<br/>Document List] --> FILTER{Source<br/>Filter?}

    FILTER -->|faq| FAQ_ONLY[Filter to FAQ<br/>Documents Only]
    FILTER -->|fund| FUND_ONLY[Filter to Fund<br/>Documents Only]
    FILTER -->|null| ALL_RESULTS[Keep All<br/>Results]

    FAQ_ONLY --> RERANK_CHECK
    FUND_ONLY --> RERANK_CHECK
    ALL_RESULTS --> RERANK_CHECK

    RERANK_CHECK{Rerank<br/>Enabled?}

    RERANK_CHECK -->|Yes| RERANK[Cohere Rerank API<br/>Two-stage retrieval<br/>Improve precision]
    RERANK_CHECK -->|No| SKIP_RERANK[Skip Reranking<br/>Use Original Results]

    RERANK --> RERANKED[Top Reranked Results<br/>Better Relevance]
    SKIP_RERANK --> ORIGINAL[Original Results]

    RERANKED --> CLASSIFY
    ORIGINAL --> CLASSIFY

    CLASSIFY[Classify Query Type<br/>Keyword Detection<br/>FAQ / Numerical / Hybrid] --> EXTRACT_FUNDS[Extract Fund Information<br/>From Results Metadata<br/>With Cache Fallback]

    EXTRACT_FUNDS --> FORMAT_CONTEXT[Format Context<br/>For LLM<br/>Include Sources]

    FORMAT_CONTEXT --> SELECT_PROMPT[Select Prompt Template<br/>Based on Query Type<br/>prompts.py]

    SELECT_PROMPT --> LLM_CALL[Call Claude API<br/>claude-3-opus-20240229<br/>System + User Prompt]

    LLM_CALL --> LLM_RESPONSE[Receive LLM Response<br/>Generated Answer<br/>Text Format]

    LLM_RESPONSE --> CALC_CONF[Calculate Confidence<br/>Based on:<br/>- Source scores<br/>- Field completeness<br/>- Query type match]

    CALC_CONF --> BUILD_RESPONSE[Build QueryResponse<br/>Schema Object]

    BUILD_RESPONSE --> RETURN([📤 Return JSON<br/>200 OK])

    %% Error Handling
    VALIDATE_REQ -.->|Invalid| ERROR_VALID[400 Bad Request<br/>Validation Error]
    LLM_CALL -.->|API Error| ERROR_LLM[500 Internal Error<br/>LLM Failed]
    ERROR_VALID --> RETURN
    ERROR_LLM --> RETURN

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef validateStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef embedStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef searchStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef llmStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef outputStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef errorStyle fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
    classDef decisionStyle fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px

    class START inputStyle
    class VALIDATE_REQ validateStyle
    class EMBED_QUERY,CACHE_CHECK,GEN_EMBED,SAVE_EMBED embedStyle
    class LEXICAL_FLOW,SEMANTIC_FLOW,HYBRID_FLOW,TOKENIZE,BM25_SEARCH,CHROMA_QUERY searchStyle
    class LLM_CALL,LLM_RESPONSE,CALC_CONF llmStyle
    class BUILD_RESPONSE,RETURN outputStyle
    class ERROR_VALID,ERROR_LLM errorStyle
    class MODE_CHECK,FILTER,RERANK_CHECK decisionStyle
```

-----

## 8\. Database & Cache Flow

```mermaid
flowchart TD
    subgraph Input ["📥 INPUT"]
        QUERY_EMBED[Query Embedding<br/>1024-dim vector]
        DOCUMENTS[Documents<br/>Text + Metadata]
    end

    subgraph EmbeddingCache ["🔵 EMBEDDING CACHE (Active & Integrated)"]
        CHECK_EMBED{Query Embedding<br/>in Cache?}
        CHECK_EMBED -.->|Hit| GET_EMBED[Return Cached<br/>Embedding]
        CHECK_EMBED -.->|Miss| STORE_EMBED[Generate & Store<br/>TTL: 24 hours]
    end

    subgraph QueryCache ["🟢 QUERY CACHE (Active & Integrated)"]
        CHECK_QUERY{Query + Mode<br/>in Cache?}
        CHECK_QUERY -.->|Hit| GET_QUERY[Return Cached<br/>Response]
        CHECK_QUERY -.->|Miss| STORE_QUERY[Store Response<br/>TTL: 5 minutes]
    end

    subgraph ChromaDB ["💜 CHROMADB (Active)"]
        CHROMA_WRITE[Write Documents<br/>with Embeddings]
        CHROMA_READ[Read Similar<br/>Documents]
        CHROMA_CLEAR[Clear Collection<br/>on Startup]
    end

    subgraph BM25Index ["🟡 BM25 INDEX (Active)"]
        BM25_WRITE[Index Documents<br/>Tokenized]
        BM25_READ[Search Index<br/>BM25 Scoring]
    end

    subgraph Database ["🗄️ DATABASE (PostgreSQL/SQLite, Async, Optional)"]
        DB_WRITE[Write Metadata<br/>Funds, FAQs<br/>Async Operations]
        DB_READ[Read Metadata<br/>Async Operations]
    end

    QUERY_EMBED --> CHROMA_READ
    DOCUMENTS --> CHROMA_WRITE
    DOCUMENTS --> BM25_WRITE

    %% Dotted lines indicate logical flow, solid for primary path
    QUERY_EMBED -.-> CHECK_EMBED
    
    CHROMA_READ --> RESULTS
    BM25_READ --> RESULTS

    RESULTS[Search Results] -.-> CHECK_QUERY

    subgraph CacheStrategy ["⚙️ CACHE STRATEGY (Defined in services/cache.py)"]
        direction LR
        STRATEGY["Embedding Cache:<br/>Hash(embedding) → Vector<br/>Query Cache:<br/>Hash(query+mode+top_k) → Response"]
        TTL["TTL:<br/>Embeddings: 24hr<br/>Queries: 5min"]
    end

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef activeStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef infraStyle fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,stroke-dasharray: 5 5
    classDef dbStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,stroke-dasharray: 5 5

    class QUERY_EMBED,DOCUMENTS inputStyle
    class CHROMA_WRITE,CHROMA_READ,CHROMA_CLEAR,BM25_WRITE,BM25_READ activeStyle
    class CHECK_EMBED,GET_EMBED,STORE_EMBED,CHECK_QUERY,GET_QUERY,STORE_QUERY infraStyle
    class DB_WRITE,DB_READ dbStyle
```

-----

## 9\. Complete End-to-End Flow

```mermaid
flowchart TD
    START([👤 USER]) -->|Visits| HOMEPAGE[Homepage<br/>Landing Page<br/>page.tsx]

    HOMEPAGE --> ACTION{User<br/>Action?}

    ACTION -->|Search Query| CHAT_PAGE[Chat Page<br/>/chat]
    ACTION -->|Browse Funds| FUNDS_PAGE[Fund Explorer<br/>/funds]

    subgraph ChatFlow ["💬 CHAT FLOW"]
        CHAT_PAGE --> USER_TYPES["User Types Query<br/>'Best Sharpe ratio funds'"]
        USER_TYPES --> SELECT_MODE[Select Search Mode<br/>Lexical/Semantic/Hybrid]
        SELECT_MODE --> SUBMIT[Submit Query<br/>ChatInput Component]
        SUBMIT --> FRONTEND_API[Frontend API Call<br/>lib/api.ts]
    end

    subgraph FundsFlow ["📊 FUNDS FLOW"]
        FUNDS_PAGE --> LOAD_FUNDS[Load Funds<br/>GET /api/v1/funds]
        LOAD_FUNDS --> DISPLAY_GRID[Display Grid<br/>Fund Cards]
        DISPLAY_GRID --> USER_CLICKS{User<br/>Action?}
        USER_CLICKS -->|Ask AI| NAV_TO_CHAT[Navigate to Chat<br/>with Pre-filled Query]
        USER_CLICKS -->|View Details| NAV_TO_DETAIL["Fund Detail Page<br/>/funds/[fundId]"]
        NAV_TO_CHAT --> CHAT_PAGE
    end

    FRONTEND_API --> BACKEND_API[Backend API<br/>FastAPI Endpoint<br/>POST /api/v1/query]

    subgraph BackendProcessing ["⚙️ BACKEND PROCESSING"]
        BACKEND_API --> RAG_PIPELINE[RAG Pipeline<br/>pipeline.py]
        RAG_PIPELINE --> EMBED[Embed Query<br/>BGE-M3]
        EMBED --> SEARCH[Hybrid Search<br/>Parallel Retrieval]
        SEARCH --> RETRIEVE[Retrieve Documents<br/>FAQs + Funds]
        RETRIEVE --> RERANK[Rerank Results<br/>Cohere API]
        RERANK --> GENERATE[Generate Answer<br/>Claude API]
        GENERATE --> RESPONSE[Build Response<br/>QueryResponse]
    end

    RESPONSE --> FRONTEND_RECV[Frontend Receives<br/>Response JSON]

    FRONTEND_RECV --> PARSE_RESPONSE[Parse Response<br/>Extract Data]

    PARSE_RESPONSE --> DISPLAY_ANSWER[Display Answer<br/>ChatMessage Component]

    DISPLAY_ANSWER --> DISPLAY_FUNDS{Funds<br/>in Response?}

    DISPLAY_FUNDS -->|Yes| FUND_CARDS[Fund Analysis Results<br/>Grid of Cards<br/>CAGR, Sharpe, Volatility]
    DISPLAY_FUNDS -->|No| SKIP_CARDS

    FUND_CARDS --> CITATIONS[Display Citations<br/>Source Badges]
    SKIP_CARDS --> CITATIONS

    CITATIONS --> END_CHAT([✅ Complete])

    subgraph DataFlow ["📊 DATA FLOW"]
        direction TB
        CSV[CSV Files<br/>faqs.csv, funds.csv] --> INGEST[Data Ingestion<br/>Startup]
        INGEST --> EMBEDDINGS[Generate Embeddings<br/>BGE-M3 Model]
        EMBEDDINGS --> CHROMADB[(ChromaDB<br/>Vector Store)]
        EMBEDDINGS --> BM25[BM25 Index<br/>Lexical]
        CHROMADB --> SEARCH
        BM25 --> SEARCH
    end

    CSV --> INGEST

    %% Styling
    classDef userStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef frontendStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef backendStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef storageStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef dataStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef decisionStyle fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px

    class START,END_CHAT userStyle
    class HOMEPAGE,CHAT_PAGE,FUNDS_PAGE,USER_TYPES,SELECT_MODE,SUBMIT,FRONTEND_API,FRONTEND_RECV,PARSE_RESPONSE,DISPLAY_ANSWER,FUND_CARDS,CITATIONS frontendStyle
    class BACKEND_API,RAG_PIPELINE,EMBED,SEARCH,RETRIEVE,RERANK,GENERATE,RESPONSE backendStyle
    class CHROMADB,BM25 storageStyle
    class CSV,INGEST,EMBEDDINGS dataStyle
    class ACTION,USER_CLICKS,DISPLAY_FUNDS decisionStyle
```

-----

## 10\. Response Generation Flow

```mermaid
flowchart TD
    START([Search Results<br/>Retrieved]) --> CLASSIFY[Classify Query Type<br/>Keyword Detection]

    CLASSIFY --> QUERY_TYPE{Query<br/>Type?}

    QUERY_TYPE -->|FAQ| FAQ_PROMPT[Use FAQ Prompt<br/>prompts.py]
    QUERY_TYPE -->|Numerical| NUM_PROMPT[Use Numerical Prompt<br/>emphasize metrics]
    QUERY_TYPE -->|Hybrid| HYBRID_PROMPT[Use Hybrid Prompt<br/>combine both]

    FAQ_PROMPT --> FORMAT_FAQ
    NUM_PROMPT --> FORMAT_NUM
    HYBRID_PROMPT --> FORMAT_HYBRID

    subgraph FormatContext ["📝 FORMAT CONTEXT"]
        FORMAT_FAQ[Format Context<br/>FAQ-focused]
        FORMAT_NUM[Format Context<br/>Fund-focused]
        FORMAT_HYBRID[Format Context<br/>Combined]
        
        FORMAT_FAQ --> INCLUDE_SOURCES[Include Source Documents<br/>with Metadata]
        FORMAT_NUM --> INCLUDE_SOURCES
        FORMAT_HYBRID --> INCLUDE_SOURCES
        
        INCLUDE_SOURCES --> ADD_INSTRUCTIONS[Add Instructions<br/>- Answer format<br/>- Metric extraction<br/>- Source citation]
    end

    ADD_INSTRUCTIONS --> BUILD_PROMPT[Build Full Prompt<br/>System + User]

    BUILD_PROMPT --> CLAUDE_CALL[Call Claude API<br/>claude-3-opus-20240229]

    subgraph ClaudeAPI ["🤖 CLAUDE API"]
        CLAUDE_CALL --> SEND[Send Request<br/>POST /v1/messages]
        SEND --> WAIT[Wait for Response<br/>Stream/Non-stream]
        WAIT --> RECEIVE[Receive Response<br/>Generated Text]
        RECEIVE --> PARSE_JSON{Response<br/>Format?}
        PARSE_JSON -->|JSON| PARSE[Parse JSON<br/>Extract Fields]
        PARSE_JSON -->|Text| CLEAN[Clean Text<br/>Remove Markdown]
    end

    PARSE --> EXTRACT_FIELDS
    CLEAN --> EXTRACT_FIELDS

    EXTRACT_FIELDS[Extract Fields<br/>Answer, Funds, etc.] --> EXTRACT_FUNDS[Extract Fund Info<br/>From Metadata<br/>Fallback to Cache]

    EXTRACT_FUNDS --> CALC_CONF[Calculate Confidence<br/>Score Calculation]

    subgraph ConfidenceCalc ["📊 CONFIDENCE CALCULATION"]
        CALC_CONF --> CHECK_SCORES[Check Source Scores<br/>Average relevance]
        CHECK_SCORES --> CHECK_COMPLETE[Check Field Completeness<br/>Required fields present]
        CHECK_COMPLETE --> CHECK_TYPE[Check Query Type Match<br/>Expected vs Actual]
        CHECK_TYPE --> COMBINE_CONF[Combine Factors<br/>Weighted Average]
        COMBINE_CONF --> CONF_SCORE[Confidence Score<br/>0.0 - 1.0]
    end

    CONF_SCORE --> BUILD_RESPONSE[Build QueryResponse<br/>Schema Object]

    BUILD_RESPONSE --> VALIDATE_RESPONSE{Validate<br/>Response?}

    VALIDATE_RESPONSE -->|Valid| RETURN([📤 Return Response<br/>JSON Format])
    VALIDATE_RESPONSE -->|Invalid| ERROR_HANDLE[Error Handling<br/>Default Response]

    ERROR_HANDLE --> RETURN

    subgraph ResponseStructure ["📦 RESPONSE STRUCTURE"]
        direction TB
        RETURN --> RESP_STRUCT["{<br/>answer: string,<br/>query_type: 'faq'|'numerical'|'hybrid',<br/>funds: FundInfo[],<br/>sources: SourceDocument[],<br/>confidence: number,<br/>search_mode: string<br/>}"]
    end

    %% Styling
    classDef inputStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef classifyStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef promptStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef apiStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef confStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef outputStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef errorStyle fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
    classDef decisionStyle fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px

    class START inputStyle
    class CLASSIFY,QUERY_TYPE classifyStyle
    class FAQ_PROMPT,NUM_PROMPT,HYBRID_PROMPT,FORMAT_FAQ,FORMAT_NUM,FORMAT_HYBRID,INCLUDE_SOURCES,ADD_INSTRUCTIONS,BUILD_PROMPT promptStyle
    class CLAUDE_CALL,SEND,WAIT,RECEIVE,PARSE,CLEAN apiStyle
    class CALC_CONF,CHECK_SCORES,CHECK_COMPLETE,CHECK_TYPE,COMBINE_CONF,CONF_SCORE confStyle
    class BUILD_RESPONSE,RETURN,RESP_STRUCT outputStyle
    class ERROR_HANDLE errorStyle
    class QUERY_TYPE,PARSE_JSON,VALIDATE_RESPONSE decisionStyle
```

```
```