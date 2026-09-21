from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Paper(Base):
    __tablename__ = "papers"

    paper_id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    num_pages = Column(Integer, nullable=False)
    num_chunks = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    paper_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))