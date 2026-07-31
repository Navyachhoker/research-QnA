# app/eval/list_collections.py
import chromadb
from app.config import CHROMA_PATH

client = chromadb.PersistentClient(path=CHROMA_PATH)  # same path you already have working
collections = client.list_collections()

for c in collections:
    print(c.name)