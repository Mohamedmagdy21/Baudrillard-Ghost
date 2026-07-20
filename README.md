<div align="center">

# 🟢 BAUDRILLARD'S GHOST

### *The Simulation Has Already Begun*

> *"The simulacrum is never that which conceals the truth—it is the truth which conceals that there is none."*  
> **— Jean Baudrillard, *Simulacra and Simulation***

<br>

[![Framework](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vector DB](https://img.shields.io/badge/Qdrant-5C2D91?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![LLM](https://img.shields.io/badge/GLM--5.2-FF6F00?style=for-the-badge&logo=openai&logoColor=white)](https://bigmodel.cn/)
[![Local](https://img.shields.io/badge/Qwen_3-0769AD?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Cohere](https://img.shields.io/badge/Cohere_Rerank-3955A3?style=for-the-badge&logo=cohere&logoColor=white)](https://cohere.com/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

<br>

```
  ██████╗  █████╗ ██╗   ██╗██████╗ ██████╗ ██╗██╗      █████╗ ██████╗ ██████╗
  ██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔══██╗██║██║     ██╔══██╗██╔══██╗██╔══██╗
  ██████╔╝███████║██║   ██║██║  ██║██████╔╝██║██║     ███████║██║  ██║██████╔╝
  ██╔══██╗██╔══██║██║   ██║██║  ██║██╔══██╗██║██║     ██╔══██║██║  ██║██╔══██╗
  ██████╔╝██║  ██║╚██████╔╝██████╔╝██║  ██║██║███████╗██║  ██║██████╔╝██║  ██║
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
                                                                                
 ╔═══════════════════════════════════════════════════════════════════════════════╗
 ║              GHOST — Generative Hyper-Optical Semantic Transcoder           ║
 ║         A Modular, Plug-and-Play RAG Pipeline for the Post-Truth Age        ║
 ╚═══════════════════════════════════════════════════════════════════════════════╝
```

</div>

---

## 🧬 The Philosophy

**Baudrillard's Ghost** is not just a RAG pipeline—it's a **simulation engine**. Inspired by the recursive, hyperreal world of *The Matrix* (where Baudrillard's *Simulacra and Simulation* literally appears as a prop), this project builds an **AI that consumes, understands, and simulates knowledge**.

The end goal? **AI as the simulation.** When you ingest a corpus—whether it's legal documents, corporate wikis, academic papers, or a thousand-page novel—the ghost doesn't just retrieve answers. It *simulates understanding*. It *becomes* the document.

> *"Welcome to the desert of the real."* — Morpheus, *The Matrix*

---

## 🔌 Modular Architecture — Plug In, Plug Out

This project is built around **provider abstractions** for every critical component. Swap backends with a single `.env` variable:

| Layer | Providers | Status |
|-------|-----------|--------|
| **Embedding** | Cohere (`embed-v4.0`), GLM/Z.AI | ✅ |
| **Generation** | GLM 5.2, Cohere, Qwen (via Ollama) | ✅ |
| **Query Rewriter** | GLM (BigModel API), Qwen 3 (local Ollama) | ✅ |
| **Cross-Encoder Reranker** | Cohere Rerank, sentence-transformers | ✅ |
| **Vector Database** | Qdrant (local/Docker), pgvector | ✅ |
| **Document Store** | MongoDB, PostgreSQL (asyncpg) | ✅ |
| **File Ingestion** | PDF (unstructured.io), TXT | ✅ |

**Want to swap from Cohere to a local embedding model?** Change one env var.  
**Want to switch from GLM to a local Qwen 3 for generation?** Change one env var.  
**Want to disable the reranker entirely?** Empty string in `.env`.

No code changes. No rebuilds. **The architecture is agnostic by design.**

---

## 🏗️ The Pipeline

```
                        ┌─────────────────────────────────────────┐
                        │          RAW DOCUMENT (PDF/TXT)          │
                        └─────────────────┬───────────────────────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────────────┐
                        │       INGESTION (unstructured.io)        │
                        │  Semantic Chunking + Chapter/Page Meta   │
                        └─────────────────┬───────────────────────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────────────┐
                        │          EMBED (Cohere / GLM)            │
                        │    Bi-Encoder → Vector Embeddings        │
                        └─────────────────┬───────────────────────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────────────┐
                        │       STORE (Qdrant / pgvector)          │
                        │  HNSW Index + Metadata Payload           │
                        └─────────────────┬───────────────────────┘
                                          │
                      ┌───────────────────┴───────────────────┐
                      │                                       │
                      ▼                                       ▼
        ┌───────────────────────────┐          ┌───────────────────────────┐
        │      SEMANTIC SEARCH       │          │     RAG QUERY FLOW        │
        │  Bi-Encoder → Cosine Sim   │          │                           │
        │  Top-K Retrieval           │          │  User Query               │
        └───────────────────────────┘          │     │                     │
                                               │     ▼                     │
                                               │  ┌──────────┐            │
                                               │  │ REWRITER │  (Qwen 3   │
                                               │  │ AGENT    │   / GLM)   │
                                               │  └────┬─────┘            │
                                               │       │                  │
                                               │       ▼                  │
                                               │  ┌──────────┐            │
                                               │  │  EMBED   │            │
                                               │  └────┬─────┘            │
                                               │       │                  │
                                               │       ▼                  │
                                               │  ┌──────────┐            │
                                               │  │ VECTOR   │  Over-     │
                                               │  │ SEARCH   │  fetch 20  │
                                               │  └────┬─────┘            │
                                               │       │                  │
                                               │       ▼                  │
                                               │  ┌──────────┐            │
                                               │  │ RERANKER │  Cross-    │
                                               │  │          │  encoder   │
                                               │  └────┬─────┘  Top 5    │
                                               │       │                  │
                                               │       ▼                  │
                                               │  ┌──────────┐            │
                                               │  │ GENERATE │  GLM 5.2 / │
                                               │  │          │  Qwen      │
                                               │  └──────────┘            │
                                               │                           │
                                               └───────────────────────────┘
```

### Agentic Query Rewriting

The rewriter agent uses **Qwen 3 4B (local via Ollama)** or **GLM 5.2** to improve search queries:

1. **Rewrite** — Fix typos, expand abbreviations, remove filler words
2. **Embed & Search** — Find relevant documents
3. **Evaluate** — Score relevance (cosine similarity). If below threshold, retry with different phrasing
4. **Best Result** — Return the iteration with highest avg score

### Cross-Encoder Reranking

After retrieval, a **cross-encoder** re-ranks the candidates:

- **Cohere Rerank** (`rerank-english-v3.0`) — cloud API, production-ready
- **sentence-transformers** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) — local, offline, free

Over-fetch 20 → rerank → return top 5. The cross-encoder catches relevance signals that cosine similarity misses.

---

## 💼 Use Cases — Beyond the Demo

This is **not a toy**. The modular design makes it adaptable to any knowledge domain:

### ⚖️ Legal Research / Law Search
Ingest case law, statutes, regulations. The semantic chunking preserves chapter/article metadata. Lawyers query by concept, not keyword. The ghost retrieves precedent with context.

### 🏢 Corporate Brain / Enterprise Knowledge Base
Ingest every internal document — onboarding manuals, architecture decisions, RFCs, HR policies, product specs. Employees ask questions in plain English. The ghost surfaces the exact document, section, and page.

### 🎓 Academic Research
Ingest papers, theses, textbooks. The agent rewrites vague research questions into precise search queries. Chapter/section metadata preserves citations.

### 🏥 Medical Knowledge Retrieval
Ingest clinical guidelines, drug formularies, research papers. Semantic search finds treatments by symptom description, not just exact drug names.

### 🛠️ DevOps / Internal Tooling
Ingest runbooks, incident postmortems, configuration guides. "Why did the database fail last week?" — the ghost retrieves the postmortem, the change that caused it, and the fix.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (for MongoDB + Qdrant)
- [Ollama](https://ollama.com/) (optional, for local models)

### 1. Clone & Setup

```bash
git clone https://github.com/Mohamedmagdy21/Baudrillard-Ghost.git
cd Baudrillard-Ghost
python -m venv .venv && source .venv/bin/activate
pip install -r src/requirements.txt
```

### 2. Launch Infrastructure

```bash
docker compose -f docker/docker-compose.yaml up -d
```

This starts:
- **MongoDB** on `localhost:27007`
- **Qdrant** on `localhost:6333`
- **pgvector** on `localhost:5430` (optional)

### 3. Configure `.env`

```bash
cp src/.env.example src/.env
```

Edit `src/.env`:

| Variable | Purpose | Example |
|----------|---------|---------|
| `COHERE_API_KEY` | Embeddings & reranker | `cohere_xxx...` |
| `ZAI_API_KEY` | GLM generation via Z.AI | `xxx.yyy...` |
| `ZAI_URL` | Z.AI API endpoint | `https://api.z.ai/api/paas/v4` |
| `REWRITER_BASE_URL` | Agent rewriter endpoint | `http://localhost:11434/v1` |
| `REWRITER_MODEL` | Rewriter model | `qwen3:4b` |
| `RERANKER_BACKEND` | Reranker provider | `COHERE` or `SENTENCE_TRANSFORMERS` |

**For local-only mode (no API keys):**
```env
GENERATION_BACKEND="GLM"
EMBEDDING_BACKEND="COHERE"
# Use Ollama for rewriting
REWRITER_BASE_URL="http://localhost:11434/v1"
REWRITER_API_KEY="ollama"
REWRITER_MODEL="qwen3:4b"
```

### 4. Run Ollama (Optional — for Local Rewriter)

```bash
ollama pull qwen3:4b
ollama serve
```

### 5. Start the Server

```bash
uvicorn src.main:app --reload --port 8000
```

### 6. Open the UI

Navigate to **[http://localhost:8000/ui](http://localhost:8000/ui)**

### 7. Pipeline Walkthrough

1. **Enter a Project ID** — (e.g., `simulacra`) → Save
2. **Upload a File** — PDF or TXT, drag & drop
3. **Process** — chunks with chapter/page metadata
4. **Index** — embed & push to Qdrant
5. **Search** — semantic vector search
6. **Ask** — full RAG pipeline with rewrite → retrieve → rerank → generate

---

## 🧠 Model Support

### Embedding Models
| Model | Provider | Dimensions | Type |
|-------|----------|------------|------|
| `embed-v4.0` | Cohere | 1536 | Cloud API |
| `glm-5.2` | Z.AI / BigModel | 1024 | Cloud API |

### Generation Models
| Model | Provider | Type |
|-------|----------|------|
| `glm-5.2` | Z.AI / BigModel | SOTA cloud LLM |
| `qwen3:4b` | Ollama (local) | Local, 4B params |
| Command R+ | Cohere | Cloud API |

### Reranker Models
| Model | Provider | Type |
|-------|----------|------|
| `rerank-english-v3.0` | Cohere | Cloud cross-encoder |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | HuggingFace (local) | Local cross-encoder |

### Query Rewriter
| Model | Endpoint | Context |
|-------|----------|---------|
| `qwen3:4b` | `http://localhost:11434/v1` | Local, 256K context |
| `glm-5.2` | `https://api.z.ai/api/paas/v4` | Cloud, 128K context |

---

## 🏛️ Project Structure

```
Baudrillard-Ghost/
├── docker/
│   └── docker-compose.yaml      # Infrastructure (MongoDB, Qdrant, pgvector)
└── src/
    ├── main.py                   # FastAPI server, lifespan, DI wiring
    ├── .env.example              # Configuration template
    ├── requirements.txt          # Python dependencies
    ├── static/
    │   └── index.html            # Single-page web UI
    ├── agents/
    │   ├── QueryRewriterAgentInterface.py  # Abstract rewriter base
    │   └── providers/
    │       └── OpenAiProvider.py           # OpenAI-compatible rewriter (Qwen/GLM)
    ├── controllers/
    │   ├── BaseController.py
    │   ├── DataController.py
    │   ├── ProjectController.py
    │   ├── NLPController.py      # Search, index, RAG answer orchestration
    │   └── ProcessController.py  # Semantic chunking with chapter/page metadata
    ├── helpers/
    │   └── config.py             # Pydantic settings reader
    ├── models/
    │   ├── db_schema/
    │   │   ├── data_chunk.py     # DataChunk + RetrievedDocument
    │   │   ├── chunk_metadata.py # ChunkMetaData (book, chapter, page)
    │   │   ├── AgenticResponseModel.py
    │   │   └── ...
    │   └── ...
    ├── routes/
    │   ├── base.py               # GET /api/v1/
    │   ├── data.py               # Upload & Process endpoints
    │   ├── nlp.py                # Search, Index, RAG Answer endpoints
    │   └── schemes/
    │       ├── data.py           # ProcessRequest schema
    │       └── nlp.py            # PushRequest, SearchRequest schemas
    └── stores/
        ├── llm/
        │   ├── LLMInterface.py           # Abstract LLM provider base
        │   ├── LLMProviderFactory.py     # Provider factory (Cohere, GLM)
        │   ├── LLMEnums.py
        │   └── providers/
        │       ├── CohereProvider.py     # Cohere embeddings + generation
        │       └── GlmProvider.py        # GLM 5.2 generation
        ├── vectordb/
        │   ├── VectorDBInterface.py      # Abstract vector DB base
        │   ├── VectorDBFactory.py
        │   └── providers/
        │       └── QdrantDB.py           # Qdrant operations
        └── reranker/
            ├── RerankerInterface.py      # Abstract reranker base
            ├── RerankerFactory.py        # Provider factory
            └── providers/
                ├── CohereReranker.py     # Cohere Rerank API
                └── SentenceTransformersReranker.py  # Local cross-encoder
```

---

## ⚡ API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/` | Welcome & app info |
| `POST` | `/api/v1/data/upload/{project_id}` | Upload a file (multipart) |
| `POST` | `/api/v1/data/process/{project_id}` | Process file into semantic chunks |
| `POST` | `/api/v1/nlp/push/index/{project_id}` | Index chunks into vector DB |
| `GET` | `/api/v1/nlp/index/info/{project_id}` | Get collection stats |
| `POST` | `/api/v1/nlp/index/search/{project_id}` | Semantic vector search |
| `POST` | `/api/v1/nlp/index/answer/{project_id}` | Full RAG query → answer |

---

## 🔮 The Simulation Continues

This is **version 0.1** of the ghost. The architecture is built to grow:

- **Multi-modal ingestion** — images, audio, video via embedding fusion
- **Graph-based retrieval** — knowledge graphs for entity-aware search
- **Memory** — persistent conversation history with long-term context
- **Multi-agent debate** — multiple LLMs discussing to reach consensus answers
- **Streaming** — token-by-token response streaming via Server-Sent Events

> *The ghost is not a chatbot. It's a simulation of knowledge. And the simulation is recursive.*

---

<div align="center">

<br>

**Built with ☕ and existential dread by [Mohamed Magdy](https://github.com/Mohamedmagdy21)**

*"There is no spoon."* — Neo, *The Matrix*

```
  ════════════════════════════════════════════════════════
   BAUDRILLARD'S GHOST  •  v0.1  •  THE SIMULATION LIVES
  ════════════════════════════════════════════════════════
```

</div>
