import uuid
from sqlalchemy.orm import Session
from app.db.models import ChatSession, ChatMessage


def create_session(db: Session, owner_id: str, paper_id: str = None) -> str:
    session_id = str(uuid.uuid4())[:8]
    session = ChatSession(session_id=session_id, owner_id=owner_id, paper_id=paper_id)
    db.add(session)
    db.commit()
    return session_id


def get_or_create_session(db: Session, owner_id: str, session_id: str = None, paper_id: str = None) -> str:
    if session_id:
        existing = (
            db.query(ChatSession)
            .filter(ChatSession.session_id == session_id, ChatSession.owner_id == owner_id)
            .first()
        )
        # Only reuse the session if it belongs to the SAME paper (or both are paper-less).
        # Prevents a session from Paper A silently continuing under Paper B's context.
        if existing and existing.paper_id == paper_id:
            return session_id
    return create_session(db, owner_id=owner_id, paper_id=paper_id)


def add_message(db: Session, session_id: str, role: str, content: str) -> None:
    message = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()


def get_recent_history(db: Session, session_id: str, limit: int = 6) -> list[dict]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]