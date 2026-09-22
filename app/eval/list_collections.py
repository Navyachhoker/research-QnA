# app/eval/list_collections.py — dev utility, not part of the API.
# Run with: python -m app.eval.list_collections
import chromadb

from app.config import settings

client = chromadb.PersistentClient(path=str(settings.chroma_dir))
collections = client.list_collections()

for c in collections:
    print(c.name)
