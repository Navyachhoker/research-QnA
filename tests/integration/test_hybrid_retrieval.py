from unittest.mock import patch

from app.config import settings
from app.services.retriever_service import retrieve_chunks


def _add_sample_chunks(store):
    store.add_chunks(
        [
            {
                "chunk_id": "c1",
                "paper_id": "p1",
                "owner_id": "owner-1",
                "page_number": 1,
                "text": "The Transformer architecture relies entirely on attention mechanisms.",
            },
            {
                "chunk_id": "c2",
                "paper_id": "p1",
                "owner_id": "owner-1",
                "page_number": 2,
                "text": "BERT achieves state of the art results on eleven NLP tasks.",
            },
            {
                "chunk_id": "c3",
                "paper_id": "p1",
                "owner_id": "owner-1",
                "page_number": 3,
                "text": "Recurrent neural networks process sequences one step at a time.",
            },
        ]
    )


def test_retrieve_chunks_with_hybrid_and_reranking_enabled(real_vector_store, fake_reranker):
    _add_sample_chunks(real_vector_store)

    with (
        patch.object(settings, "enable_hybrid_search", True),
        patch.object(settings, "enable_reranking", True),
    ):
        results = retrieve_chunks("attention mechanisms transformer", owner_id="owner-1", top_k=2)

    assert len(results) <= 2
    assert all(r["chunk_id"] in {"c1", "c2", "c3"} for r in results)


def test_retrieve_chunks_with_hybrid_disabled_falls_back_to_vector_only(real_vector_store, fake_reranker):
    _add_sample_chunks(real_vector_store)

    with (
        patch.object(settings, "enable_hybrid_search", False),
        patch.object(settings, "enable_reranking", False),
    ):
        results = retrieve_chunks("attention mechanisms", owner_id="owner-1", top_k=2)

    assert len(results) <= 2


def test_retrieve_chunks_respects_owner_scoping_through_hybrid_pipeline(real_vector_store, fake_reranker):
    real_vector_store.add_chunks(
        [
            {
                "chunk_id": "a1",
                "paper_id": "p1",
                "owner_id": "owner-a",
                "page_number": 1,
                "text": "owner a private research content",
            },
            {
                "chunk_id": "b1",
                "paper_id": "p1",
                "owner_id": "owner-b",
                "page_number": 1,
                "text": "owner b private research content",
            },
        ]
    )

    with (
        patch.object(settings, "enable_hybrid_search", True),
        patch.object(settings, "enable_reranking", True),
    ):
        results = retrieve_chunks("private research content", owner_id="owner-a", top_k=10)

    assert all(r["chunk_id"] == "a1" for r in results)


def test_retrieve_chunks_returns_empty_when_no_chunks_match(real_vector_store, fake_reranker):
    with (
        patch.object(settings, "enable_hybrid_search", True),
        patch.object(settings, "enable_reranking", True),
    ):
        results = retrieve_chunks("anything at all", owner_id="owner-with-no-papers", top_k=5)

    assert results == []
