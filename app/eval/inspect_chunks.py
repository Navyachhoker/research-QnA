# app/eval/inspect_chunks.py — throwaway script, not part of the eval pipeline
import chromadb
from app.config import CHROMA_PATH  # match whatever import worked in list_collections.py

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("research_papers")

results = collection.get(include=["documents", "metadatas"])

for id_, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
    print(f"ID: {id_}")
    print(f"Source: {meta.get('source', 'unknown')}")
    print(f"Text: {doc[:150]}...")
    print("-" * 60)