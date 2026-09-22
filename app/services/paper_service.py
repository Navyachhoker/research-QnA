from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Paper
from app.rag.vector_store import get_vector_store


def list_papers(db: Session, owner_id: str) -> list[Paper]:
    return db.query(Paper).filter(Paper.owner_id == owner_id).order_by(Paper.uploaded_at.desc()).all()


def get_paper(paper_id: str, db: Session, owner_id: str) -> Paper:
    paper = db.query(Paper).filter(Paper.paper_id == paper_id, Paper.owner_id == owner_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper


def delete_paper(paper_id: str, db: Session, owner_id: str) -> None:
    paper = get_paper(paper_id, db, owner_id)

    get_vector_store().delete_paper_chunks(paper_id, owner_id=owner_id)

    pdf_path: Path = settings.papers_dir / f"{paper_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    db.delete(paper)
    db.commit()
