"""
Standard IR metrics. No API calls here — deterministic and fast, so you can
run this on every commit without burning Groq quota.
"""

from typing import List

def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Of all the chunks that SHOULD have been retrieved, what fraction actually
    showed up in your top-k results?
    """
    if not relevant_ids:
        return 0.0
    top_k = set(retrieved_ids[:k])
    relevant = set(relevant_ids)
    hits = len(top_k & relevant)
    return hits / len(relevant)

def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """
    Mean Reciprocal Rank: how high up was the FIRST relevant chunk?
    1.0 = it was rank 1. 0.5 = it was rank 2. 0 = never found.
    This matters because even if recall is fine, users care whether the
    right answer showed up first, not buried at position 8.
    """
    relevant = set(relevant_ids)
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0