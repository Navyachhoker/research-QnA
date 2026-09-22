from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    paper: str | None = None  # paper_id to scope retrieval to, or None for all of the user's papers
    top_k: int = Field(default=5, ge=1, le=20)
    session_id: str | None = None


class SourceItem(BaseModel):
    source_num: int
    paper_id: str
    page: int
    chunk_id: str
    snippet: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
