from app.rag.generator import get_generator
from app.services.summarizer_service import summarize_paper


def compare_papers(paper_id_a: str, paper_id_b: str, owner_id: str) -> str:
    summary_a = summarize_paper(paper_id_a, owner_id=owner_id)
    summary_b = summarize_paper(paper_id_b, owner_id=owner_id)
    return get_generator().generate_comparison(paper_id_a, summary_a, paper_id_b, summary_b)
