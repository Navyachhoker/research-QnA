# backend/routers/sessions.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.services.history_service import (
    create_session, get_sessions, get_session,
    delete_session, get_turns
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


class CreateSessionRequest(BaseModel):
    name: str


@router.post("/")
def new_session(req: CreateSessionRequest, db: DBSession = Depends(get_db)):
    """Create a new named conversation session."""
    session = create_session(db, req.name)
    return {"id": session.id, "name": session.name, "created_at": session.created_at}


@router.get("/")
def list_sessions(db: DBSession = Depends(get_db)):
    """List all sessions ordered by newest first."""
    sessions = get_sessions(db)
    return [{"id": s.id, "name": s.name, "created_at": s.created_at} for s in sessions]


@router.get("/{session_id}/history")
def get_history(session_id: int, db: DBSession = Depends(get_db)):
    """Get all turns (Q&A pairs) for a session."""
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    turns = get_turns(db, session_id)
    return {
        "session_id":   session_id,
        "session_name": session.name,
        "turns": [
            {
                "id":         t.id,
                "question":   t.question,
                "answer":     t.answer,
                "created_at": t.created_at,
            }
            for t in turns
        ],
    }


@router.delete("/{session_id}")
def remove_session(session_id: int, db: DBSession = Depends(get_db)):
    """Delete a session and all its turns."""
    if not delete_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"message": f"Session {session_id} deleted."}