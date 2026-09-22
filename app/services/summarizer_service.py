from app.rag.generator import get_generator
from app.rag.vector_store import get_vector_store


def summarize_paper(paper_id: str, owner_id: str) -> str:
    chunks = get_vector_store().get_all_chunks_for_paper(paper_id, owner_id=owner_id)
    return get_generator().generate_summary(chunks)
