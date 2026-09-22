# app/eval/inspect_chunks.py — throwaway inspection script, not part of the API.
# Run with: python -m app.eval.inspect_chunks
import chromadb

from app.config import settings

client = chromadb.PersistentClient(path=str(settings.chroma_dir))
collection = client.get_collection("research_papers")

results = collection.get(include=["documents", "metadatas"])

for id_, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
    print(f"ID: {id_}")
    print(
        f"Paper: {meta.get('paper_id', 'unknown')}  Owner: {meta.get('owner_id', 'unknown')}  Page: {meta.get('page_number', '?')}"
    )
    print(f"Text: {doc[:150]}...")
    print("-" * 60)
