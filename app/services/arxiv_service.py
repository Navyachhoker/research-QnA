import tempfile
import uuid
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Paper
from app.rag.arxiv_client import ArxivError, download_arxiv_pdf, search_arxiv
from app.rag.ingest import chunk_text
from app.rag.vector_store import get_vector_store
from app.utils.pdf_utils import PDFExtractionError, extract_text_by_page


def search_arxiv_papers(query: str, max_results: int = 5) -> list[dict]:
    try:
        return search_arxiv(query, max_results=max_results)
    except ArxivError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def import_paper_from_arxiv(arxiv_id: str, db: Session, owner_id: str) -> dict:
    paper_id = str(uuid.uuid4())[:8]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_pdf = Path(tmp_dir) / f"{paper_id}.pdf"
        try:
            download_arxiv_pdf(arxiv_id, tmp_pdf)
            pages = extract_text_by_page(tmp_pdf)
        except ArxivError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except PDFExtractionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        chunks = chunk_text(pages, paper_id=paper_id, owner_id=owner_id)
        get_vector_store().add_chunks(chunks)

        from app.config import settings

        settings.papers_dir.mkdir(parents=True, exist_ok=True)
        final_path = settings.papers_dir / f"{paper_id}.pdf"
        final_path.write_bytes(tmp_pdf.read_bytes())

    paper_record = Paper(
        paper_id=paper_id,
        owner_id=owner_id,
        filename=f"arxiv_{arxiv_id}.pdf",
        num_pages=len(pages),
        num_chunks=len(chunks),
    )
    db.add(paper_record)
    db.commit()

    return {
        "paper_id": paper_id,
        "filename": paper_record.filename,
        "num_pages": len(pages),
        "num_chunks": len(chunks),
    }
