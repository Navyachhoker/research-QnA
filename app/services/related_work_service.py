from app.rag.vector_store import get_vector_store
from app.rag.generator import get_generator
from app.services.summarizer_service import summarize_paper


def generate_related_work_section(target_paper_id: str, top_k: int = 8) -> dict:
    target_summary = summarize_paper(target_paper_id)

    excerpts = get_vector_store().search_excluding_paper(
        query=target_summary,
        exclude_paper_id=target_paper_id,
        top_k=top_k,
    )

    section_text = get_generator().generate_related_work(target_summary, excerpts)
    referenced_paper_ids = sorted({e["paper_id"] for e in excerpts})

    return {"related_work": section_text, "referenced_paper_ids": referenced_paper_ids}