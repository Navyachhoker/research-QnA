"""
Orchestrator — wires the QA dataset, retrieval metrics, and LLM judge
against your actual RAG pipeline (app/services/retriever_service.py + app/services/generator_service.py).
"""

import json
import csv
from datetime import datetime
import sys
import os

# Add repo root AND app/ folder to path:
# - repo root so "app.eval.qa_dataset" etc. resolve
# - app/ folder so bare "from config import ..." (used inside
#   retriever_service.py, generator_service.py) resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

# Override the SAME "config" module that retriever_service.py /
# generator_service.py import via "from config import ...".
# Must be plain "import config" (not "app.config") — otherwise it's a
# different module object and the override silently does nothing.
import config
config.CHROMA_PATH = "chroma_db_test"
config.EMBEDDING_MODEL = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"

from app.eval.qa_dataset import QA_DATASET
from app.eval.retrieval_metrics import recall_at_k, mrr
from app.eval.llm_judge import judge_answer
from app.services.retriever_service import retrieve
from app.services.generator_service import generate


def chunk_dict_to_id(chunk: dict) -> str:
    """
    Reconstructs the chunk_id string from retrieve()'s metadata output,
    since retrieve() returns paper/page/chunk_index separately rather
    than a single id string. This must match the format used when your
    chunks were originally stored (paper__pPAGE__cINDEX).
    """
    return f"{chunk['paper']}__p{chunk['page']}__c{chunk['chunk_index']}"


def run_evaluation(k: int = 5):
    results = []

    for item in QA_DATASET:
        # 1. Retrieve
        retrieved_chunks = retrieve(item.question, top_k=k)
        retrieved_ids = [chunk_dict_to_id(c) for c in retrieved_chunks]
        print("EXPECTED:", item.relevant_chunk_ids)
        print("GOT:     ", retrieved_ids)
        print("-" * 40)

        r_at_k = recall_at_k(retrieved_ids, item.relevant_chunk_ids, k)
        r_mrr = mrr(retrieved_ids, item.relevant_chunk_ids)

        # 2. Generate
        gen_result = generate(item.question, retrieved_chunks)
        answer = gen_result["answer"]

        # 3. Judge
        context_text = "\n\n".join(c["text"] for c in retrieved_chunks)
        judgment = judge_answer(item.question, context_text, answer)

        results.append({
            "question": item.question,
            "recall_at_k": r_at_k,
            "mrr": r_mrr,
            "faithfulness": judgment["faithfulness"],
            "relevance": judgment["relevance"],
            "reasoning": judgment.get("reasoning", ""),
            "generated_answer": answer,
            "retrieved_ids": retrieved_ids,
            "expected_ids": item.relevant_chunk_ids,
        })

        # live progress so you can see it working, not just wait blindly
        print(f"✓ {item.question[:60]}...  R@{k}={r_at_k:.2f}  MRR={r_mrr:.2f}  "
              f"Faith={judgment['faithfulness']}/5  Rel={judgment['relevance']}/5")

    # ---- aggregate ----
    n = len(results)
    avg_recall = sum(r["recall_at_k"] for r in results) / n
    avg_mrr = sum(r["mrr"] for r in results) / n
    avg_faith = sum(r["faithfulness"] for r in results) / n
    avg_rel = sum(r["relevance"] for r in results) / n

    print("\n" + "=" * 50)
    print(f"Avg Recall@{k}:      {avg_recall:.2f}")
    print(f"Avg MRR:             {avg_mrr:.2f}")
    print(f"Avg Faithfulness:    {avg_faith:.2f}/5")
    print(f"Avg Relevance:       {avg_rel:.2f}/5")
    print("=" * 50)

    # ---- save results for tracking over time ----
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"app/eval/results/eval_{timestamp}.csv"

    os.makedirs("app/eval/results", exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved detailed results to {out_path}")

    return results


if __name__ == "__main__":
    run_evaluation(k=5)