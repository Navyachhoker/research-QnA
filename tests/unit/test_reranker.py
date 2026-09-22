from app.rag.reranker import CrossEncoderReranker


class _FakeCrossEncoderModel:
    """Stands in for sentence_transformers.CrossEncoder: scores each
    (query, text) pair by how many query words appear in the text, so
    tests can assert on a deterministic, meaningful ranking without
    loading a real model."""

    def predict(self, pairs):
        scores = []
        for query, text in pairs:
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            scores.append(len(query_words & text_words))
        return scores


def _make_reranker() -> CrossEncoderReranker:
    # Bypass __init__ (which loads a real model) and inject the fake directly.
    reranker = CrossEncoderReranker.__new__(CrossEncoderReranker)
    reranker._model = _FakeCrossEncoderModel()
    return reranker


def test_rerank_orders_by_relevance_score():
    reranker = _make_reranker()
    chunks = [
        {"chunk_id": "c1", "text": "completely irrelevant gardening content"},
        {"chunk_id": "c2", "text": "transformer architecture self attention"},
        {"chunk_id": "c3", "text": "some transformer mention only"},
    ]

    result = reranker.rerank("transformer architecture attention", chunks, top_k=3)

    assert [c["chunk_id"] for c in result][:2] == ["c2", "c3"]


def test_rerank_respects_top_k():
    reranker = _make_reranker()
    chunks = [{"chunk_id": f"c{i}", "text": "transformer"} for i in range(10)]

    result = reranker.rerank("transformer", chunks, top_k=3)

    assert len(result) == 3


def test_rerank_empty_chunks_returns_empty():
    reranker = _make_reranker()
    assert reranker.rerank("query", [], top_k=5) == []


def test_rerank_preserves_chunk_dict_contents():
    reranker = _make_reranker()
    chunks = [{"chunk_id": "c1", "text": "transformer", "page_number": 7, "paper_id": "p1"}]

    result = reranker.rerank("transformer", chunks, top_k=1)

    assert result[0] == chunks[0]
