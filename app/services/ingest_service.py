import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Paper
from app.rag.ingest import chunk_text
from app.rag.vector_store import get_vector_store
from app.utils.pdf_utils import PDFExtractionError, extract_text_by_page

MAX_UPLOAD_BYTES = settings.max_upload_mb * 1024 * 1024


def _validate_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Trust the declared content-type as a first filter (still validated by
    # actually parsing the file with PyMuPDF below — this just rejects
    # obviously-wrong uploads early with a clear message).
    if file.content_type and file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")


def save_uploaded_file(file: UploadFile, paper_id: str) -> Path:
    settings.papers_dir.mkdir(parents=True, exist_ok=True)
    # paper_id is always a server-generated uuid — never derived from the
    # client filename — so this path can't be used for traversal.
    dest_path = settings.papers_dir / f"{paper_id}.pdf"

    size = 0
    with open(dest_path, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                f.close()
                dest_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds the {settings.max_upload_mb}MB upload limit.",
                )
            f.write(chunk)

    if size == 0:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return dest_path


def ingest_paper(file: UploadFile, db: Session, owner_id: str) -> dict:
    _validate_upload(file)

    paper_id = str(uuid.uuid4())[:8]
    pdf_path = save_uploaded_file(file, paper_id)

    try:
        pages = extract_text_by_page(pdf_path)
        chunks = chunk_text(pages, paper_id=paper_id, owner_id=owner_id)
        get_vector_store().add_chunks(chunks)
    except PDFExtractionError as exc:
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        # Any other failure mid-ingest (embedding/vector store errors, etc.)
        # — don't leave an orphaned file with no matching DB record.
        pdf_path.unlink(missing_ok=True)
        raise

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
