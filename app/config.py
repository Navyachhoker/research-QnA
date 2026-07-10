import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
GROQ_MODEL       = "llama-3.3-70b-versatile"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
TEMPERATURE      = 0.2
MAX_TOKENS       = 1024
TOP_K            = 5
CHUNK_SIZE       = 500
CHUNK_OVERLAP    = 100

# Use /data/ on Render (persistent disk), local paths in dev
CHROMA_PATH      = os.getenv("CHROMA_PATH",    "./chroma_db")
COLLECTION_NAME  = "research_papers"
UPLOAD_DIR       = os.getenv("UPLOAD_DIR",     "./uploads")
DATA_DIR         = os.getenv("DATA_DIR",        "./data")
PAPERS_DIR       = os.path.join(DATA_DIR, "papers")

os.makedirs(UPLOAD_DIR,  exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(PAPERS_DIR,  exist_ok=True)

# DB
DATABASE_URL     = os.getenv("DATABASE_URL", "sqlite:///./researchgpt.db")

# JWT
JWT_SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM    = "HS256"
JWT_EXPIRE_HOURS = 168    # 7 days