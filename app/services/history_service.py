# backend/services/history_service.py

from sqlalchemy.orm import Session as DBSession
from models import Session, Turn


# ── Sessions ───────────────────────────────────────────────────────────────────

def create_session(db: DBSession, name: str) -> Session:
    session = Session(name=name)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions(db: DBSession) -> list[Session]:
    return db.query(Session).order_by(Session.created_at.desc()).all()


def get_session(db: DBSession, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()


def delete_session(db: DBSession, session_id: int) -> bool:
    session = get_session(db, session_id)
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


# ── Turns ──────────────────────────────────────────────────────────────────────

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