# backend/schemas/sessions.py

from pydantic import BaseModel, Field
from datetime import datetime


class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class SessionResponse(BaseModel):
    """Single session summary."""
    id:         int
    name:       str
    created_at: datetime

    model_config = {"from_attributes": True}


class TurnResponse(BaseModel):
    """Single Q&A turn within a session."""
    id:         int
    question:   str
    answer:     str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    """Full session history returned by GET /sessions/{id}/history."""
    session_id:   int
    session_name: str
    turns:        list[TurnResponse]