"""
Central configuration for ResearchGPT.

Design notes (read before touching this file):
- Nothing here raises at import time. A missing secret (GROQ_API_KEY,
  JWT_SECRET_KEY) is a real problem, but raising during `import app.config`
  means the module can never be imported for tooling, linting, or tests
  without live secrets configured. Instead, the pieces that actually need
  a secret (the LLM client, the JWT signer) validate it lazily, the first
  time it's used, with a clear error message.
- Everything is exposed through a single `settings` object so the rest of
  the codebase has one consistent way to reach configuration.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _get_list(name: str, default: list[str]) -> list[str]:
    val = os.getenv(name)
    if not val:
        return default
    return [item.strip() for item in val.split(",") if item.strip()]


class Settings:
    # --- LLM / Groq ---
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1024"))

    # --- Embeddings / retrieval ---
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    top_k: int = int(os.getenv("TOP_K", "5"))
    # Chroma uses cosine *distance* by default (0 = identical, 2 = opposite).
    # Chunks farther than this from the query are dropped even if they made
    # the top-k cut, so a near-empty knowledge base doesn't force in
    # irrelevant filler as "context" for the LLM.
    max_retrieval_distance: float = float(os.getenv("MAX_RETRIEVAL_DISTANCE", "1.1"))

    # --- Hybrid search + reranking ---
    # Hybrid search (BM25 keyword + vector) and cross-encoder reranking
    # both cost extra latency and (for reranking) extra memory to load a
    # second model — toggleable so a memory-constrained deployment (e.g.
    # a free-tier host) can disable reranking without a code change.
    enable_hybrid_search: bool = _get_bool("ENABLE_HYBRID_SEARCH", True)
    enable_reranking: bool = _get_bool("ENABLE_RERANKING", True)
    reranker_model: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    # How many candidates the first pass (vector + BM25, fused) gathers
    # before reranking narrows down to top_k. Larger = better recall for
    # the reranker to work with, at the cost of more BM25/rerank work.
    retrieval_candidate_pool: int = int(os.getenv("RETRIEVAL_CANDIDATE_POOL", "20"))

    # --- Chunking ---
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    # --- Paths ---
    base_dir: Path = BASE_DIR
    chroma_dir: Path = Path(os.getenv("CHROMA_PATH", str(BASE_DIR / "chroma_db")))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    data_dir: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
    papers_dir: Path = data_dir / "papers"

    # --- Uploads ---
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "25"))

    # --- Database ---
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'researchgpt.db'}")

    # --- Auth / JWT ---
    jwt_secret_key: str | None = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(7 * 24 * 60)))

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g.
    # "https://myapp.vercel.app,http://localhost:5173"
    allowed_origins: list[str] = _get_list("ALLOWED_ORIGINS", ["http://localhost:5173"])

    # --- Misc ---
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    environment: str = os.getenv("ENVIRONMENT", "development")

    def require_groq_api_key(self) -> str:
        if not self.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file "
                "(see .env.example) before making any LLM calls."
            )
        return self.groq_api_key

    def require_jwt_secret(self) -> str:
        if not self.jwt_secret_key:
            raise RuntimeError(
                "JWT_SECRET_KEY is not set. Add it to your .env file "
                "(see .env.example). Never rely on a hardcoded default "
                "secret in production."
            )
        return self.jwt_secret_key


settings = Settings()

for _dir in (settings.upload_dir, settings.chroma_dir, settings.papers_dir):
    _dir.mkdir(parents=True, exist_ok=True)
