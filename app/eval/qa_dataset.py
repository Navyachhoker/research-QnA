"""
20-30 hand-written QA pairs from your actual PDFs.
Each entry needs: a question, the expected answer (rough, for judge reference),
and the ground-truth chunk id(s) that SHOULD be retrieved.

Why manual: you need ground truth to know if retrieval worked. Without knowing
"chunk_47 is the right chunk", you can't compute Recall@k or MRR at all —
you're just guessing whether an answer sounds right.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class QAItem:
    question: str
    expected_answer: str      # rough summary, used as reference for the judge
    relevant_chunk_ids: List[str]  # ground truth — which chunks SHOULD be retrieved

QA_DATASET: List[QAItem] = [
    QAItem(
        question="What is the maximum concurrent session limit for X?",
        expected_answer="The system supports up to 500 concurrent sessions per node.",
        relevant_chunk_ids=["doc3_chunk12", "doc3_chunk13"],
    ),
    # ... add 20-30 of these by hand, pulled from pages you know well
]