from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

print(f"[Embeddings] Loading model: {EMBEDDING_MODEL}")

embedder = SentenceTransformer(EMBEDDING_MODEL)

print("[Embeddings] model loaded successfully")