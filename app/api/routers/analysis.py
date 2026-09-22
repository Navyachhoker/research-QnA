from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.analysis import (
    CompareRequest,
    CompareResponse,
    RelatedWorkRequest,
    RelatedWorkResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.db.database import get_db
from app.db.models import User
from app.services import (
    auth_service,
    comparator_service,
    paper_service,
    related_work_service,
    summarizer_service,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(
    payload: SummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    paper = paper_service.get_paper(payload.paper_id, db, owner_id=current_user.user_id)
    summary = summarizer_service.summarize_paper(paper.paper_id, owner_id=current_user.user_id)
    return SummarizeResponse(paper_id=paper.paper_id, filename=paper.filename, summary=summary)


@router.post("/compare", response_model=CompareResponse)
def compare(
    payload: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    paper_a = paper_service.get_paper(payload.paper_a_id, db, owner_id=current_user.user_id)
    paper_b = paper_service.get_paper(payload.paper_b_id, db, owner_id=current_user.user_id)
    comparison = comparator_service.compare_papers(
        paper_a.paper_id, paper_b.paper_id, owner_id=current_user.user_id
    )
    return CompareResponse(
        paper_a=paper_a.filename,
        paper_b=paper_b.filename,
        comparison=comparison,
    )


@router.post("/related-work", response_model=RelatedWorkResponse)
def related_work(
    payload: RelatedWorkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    result = related_work_service.generate_related_work_by_topic(payload.topic, owner_id=current_user.user_id)
    return RelatedWorkResponse(
        topic=payload.topic,
        related_work=result["related_work"],
        referenced_paper_ids=result["referenced_paper_ids"],
    )
