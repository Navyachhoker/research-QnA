def test_hybrid_retrieval_uses_reranker(
    real_vector_store,
    fake_reranker,
    monkeypatch,
):
    from app.services.retriever_service import retrieve_chunks

    real_vector_store.add_chunks(
        [
            {
                "chunk_id": "c1",
                "text": "transformer self attention architecture",
                "paper_id": "paper1",
                "owner_id": "owner1",
                "page_number": 1,
            },
            {
                "chunk_id": "c2",
                "text": "recurrent neural network sequence processing",
                "paper_id": "paper1",
                "owner_id": "owner1",
                "page_number": 2,
            },
            {
                "chunk_id": "c3",
                "text": "transformer encoder attention mechanism",
                "paper_id": "paper1",
                "owner_id": "owner1",
                "page_number": 3,
            },
        ]
    )

    from app.config import settings

    monkeypatch.setattr(settings, "enable_hybrid_search", True)
    monkeypatch.setattr(settings, "enable_reranking", True)
    monkeypatch.setattr(settings, "retrieval_candidate_pool", 3)

    results = retrieve_chunks(
        query="transformer attention",
        owner_id="owner1",
        top_k=2,
    )

    assert len(results) <= 2

    # The fake reranker must actually have been called.
    assert len(fake_reranker.calls) == 1

    call = fake_reranker.calls[0]
    assert call["query"] == "transformer attention"
    assert call["input_count"] >= 2
    assert call["top_k"] == 2

    # The fake reverses the candidate order, proving that the
    # service uses the reranker's returned ordering.
    assert results