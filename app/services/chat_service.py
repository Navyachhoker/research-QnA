import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from app.db.models import ChatMessage, ChatSession


def create_session(db: DBSession, owner_id: str, name: str, paper_id: str | None = None) -> ChatSession:
    session = ChatSession(session_id=str(uuid.uuid4()), owner_id=owner_id, name=name, paper_id=paper_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: DBSession, owner_id: str) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.owner_id == owner_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


def get_owned_session(db: DBSession, session_id: str, owner_id: str) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id, ChatSession.owner_id == owner_id)
        .first()
    )
    if session is None:
        # 404, not 403: don't reveal whether a session with this id exists
        # for a different owner.
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


def delete_session(db: DBSession, session_id: str, owner_id: str) -> None:
    session = get_owned_session(db, session_id, owner_id)
    db.query(ChatMessage).filter(ChatMessage.session_id == session.session_id).delete()
    db.delete(session)
    db.commit()


def add_message(db: DBSession, session_id: str, role: str, content: str) -> ChatMessage:
    message = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_recent_history(db: DBSession, session_id: str, max_turns: int = 5) -> list[dict]:
    """Role-based recent turns for feeding back into the LLM as context."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    turns = _pair_messages(messages)
    return turns[-max_turns:]


def get_full_history(db: DBSession, session_id: str) -> list[dict]:
    """Full history, paired into {question, answer, created_at} turns for
    the /sessions/{id}/history endpoint the frontend renders."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return _pair_messages(messages, with_metadata=True)


def _pair_messages(messages: list[ChatMessage], with_metadata: bool = False) -> list[dict]:
    """Pairs sequential user->assistant messages into turns. Any unpaired
    trailing user message (e.g. a request that failed before the answer
    was stored) is dropped rather than shown as a broken turn."""
    turns = []
    pending_question = None
    for message in messages:
        if message.role == "user":
            pending_question = message
        elif message.role == "assistant" and pending_question is not None:
            turn: dict = {"question": pending_question.content, "answer": message.content}
            if with_metadata:
                turn["id"] = message.id
                turn["created_at"] = message.created_at
            turns.append(turn)
            pending_question = None
    return turns
