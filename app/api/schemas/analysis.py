from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)


class SummarizeResponse(BaseModel):
    paper_id: str
    filename: str
    summary: str


class CompareRequest(BaseModel):
    paper_a_id: str = Field(..., min_length=1)
    paper_b_id: str = Field(..., min_length=1)


class CompareResponse(BaseModel):
    paper_a: str
    paper_b: str
    comparison: str


class RelatedWorkRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=500)


class RelatedWorkResponse(BaseModel):
    topic: str
    related_work: str
    referenced_paper_ids: list[str]
