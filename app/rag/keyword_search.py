"""
Keyword search (BM25) and fusion with dense vector search results.

Why this exists: dense embeddings are good at matching *meaning* but
regularly miss exact terms — model names, acronyms, specific numbers —
because two texts using the same rare token don't necessarily end up
close together in embedding space. BM25 is the opposite: it's a
term-frequency statistic, so it's excellent at exact-term matches and
weak at paraphrases. Combining both (hybrid search) covers more cases
than either alone.

This computes BM25 fresh per query over the owner's (optionally
paper-scoped) chunk corpus rather than maintaining a separate persistent
index. That's the right tradeoff for a single-user-at-a-time research
corpus (hundreds to a few thousand chunks) — simple, always consistent
with what's actually in the vector store, no second index to keep in
sync. It would need a real persistent inverted index to scale to a much
larger, shared corpus.
"""

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def bm25_search(query: str, corpus: list[dict], top_k: int) -> list[dict]:
    """Rank corpus chunks by BM25 score against the query. corpus is a
    list of chunk dicts (as returned by VectorStore.get_all_chunks) each
    with a "text" key. Chunks with zero term overlap are dropped rather
    than padding out low-quality results."""
    if not corpus:
        return []

    tokenized_corpus = [_tokenize(c["text"]) for c in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(_tokenize(query))

    ranked = sorted(zip(corpus, scores, strict=True), key=lambda pair: pair[1], reverse=True)
    return [chunk for chunk, score in ranked[:top_k] if score > 0]


def reciprocal_rank_fusion(rankings: list[list[dict]], key: str = "chunk_id", k: int = 60) -> list[dict]:
    """Merge multiple ranked lists (e.g. vector search + BM25) into one,
    using Reciprocal Rank Fusion: each item's fused score is the sum of
    1/(k + rank) across every ranking it appears in. A chunk that shows up
    high in both rankings outranks one that's only in one — this is a
    standard, parameter-light way to combine differently-scaled ranking
    signals without having to normalize and weight raw scores by hand.
    """
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranking in rankings:
        for rank, item in enumerate(ranking):
            item_id = item[key]
            items[item_id] = item
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)

    fused_ids = sorted(scores, key=lambda item_id: scores[item_id], reverse=True)
    return [items[item_id] for item_id in fused_ids]
