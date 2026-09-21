import uuid
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.utils.pdf_utils import extract_text_by_page
from app.rag.ingest import chunk_text
from app.rag.vector_store import get_vector_store
from app.db.models import Paper


def save_uploaded_file(file: UploadFile, paper_id: str) -> Path:
    settings.papers_dir.mkdir(parents=True, exist_ok=True)
    dest_path = settings.papers_dir / f"{paper_id}.pdf"
    with open(dest_path, "wb") as f:
        f.write(file.file.read())
    return dest_path


def ingest_paper(file: UploadFile, db: Session, owner_id: str) -> dict:
    paper_id = str(uuid.uuid4())[:8]
    pdf_path = save_uploaded_file(file, paper_id)

    pages = extract_text_by_page(pdf_path)
    chunks = chunk_text(pages, paper_id=paper_id)
    get_vector_store().add_chunks(chunks)

    paper_record = Paper(
        paper_id=paper_id,
        owner_id=owner_id,
        filename=file.filename,
        num_pages=len(pages),
        num_chunks=len(chunks),
    )
    db.add(paper_record)
    db.commit()

    return {
        "paper_id": paper_id,
        "filename": file.filename,
        "num_pages": len(pages),
        "num_chunks": len(chunks),
    }