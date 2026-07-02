import chromadb
from sentence_transformers import SentenceTransformer
from app.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
    )

embedder = SentenceTransformer(EMBEDDING_MODEL)

chroma = chromadb.PersistentClient(
    path= CHROMA_PATH
)

collection = chroma.get_or_create_collection(
    name = COLLECTION_NAME
)

def retrieve(
    query: str,
    top_k: int =TOP_K,
    paper: str | None=None,
)-> list[dict]:
    
    query_embedding = embedder.encode(
        [query]
    ).tolist()
    
    where_filter = (
        {"paper": paper}
        if paper
        else None
    )
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )
    
    retrieved_chunks = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):

        retrieved_chunks.append(
            {
                "text": document,
                "paper": metadata["paper"],
                "page": metadata["page"],
                "chunk_index": metadata["chunk_index"],
                "distance": round(distance, 4),
            }
        )

    return retrieved_chunks