"""
Orchestrator — wires the QA dataset, retrieval metrics, and LLM judge
against the actual RAG pipeline (app/services/retriever_service.py +
app/services/generator_service.py).

Setup: this evaluates retrieval/generation quality against papers already
ingested for a specific account. Register a user, log in, and upload the
BERT and "Attention Is All You Need" papers (the ones qa_dataset.py's
ground truth was written against) through the normal API first, then set
EVAL_OWNER_ID below to that user's user_id (see GET /auth/me).

Run with: python -m app.eval.run_eval
"""

import csv
import os
from datetime import datetime

from groq import RateLimitError

from app.db.database import SessionLocal
from app.db.models import Paper
from app.eval.llm_judge import judge_answer
from app.eval.qa_dataset import QA_DATASET
from app.eval.retrieval_metrics import mrr, recall_at_k
from app.services.generator_service import answer_query
from app.services.retriever_service import retrieve_chunks

EVAL_OWNER_ID = os.environ.get("EVAL_OWNER_ID", "")


def _page_key(filename_stem: str, page_number: int) -> str:
    return f"{filename_stem}__p{page_number}"


def _normalize_expected_id(old_style_id: str) -> str:
    """Old ground-truth ids look like 'name__p6__c4'. Drop the chunk-index
    suffix so we compare at page granularity."""
    parts = old_style_id.split("__")
    return "__".join(parts[:2]) if len(parts) >= 2 else old_style_id


def run_evaluation(k: int = 5):
    if not EVAL_OWNER_ID:
        raise SystemExit(
            "Set EVAL_OWNER_ID (env var) to the user_id whose account has the "
            "eval papers uploaded. See GET /auth/me after logging in."
        )

    db = SessionLocal()
    filename_by_paper_id = {
        p.paper_id: p.filename.rsplit(".", 1)[0]
        for p in db.query(Paper).filter(Paper.owner_id == EVAL_OWNER_ID)
    }
    db.close()

    results = []
    stopped_early = False

    for item in QA_DATASET:
        expected_ids = [_normalize_expected_id(cid) for cid in item.relevant_chunk_ids]

        try:
            retrieved_chunks = retrieve_chunks(item.question, owner_id=EVAL_OWNER_ID, top_k=k)
            retrieved_ids = [
                _page_key(filename_by_paper_id.get(c["paper_id"], c["paper_id"]), c["page_number"])
                for c in retrieved_chunks
            ]

            r_at_k = recall_at_k(retrieved_ids, expected_ids, k)
            r_mrr = mrr(retrieved_ids, expected_ids)

            gen_result = answer_query(item.question, retrieved_chunks)
            answer = gen_result["answer"]

            context_text = "\n\n".join(c["text"] for c in retrieved_chunks)
            judgment = judge_answer(item.question, context_text, answer)
        except RateLimitError as exc:
            # A free/dev-tier daily token quota running out mid-run is
            # expected, not a bug — this eval makes 2 LLM calls per
            # question. Stop cleanly and still save/report whatever we
            # collected so far, rather than losing the whole run.
            print(f"\n⚠ Hit a Groq rate limit after {len(results)}/{len(QA_DATASET)} questions: {exc}")
            print("Stopping early and saving partial results. Re-run later to pick up more coverage.")
            stopped_early = True
            break
        except Exception as exc:  # noqa: BLE001 - one bad question shouldn't sink the whole run
            print(f"\n⚠ Skipping question due to an error: {item.question[:60]}...  ({exc})")
            continue

        results.append(
            {
                "question": item.question,
                "recall_at_k": r_at_k,
                "mrr": r_mrr,
                "faithfulness": judgment["faithfulness"],
                "relevance": judgment["relevance"],
                "reasoning": judgment.get("reasoning", ""),
                "generated_answer": answer,
                "retrieved_ids": retrieved_ids,
                "expected_ids": expected_ids,
            }
        )

        print(
            f"✓ {item.question[:60]}...  R@{k}={r_at_k:.2f}  MRR={r_mrr:.2f}  "
            f"Faith={judgment['faithfulness']}/5  Rel={judgment['relevance']}/5"
        )

    if not results:
        print("No questions completed — nothing to report or save.")
        return results

    n = len(results)
    avg_recall = sum(r["recall_at_k"] for r in results) / n
    avg_mrr = sum(r["mrr"] for r in results) / n
    avg_faith = sum(r["faithfulness"] for r in results) / n
    avg_rel = sum(r["relevance"] for r in results) / n

    print("\n" + "=" * 50)
    if stopped_early:
        print(f"(Partial results: {n}/{len(QA_DATASET)} questions completed)")
    print(f"Avg Recall@{k}:      {avg_recall:.2f}")
    print(f"Avg MRR:             {avg_mrr:.2f}")
    print(f"Avg Faithfulness:    {avg_faith:.2f}/5")
    print(f"Avg Relevance:       {avg_rel:.2f}/5")
    print("=" * 50)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, f"eval_{timestamp}.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved detailed results to {out_path}")
    return results


if __name__ == "__main__":
    run_evaluation(k=5)
