from app.services.summarizer_service import summarize_paper
from app.rag.generator import get_generator


def compare_papers(paper_id_a: str, paper_id_b: str) -> str:
    summary_a = summarize_paper(paper_id_a)
    summary_b = summarize_paper(paper_id_b)
    return get_generator().generate_comparison(paper_id_a, summary_a, paper_id_b, summary_b)