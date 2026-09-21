import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Core values (kept from your original config) ---
GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
GROQ_MODEL       = "openai/gpt-oss-120b"
EMBEDDING_MODEL  = "paraphrase-MiniLM-L3-v2"  # 17MB — 5x smaller, good for low-memory machines
TEMPERATURE      = 0.2
MAX_TOKENS       = 1024
TOP_K            = 10
CHUNK_SIZE       = 500
CHUNK_OVERLAP    = 100

BASE_DIR         = Path(__file__).resolve().parent.parent

CHROMA_PATH      = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME  = "research_papers"
UPLOAD_DIR       = os.getenv("UPLOAD_DIR", "./uploads")
DATA_DIR         = os.getenv("DATA_DIR", "./data")
PAPERS_DIR       = os.path.join(DATA_DIR, "papers")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(PAPERS_DIR, exist_ok=True)

DATABASE_URL     = os.getenv("DATABASE_URL", "sqlite:///./researchgpt.db")

JWT_SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM    = "HS256"
JWT_EXPIRE_HOURS = 168  # 7 days

FRONTEND_URL     = os.getenv("FRONTEND_URL", "http://localhost:5173")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set. Check your .env file.")


# --- Compatibility layer ---
# Everything else in this project (services, db, rag modules) imports
# `settings` and reads attributes like settings.chunk_size, settings.chroma_dir, etc.
# Rather than rewrite every file, we expose one `settings` object here that maps
# your existing variables to those attribute names.
class Settings:
    groq_api_key = GROQ_API_KEY
    groq_model = GROQ_MODEL
    embedding_model = EMBEDDING_MODEL
    temperature = TEMPERATURE
    max_tokens = MAX_TOKENS
    top_k = TOP_K

    chunk_size = CHUNK_SIZE
    chunk_overlap = CHUNK_OVERLAP

    base_dir = BASE_DIR
    papers_dir = Path(PAPERS_DIR)
    chroma_dir = Path(CHROMA_PATH)
    upload_dir = Path(UPLOAD_DIR)
    data_dir = Path(DATA_DIR)

    database_url = DATABASE_URL

    jwt_secret_key = JWT_SECRET_KEY
    jwt_algorithm = JWT_ALGORITHM
    access_token_expire_minutes = JWT_EXPIRE_HOURS * 60

    frontend_url = FRONTEND_URL


settings = Settings()