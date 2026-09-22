from datetime import datetime

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class SessionResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TurnResponse(BaseModel):
    id: int | None = None
    question: str
    answer: str
    created_at: datetime | None = None


class HistoryResponse(BaseModel):
    session_id: str
    session_name: str
    turns: list[TurnResponse]
