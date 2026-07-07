# backend/services/history_service.py

from sqlalchemy.orm import Session as DBSession
from app.models import Session, Turn


# ── Sessions ───────────────────────────────────────────────────────────────────

def create_session(db: DBSession, name: str, user_id: int) -> Session:
    session = Session(name=name, user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_sessions(db: DBSession, user_id: int) -> list[Session]:
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
        .all()
    )

def get_session(db: DBSession, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()

def delete_session(db: DBSession, session_id: int) -> None:
    session = get_session(db, session_id)
    if session:
        db.delete(session)
        db.commit()

def add_turn(db: DBSession, session_id: int, question: str, answer: str) -> Turn:
    turn = Turn(session_id=session_id, question=question, answer=answer)
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn

def get_turns(db: DBSession, session_id: int) -> list[Turn]:
    return (
        db.query(Turn)
        .filter(Turn.session_id == session_id)
        .order_by(Turn.created_at.asc())
        .all()
    )