"""
Cross-encoder reranking: a second-pass relevance check over a small
candidate pool.

Why this is separate from (and more accurate than) the vector/BM25 first
pass: both of those score a query against a chunk by comparing two
independently-computed representations (an embedding, or a term-frequency
vector). A cross-encoder instead feeds the query and chunk into the model
*together*, so it can directly judge "does this chunk answer this
question" rather than "are these two things numerically similar". That's
more accurate, but too slow to run against an entire corpus — hence
running it only over the ~15-20 candidates the first pass already
narrowed down to, not the whole corpus.
"""

from typing import Protocol

from sentence_transformers import CrossEncoder


class Reranker(Protocol):
    def rerank(self, query: str, chunks: list[dict], top_k: int) -> list[dict]: ...


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self._model = CrossEncoder(model_name)

    def rerank(self, query: str, chunks: list[dict], top_k: int) -> list[dict]:
        if not chunks:
            return []

        pairs = [(query, c["text"]) for c in chunks]
        scores = self._model.predict(pairs)

        ranked = sorted(zip(chunks, scores, strict=True), key=lambda pair: pair[1], reverse=True)
        return [chunk for chunk, _score in ranked[:top_k]]


_reranker_instance: Reranker | None = None


def get_reranker() -> Reranker:
    """Shared instance for production/app use (loaded once, model weights
    cached). Tests do NOT use this — they construct a fake Reranker
    directly, since loading a real cross-encoder model is unnecessary
    network/compute overhead for a unit test."""
    global _reranker_instance
    if _reranker_instance is None:
        from app.config import settings  # deferred import avoids circulars

        _reranker_instance = CrossEncoderReranker(model_name=settings.reranker_model)
    return _reranker_instance
