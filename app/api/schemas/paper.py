from datetime import datetime

from pydantic import BaseModel


class PaperResponse(BaseModel):
    paper_id: str
    filename: str
    num_pages: int
    num_chunks: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class PaperListResponse(BaseModel):
    papers: list[PaperResponse]
    count: int


class UploadResponse(BaseModel):
    paper_id: str
    filename: str
    num_pages: int
    num_chunks: int
