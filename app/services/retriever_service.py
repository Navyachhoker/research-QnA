from app.config import settings
from app.rag.keyword_search import bm25_search, reciprocal_rank_fusion
from app.rag.reranker import get_reranker
from app.rag.vector_store import get_vector_store


def retrieve_chunks(
    query: str,
    owner_id: str,
    top_k: int = 5,
    paper_id: str | None = None,
) -> list[dict]:
    """
    Retrieval pipeline:

        vector search ─┐
                       ├─> RRF -> candidate pool -> reranker -> final top_k
        BM25 search ───┘

    Hybrid search and reranking can independently be disabled through
    settings.
    """
    store = get_vector_store()

    candidate_pool = max(settings.retrieval_candidate_pool, top_k)

    vector_hits = store.search(
        query=query,
        owner_id=owner_id,
        top_k=candidate_pool,
        paper_id=paper_id,
        max_distance=settings.max_retrieval_distance,
    )

    if settings.enable_hybrid_search:
        corpus = store.get_all_chunks(
            owner_id=owner_id,
            paper_id=paper_id,
        )

        keyword_hits = bm25_search(
            query,
            corpus,
            top_k=candidate_pool,
        )

        candidates = reciprocal_rank_fusion(
            [vector_hits, keyword_hits]
        )

    else:
        candidates = vector_hits[:candidate_pool]

    if not candidates:
        return []

    if settings.enable_reranking:
        return get_reranker().rerank(
            query,
            candidates,
            top_k=top_k,
        )

    return candidates[:top_k]