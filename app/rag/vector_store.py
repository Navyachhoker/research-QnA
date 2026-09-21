import chromadb
from typing import List, Dict, Optional
from app.rag.embeddings import EmbeddingModel, get_embedding_model


class VectorStore:
    """
    Wraps ChromaDB. Takes its embedding model as a dependency (constructor
    injection) rather than importing a global — this is what makes it
    possible to swap in a fake embedding model during tests.
    """

    def __init__(self, persist_dir: str, embedding_model: EmbeddingModel, collection_name: str = "research_papers"):
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(name=collection_name)
        self._embedding_model = embedding_model

    def add_chunks(self, chunks: List[Dict]) -> None:
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        embeddings = self._embedding_model.embed_texts(texts)

        self._collection.add(
            ids=[c["chunk_id"] for c in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {"paper_id": c["paper_id"], "page_number": c["page_number"]}
                for c in chunks
            ],
        )

    def search(self, query: str, top_k: int = 5, paper_id: Optional[str] = None) -> List[Dict]:
        query_embedding = self._embedding_model.embed_query(query)
        where_filter = {"paper_id": paper_id} if paper_id else None

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
        )
        return self._format_results(results)

    def search_excluding_paper(self, query: str, exclude_paper_id: str, top_k: int = 8) -> List[Dict]:
        query_embedding = self._embedding_model.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"paper_id": {"$ne": exclude_paper_id}},
        )
        return self._format_results(results)

    def get_all_chunks_for_paper(self, paper_id: str) -> List[Dict]:
        results = self._collection.get(
            where={"paper_id": paper_id},
            include=["documents", "metadatas"],
        )

        chunks = [
            {
                "chunk_id": results["ids"][i],
                "text": results["documents"][i],
                "page_number": results["metadatas"][i]["page_number"],
            }
            for i in range(len(results["ids"]))
        ]
        chunks.sort(key=lambda c: c["page_number"])
        return chunks

    def delete_paper_chunks(self, paper_id: str) -> None:
        self._collection.delete(where={"paper_id": paper_id})

    @staticmethod
    def _format_results(results: dict) -> List[Dict]:
        if not results["ids"] or not results["ids"][0]:
            return []

        matches = []
        for i in range(len(results["ids"][0])):
            matches.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "paper_id": results["metadatas"][0][i]["paper_id"],
                "page_number": results["metadatas"][0][i]["page_number"],
                "distance": results["distances"][0][i],
            })
        return matches


_vector_store_instance: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Shared instance for production/app use. Tests do NOT use this —
    they construct a VectorStore directly with a fake embedding model
    and a temp directory.
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        from app.config import settings  # deferred import avoids circulars
        _vector_store_instance = VectorStore(
            persist_dir=str(settings.chroma_dir),
            embedding_model=get_embedding_model(),
        )
    return _vector_store_instance