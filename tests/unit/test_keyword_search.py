from app.rag.keyword_search import bm25_search, reciprocal_rank_fusion


def _chunk(chunk_id, text):
    return {"chunk_id": chunk_id, "text": text, "paper_id": "p1", "page_number": 1}


def test_bm25_search_ranks_exact_term_matches_first():
    corpus = [
        _chunk("c1", "The transformer architecture uses self-attention mechanisms."),
        _chunk("c2", "Recurrent neural networks process sequences step by step."),
        _chunk("c3", "BERT is a bidirectional transformer encoder model."),
    ]

    results = bm25_search("transformer architecture", corpus, top_k=3)

    assert results
    assert results[0]["chunk_id"] in {"c1", "c3"}  # both mention "transformer"


def test_bm25_search_drops_zero_score_matches():
    corpus = [
        _chunk("c1", "Completely unrelated content about gardening and plants."),
    ]

    results = bm25_search("quantum computing algorithms", corpus, top_k=5)

    assert results == []


def test_bm25_search_empty_corpus_returns_empty():
    assert bm25_search("anything", [], top_k=5) == []


def test_bm25_search_respects_top_k():
    corpus = [_chunk(f"c{i}", f"machine learning topic number {i}") for i in range(10)]
    results = bm25_search("machine learning", corpus, top_k=3)
    assert len(results) <= 3


def test_reciprocal_rank_fusion_favors_items_ranked_high_in_both_lists():
    ranking_a = [_chunk("c1", "a"), _chunk("c2", "b"), _chunk("c3", "c")]
    ranking_b = [_chunk("c2", "b"), _chunk("c3", "c"), _chunk("c1", "a")]

    fused = reciprocal_rank_fusion([ranking_a, ranking_b])

    fused_ids = [c["chunk_id"] for c in fused]
    assert set(fused_ids) == {"c1", "c2", "c3"}
    # c2 is top-2 in both lists (rank 1 in a, rank 0 in b) so should score highest
    assert fused_ids[0] == "c2"


def test_reciprocal_rank_fusion_includes_items_only_in_one_list():
    ranking_a = [_chunk("c1", "a")]
    ranking_b = [_chunk("c2", "b")]

    fused = reciprocal_rank_fusion([ranking_a, ranking_b])

    assert {c["chunk_id"] for c in fused} == {"c1", "c2"}


def test_reciprocal_rank_fusion_empty_rankings_returns_empty():
    assert reciprocal_rank_fusion([[], []]) == []


def test_reciprocal_rank_fusion_deduplicates_shared_items():
    shared = _chunk("c1", "shared chunk")
    fused = reciprocal_rank_fusion([[shared], [shared]])
    assert len(fused) == 1
