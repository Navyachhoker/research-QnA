import os
import fitz
import chromadb
from sentence_transformers import SentenceTransformer
from config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)
from utils.pdf_utils import (
    extract_text_from_pdf,
    chunk_text,
)

# ── Lazy singletons ────────────────────────────────────────────────────────────
# NOT loaded at import time — only when first request comes in
# This keeps startup memory under 512MB on Render free tier

_embedder = None
_chroma = None
_collection = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def get_collection():
    global _chroma, _collection
    if _collection is None:
        _chroma = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _chroma.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


# ── Functions ──────────────────────────────────────────────────────────────────

def ingest_pdf(pdf_path: str, paper_name: str) -> int:
    print("1. Starting ingestion")

    pages = extract_text_from_pdf(pdf_path)
    print("2. Text extracted")

    chunks = chunk_text(pages)
    print(f"3. Created {len(chunks)} chunks")

    texts = [chunk["text"] for chunk in chunks]
    print("4. Prepared text list")

    embeddings = []

    model = get_embedder()

    for i in range(0, len(texts), 8):
        batch = texts[i:i + 8]

        batch_embeddings = model.encode(
            batch,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        embeddings.extend(batch_embeddings.tolist())

        print(f"Processed batch {i // 8 + 1}")

    print("5. Embeddings generated")

    ids = [
        f"{paper_name}__p{chunk['page']}__c{chunk['chunk_index']}"
        for chunk in chunks
    ]
    print("6. IDs created")

    metadatas = [
        {
            "paper": paper_name,
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]
    print("7. Metadata created")

    get_collection().upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print("8. Stored in Chroma")

    return len(chunks)


def list_papers() -> list[str]:
    result = get_collection().get(include=["metadatas"])
    metadata = result["metadatas"]
    return sorted({item["paper"] for item in metadata})