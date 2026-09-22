from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas.paper import PaperListResponse, PaperResponse, UploadResponse
from app.db.database import get_db
from app.db.models import User
from app.services import arxiv_service, auth_service, ingest_service, paper_service

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/upload", response_model=UploadResponse, status_code=201)
def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    result = ingest_service.ingest_paper(file, db, owner_id=current_user.user_id)
    return UploadResponse(**result)


@router.get("/list", response_model=PaperListResponse)
def list_papers(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    papers = paper_service.list_papers(db, owner_id=current_user.user_id)
    return PaperListResponse(papers=[PaperResponse.model_validate(p) for p in papers], count=len(papers))


@router.delete("/{paper_id}", status_code=204)
def delete_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    # get_paper (owner-scoped) raises 404 if the paper doesn't exist or
    # belongs to someone else, so this also naturally prevents deleting
    # another user's paper.
    paper_service.delete_paper(paper_id, db, owner_id=current_user.user_id)


@router.get("/arxiv/search")
def search_arxiv(
    query: str, max_results: int = 5, current_user: User = Depends(auth_service.get_current_user)
):
    return {"results": arxiv_service.search_arxiv_papers(query, max_results=max_results)}


@router.post("/arxiv/import/{arxiv_id}", response_model=UploadResponse, status_code=201)
def import_arxiv(
    arxiv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    result = arxiv_service.import_paper_from_arxiv(arxiv_id, db, owner_id=current_user.user_id)
    return UploadResponse(**result)
