from app.rag.generator import get_generator
from app.rag.vector_store import get_vector_store
from app.services.summarizer_service import summarize_paper


def generate_related_work_section(target_paper_id: str, owner_id: str, top_k: int = 8) -> dict:
    """Generate related work for one of the user's papers, drawn from
    their other ingested papers."""
    target_summary = summarize_paper(target_paper_id, owner_id=owner_id)

    excerpts = get_vector_store().search_excluding_paper(
        query=target_summary,
        owner_id=owner_id,
        exclude_paper_id=target_paper_id,
        top_k=top_k,
    )

    section_text = get_generator().generate_related_work(target_summary, excerpts)
    referenced_paper_ids = sorted({e["paper_id"] for e in excerpts})

    return {"related_work": section_text, "referenced_paper_ids": referenced_paper_ids}


def generate_related_work_by_topic(topic: str, owner_id: str, top_k: int = 8) -> dict:
    """Generate a related-work section for a free-text topic, drawn from
    everything the user has ingested (no target paper to exclude)."""
    excerpts = get_vector_store().search(query=topic, owner_id=owner_id, top_k=top_k)

    if not excerpts:
        return {
            "topic": topic,
            "related_work": "No relevant content found in your ingested papers.",
            "referenced_paper_ids": [],
        }

    section_text = get_generator().generate_related_work(topic, excerpts)
    referenced_paper_ids = sorted({e["paper_id"] for e in excerpts})

    return {"topic": topic, "related_work": section_text, "referenced_paper_ids": referenced_paper_ids}
