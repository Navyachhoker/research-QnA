# backend/schemas/analysis.py

from pydantic import BaseModel, Field


# ── Requests ───────────────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    paper_name: str = Field(..., min_length=1, max_length=255)


class CompareRequest(BaseModel):
    paper_a: str = Field(..., min_length=1, max_length=255)
    paper_b: str = Field(..., min_length=1, max_length=255)


class RelatedWorkRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=500)


# ── Responses ──────────────────────────────────────────────────────────────────

class SummarizeResponse(BaseModel):
    paper:       str
    summary:     str
    chunk_count: int


class CompareResponse(BaseModel):
    paper_a:     str
    paper_b:     str
    comparison:  str
    chunks_used: dict[str, int]       # {"paper_a": 12, "paper_b": 10}


class RelatedWorkResponse(BaseModel):
    topic:        str
    related_work: str
    papers_used:  list[str]
    chunks_used:  int