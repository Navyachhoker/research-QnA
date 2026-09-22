# 📚 ResearchGPT

> An AI-powered research assistant that lets users upload research papers, build a personal semantic knowledge base, ask context-aware questions, generate summaries, and compare papers using Retrieval-Augmented Generation (RAG).

---

## 📖 Overview

ResearchGPT is a full-stack RAG application: upload PDFs, and ask natural-language questions grounded in their content instead of searching through them manually. Retrieval is per-user — everything you upload is private to your account.

- Retrieval-Augmented Generation (RAG) over your own papers
- Vector similarity search (ChromaDB + sentence-transformers), fused with BM25 keyword search and cross-encoder reranking
- FastAPI backend, React (Vite) frontend
- JWT authentication, per-user data isolation
- Persistent, named chat sessions with history
- Paper summarization, pairwise comparison, and topic-based related-work generation
- Optional arXiv import (search + direct ingest by arXiv id)

---

## 🏗 Architecture

```
 React (Vite) frontend
          │
       REST API
          │
       FastAPI  ──────────────► JWT auth (bcrypt + python-jose)
          │                          │
          │                       SQLite (users, papers, sessions, messages)
          │
   RAG pipeline
          │
   PyMuPDF (PDF → text) → chunker (word-boundary aware)
          │
   sentence-transformers embeddings ──► ChromaDB (owner_id + paper_id scoped)
          │                                    │
          │                              BM25 keyword search
          │                                    │
          │                          Reciprocal Rank Fusion
          │                                    │
          │                        cross-encoder reranking (optional)
          │
   Groq LLM (chat completions)
          │
     Grounded answer + cited sources
```

---

## 📂 Project structure

```
research-QnA/
├── app/
│   ├── main.py                 # FastAPI app, CORS, error handling
│   ├── config.py                # Settings (env-driven, no import-time crashes)
│   ├── db/                      # SQLAlchemy models + session
│   ├── api/
│   │   ├── routers/             # auth, papers, qa, sessions, analysis
│   │   └── schemas/              # Pydantic request/response models
│   ├── services/                 # business logic, owner-scoped throughout
│   ├── rag/                      # chunking, embeddings, vector store, keyword search, reranking, prompts, generator
│   ├── utils/                    # PDF extraction
│   └── eval/                     # offline retrieval-quality scripts (not part of the API)
├── tests/
│   ├── unit/                     # chunking, PDF parsing, auth, prompts, arxiv client
│   ├── integration/               # full API flows via FastAPI TestClient
│   ├── security/                  # cross-tenant isolation, input validation
│   ├── regression/                 # pinned to specific bugs found in the audit
│   └── conftest.py                # fakes: embedding model, LLM generator; real ChromaDB
├── frontend/                      # React + Vite + Tailwind
├── .github/workflows/ci.yml        # lint, format check, type check, tests+coverage
├── Dockerfile
├── render.yaml
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml                  # pytest / coverage / ruff / black / mypy config
```

---

## 🚀 Setup

### Prerequisites
- Python 3.11+
- Node 18+ (for the frontend)
- A [Groq API key](https://console.groq.com) (free tier available)

### Backend

```bash
git clone https://github.com/Navyachhoker/research-QnA.git
cd research-QnA

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install --extra-index-url https://download.pytorch.org/whl/cpu torch==2.3.1+cpu
pip install -r requirements.txt

cp .env.example .env
# then edit .env and set GROQ_API_KEY and JWT_SECRET_KEY
```

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run it (from the repo root — the app is the `app` package, run as `app.main:app`, not from inside `app/`):
```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL defaults to http://localhost:8000
npm run dev
```

### Docker

```bash
docker build -t researchgpt .
docker run -p 8000:8000 --env-file .env researchgpt
```

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt

pytest                      # runs the full suite with coverage (see pyproject.toml)
ruff check app tests        # lint
black --check app tests     # format check
mypy app                    # type check
```

Tests never call the real Groq API or download the real embedding model — `tests/conftest.py` swaps in a fake LLM generator and a fake (but deterministic, feature-hashed) embedding model, while still exercising a *real* ChromaDB instance, so the owner-scoping logic in `VectorStore` is genuinely tested rather than mocked away.

CI (`.github/workflows/ci.yml`) runs lint, format check, type check, and the test suite with coverage on every push/PR to `main`.

---

## 🔍 Retrieval pipeline

Retrieval is hybrid by default: a vector similarity search (ChromaDB) and a BM25 keyword search each independently rank the owner's chunks, get merged via Reciprocal Rank Fusion, and the fused candidate pool is then reranked by a cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) before the final top-k goes to the LLM. Rationale:

- **Dense embeddings alone regularly miss exact terms** — model names, acronyms, specific numbers — because two chunks sharing a rare token aren't necessarily close together in embedding space. BM25 (term-frequency based) catches exactly those cases; fusing both covers more queries than either alone.
- **A cross-encoder reranker scores the query and chunk jointly** rather than comparing two independently-computed representations, which is more accurate — but too slow to run against a whole corpus, hence it only runs over the ~20-candidate pool the first pass narrows down to, not the whole corpus.

Both stages are independently toggleable via env vars (`ENABLE_HYBRID_SEARCH`, `ENABLE_RERANKING` in `.env.example`) — reranking loads a second small model into memory, so a memory-constrained deployment can disable it without a code change.

**Measuring retrieval quality**: `app/eval/run_eval.py` runs a hand-labeled QA dataset (`app/eval/qa_dataset.py`, written against the BERT and "Attention Is All You Need" papers) through the real pipeline and reports Recall@k, MRR, and LLM-judged faithfulness/relevance. Useful as a before/after comparison when changing retrieval settings — see the module's docstring for setup.

---

## 📌 API reference

### Auth
| Method | Endpoint | Auth |
|---|---|---|
| POST | `/auth/register` | – |
| POST | `/auth/login` | – |
| GET | `/auth/me` | required |

### Papers
| Method | Endpoint | Auth |
|---|---|---|
| POST | `/papers/upload` | required |
| GET | `/papers/list` | required |
| DELETE | `/papers/{paper_id}` | required |
| GET | `/papers/arxiv/search?query=...` | required |
| POST | `/papers/arxiv/import/{arxiv_id}` | required |

### Question answering
| Method | Endpoint | Auth |
|---|---|---|
| POST | `/qa/ask` | required |

`paper` in the request body is a `paper_id` to scope retrieval to a single paper, or omit it to search across everything you've uploaded. `session_id` is optional — pass one to get multi-turn context and persisted history.

### Sessions
| Method | Endpoint | Auth |
|---|---|---|
| POST | `/sessions/` | required |
| GET | `/sessions/` | required |
| GET | `/sessions/{id}/history` | required |
| DELETE | `/sessions/{id}` | required |

### Analysis
| Method | Endpoint | Auth |
|---|---|---|
| POST | `/analysis/summarize` | required |
| POST | `/analysis/compare` | required |
| POST | `/analysis/related-work` | required |

Full interactive schema at `/docs`.

---

## 🔒 Security notes

- Every retrieval, summarization, comparison, and related-work query is scoped by the authenticated user's id, all the way down to the ChromaDB `where` filter — one user's uploaded papers are never visible to another user's queries.
- Passwords are hashed with bcrypt (72-byte truncation applied on the UTF-8 byte boundary, not the character boundary).
- JWTs are HS256-signed; the app refuses to sign or verify tokens if `JWT_SECRET_KEY` isn't set, rather than falling back to a hardcoded default.
- CORS origins are explicit (`ALLOWED_ORIGINS` env var), not wildcarded.
- Uploaded files are validated by extension/content-type and then by actually parsing them with PyMuPDF; a failed parse cleans up the partial upload rather than leaving an orphaned file.
- LLM prompts (`app/rag/prompts.py`) explicitly instruct the model to treat retrieved PDF content as untrusted data, not instructions — a defense against prompt injection via uploaded documents.
- arXiv ids are validated against a strict pattern before being used in a URL or filesystem path.

See `tests/security/` for the tests covering these.

---

## 📈 Possible next steps

- OCR fallback for scanned PDFs with no text layer
- Hybrid search (BM25 + vector) for better keyword-heavy queries
- A real migration tool (Alembic) instead of `create_all()` for schema evolution
- Streaming responses from the LLM
- Rate limiting on auth and upload endpoints

---

## 📄 License

MIT.

## 👩‍💻 Author

**Navya Chhoker**
