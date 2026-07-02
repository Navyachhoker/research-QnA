#summarize + compare endpoints

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.analysis_service import summarize_paper, compare_papers, generate_related_work

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class SummarizeRequest(BaseModel):
    paper_name: str


class CompareRequest(BaseModel):
    paper_a: str
    paper_b: str


class RelatedWorkRequest(BaseModel):
    topic: str


@router.post("/summarize")
def summarize(req: SummarizeRequest):
    """Summarize a single ingested paper."""
    try:
        return summarize_paper(req.paper_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/compare")
def compare(req: CompareRequest):
    """Compare two ingested papers side by side."""
    if req.paper_a == req.paper_b:
        raise HTTPException(status_code=400, detail="paper_a and paper_b must be different.")
    try:
        return compare_papers(req.paper_a, req.paper_b)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/related-work")
def related_work(req: RelatedWorkRequest):
    """Generate a Related Work section from all ingested papers on a given topic."""
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        return generate_related_work(req.topic)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))