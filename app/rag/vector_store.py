import chromadb

from app.rag.embeddings import EmbeddingModel, get_embedding_model


class VectorStore:
    """
    Wraps ChromaDB. Takes its embedding model as a dependency (constructor
    injection) rather than importing a global — this is what makes it
    possible to swap in a fake embedding model during tests.

    SECURITY: every chunk is stored with an `owner_id`, and every read
    method (search / get_all_chunks_for_paper / delete_paper_chunks) takes
    owner_id and filters on it. There is a single shared Chroma collection
    across all users, so this filter is the only thing standing between
    one user's questions and another user's private papers — never call
    the underlying methods without it.
    """

    def __init__(
        self, persist_dir: str, embedding_model: EmbeddingModel, collection_name: str = "research_papers"
    ):
        self._client = chromadb.PersistentClient(path=persist_dir)
        # Chroma's default distance space is L2 (unbounded), not cosine.
        # We rely on a bounded, well-understood distance range for
        # max_retrieval_distance filtering, so pin the space explicitly
        # rather than relying on an undocumented default.
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._embedding_model = embedding_model

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        embeddings = self._embedding_model.embed_texts(texts)

        self._collection.add(
            ids=[c["chunk_id"] for c in chunks],
            embeddings=embeddings,  # type: ignore[arg-type]
            documents=texts,
            metadatas=[
                {
                    "paper_id": c["paper_id"],
                    "owner_id": c["owner_id"],
                    "page_number": c["page_number"],
                }
                for c in chunks
            ],
        )

    def search(
        self,
        query: str,
        owner_id: str,
        top_k: int = 5,
        paper_id: str | None = None,
        max_distance: float | None = None,
    ) -> list[dict]:
        query_embedding = self._embedding_model.embed_query(query)

        conditions: list[dict] = [{"owner_id": owner_id}]
        if paper_id:
            conditions.append({"paper_id": paper_id})
        where_filter = conditions[0] if len(conditions) == 1 else {"$and": conditions}

        results = self._collection.query(
            query_embeddings=[query_embedding],  # type: ignore[arg-type]
            n_results=top_k,
            where=where_filter,
        )
        matches = self._format_results(dict(results))

        if max_distance is not None:
            matches = [m for m in matches if m["distance"] <= max_distance]

        return matches

    def search_excluding_paper(
        self, query: str, owner_id: str, exclude_paper_id: str, top_k: int = 8
    ) -> list[dict]:
        query_embedding = self._embedding_model.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],  # type: ignore[arg-type]
            n_results=top_k,
            where={"$and": [{"owner_id": owner_id}, {"paper_id": {"$ne": exclude_paper_id}}]},  # type: ignore[dict-item]
        )
        return self._format_results(dict(results))

    def get_all_chunks(self, owner_id: str, paper_id: str | None = None) -> list[dict]:
        """Fetch every chunk in scope (all of the owner's papers, or one
        specific paper) without a similarity query. Used to build the BM25
        keyword-search corpus for hybrid retrieval, and by
        get_all_chunks_for_paper below."""
        conditions: list[dict] = [{"owner_id": owner_id}]
        if paper_id:
            conditions.append({"paper_id": paper_id})
        where_filter = conditions[0] if len(conditions) == 1 else {"$and": conditions}

        results = self._collection.get(where=where_filter, include=["documents", "metadatas"])

        ids = results["ids"]
        documents = results["documents"] or []
        metadatas = results["metadatas"] or []

        return [
            {
                "chunk_id": ids[i],
                "text": documents[i],
                "paper_id": metadatas[i]["paper_id"],
                "page_number": metadatas[i]["page_number"],
            }
            for i in range(len(ids))
        ]

    def get_all_chunks_for_paper(self, paper_id: str, owner_id: str) -> list[dict]:
        chunks = self.get_all_chunks(owner_id=owner_id, paper_id=paper_id)
        chunks.sort(key=lambda c: int(c["page_number"]))
        return chunks

    def delete_paper_chunks(self, paper_id: str, owner_id: str) -> None:
        self._collection.delete(where={"$and": [{"owner_id": owner_id}, {"paper_id": paper_id}]})

    @staticmethod
    def _format_results(results: dict) -> list[dict]:
        if not results["ids"] or not results["ids"][0]:
            return []

        matches = []
        for i in range(len(results["ids"][0])):
            matches.append(
                {
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "paper_id": results["metadatas"][0][i]["paper_id"],
                    "page_number": results["metadatas"][0][i]["page_number"],
                    "distance": results["distances"][0][i],
                }
            )
        return matches


_vector_store_instance: VectorStore | None = None


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
