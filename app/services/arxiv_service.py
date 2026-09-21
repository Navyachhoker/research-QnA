import uuid
from sqlalchemy.orm import Session

from app.rag.arxiv_client import search_arxiv, download_arxiv_pdf
from app.config import settings
from app.utils.pdf_utils import extract_text_by_page
from app.rag.ingest import chunk_text
from app.rag.vector_store import get_vector_store
from app.db.models import Paper


def search_papers(query: str, max_results: int = 5) -> list[dict]:
    return search_arxiv(query, max_results)


def import_paper_from_arxiv(arxiv_id: str, db: Session, owner_id: str) -> dict:
    paper_id = str(uuid.uuid4())[:8]

    settings.papers_dir.mkdir(parents=True, exist_ok=True)
    dest_path = settings.papers_dir / f"{paper_id}.pdf"
    download_arxiv_pdf(arxiv_id, dest_path)

    pages = extract_text_by_page(dest_path)
    chunks = chunk_text(pages, paper_id=paper_id)
    get_vector_store().add_chunks(chunks)

    search = search_arxiv(arxiv_id, max_results=1)
    filename = f"{search[0]['title']}.pdf" if search else f"{arxiv_id}.pdf"

    paper_record = Paper(
        paper_id=paper_id, owner_id=owner_id, filename=filename,
        num_pages=len(pages), num_chunks=len(chunks),
    )
    db.add(paper_record)
    db.commit()

    return {"paper_id": paper_id, "filename": filename, "num_pages": len(pages), "num_chunks": len(chunks)}