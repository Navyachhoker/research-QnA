import chromadb
from sentence_transformers import SentenceTransformer
from config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)

# ── Lazy singletons ────────────────────────────────────────────────────────────

_embedder   = None
_chroma     = None
_collection = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def get_collection():
    global _chroma, _collection
    if _collection is None:
        _chroma     = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _chroma.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


# ── Functions ──────────────────────────────────────────────────────────────────

def retrieve(
    query:   str,
    top_k:   int        = TOP_K,
    paper:   str | None = None,
    user_id: int         = None,
) -> list[dict]:

    query_embedding = get_embedder().encode([query]).tolist()

    if paper:
        where_filter = {"$and": [{"user_id": user_id}, {"paper": paper}]}
    else:
        where_filter = {"user_id": user_id}

    results = get_collection().query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []
    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved_chunks.append({
            "text":        document,
            "paper":       metadata["paper"],
            "page":        metadata["page"],
            "chunk_index": metadata["chunk_index"],
            "distance":    round(distance, 4),
        })

    return retrieved_chunks