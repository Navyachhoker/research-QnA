#Handles semantic retrieval from ChromaDB
#Convert the user's question into an embedding

from config import TOP_K

from rag.embeddings import embedder
from rag.vector_store import (
    query_chunks,
    get_all_papers,
)


def retrieve(
    query: str,
    top_k: int = TOP_K,
    paper_filter: str | None = None,
) -> list[dict]:

    #Retrieve the most relevant chunks for a query
   
    #Convert the question into an embedding
    query_embedding = embedder.encode(
        [query]
    ).tolist()

    #filter
    where = (
        {"paper": paper_filter}
        if paper_filter
        else None
    )

    results = query_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
        where=where,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    #will store formatted results
    retrieved = []

    for doc, meta, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        retrieved.append(
            {
                "text": doc,
                "paper": meta["paper"],
                "page": meta["page"],
                "chunk_index": meta["chunk_index"],
                "distance": round(distance, 4),
            }
        )

    print(
        f"[Retriever] Retrieved {len(retrieved)} chunks."
    )

    return retrieved


def list_ingested_papers():
    """
    Return all papers stored in ChromaDB.
    """

    return get_all_papers()