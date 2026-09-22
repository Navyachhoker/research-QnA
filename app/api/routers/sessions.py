from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.sessions import CreateSessionRequest, HistoryResponse, SessionResponse, TurnResponse
from app.db.database import get_db
from app.db.models import User
from app.services import auth_service, chat_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=201)
def create_session(
    payload: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    session = chat_service.create_session(db, owner_id=current_user.user_id, name=payload.name)
    return SessionResponse(id=session.session_id, name=session.name, created_at=session.created_at)


@router.get("/", response_model=list[SessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    sessions = chat_service.list_sessions(db, owner_id=current_user.user_id)
    return [SessionResponse(id=s.session_id, name=s.name, created_at=s.created_at) for s in sessions]


@router.get("/{session_id}/history", response_model=HistoryResponse)
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    session = chat_service.get_owned_session(db, session_id, owner_id=current_user.user_id)
    turns = chat_service.get_full_history(db, session.session_id)
    return HistoryResponse(
        session_id=session.session_id,
        session_name=session.name,
        turns=[TurnResponse(**t) for t in turns],
    )


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    chat_service.delete_session(db, session_id, owner_id=current_user.user_id)
