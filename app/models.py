# backend/models.py

from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    """Registered user."""
    __tablename__ = "users"

    id:              Mapped[int]  = mapped_column(Integer, primary_key=True, index=True)
    email:           Mapped[str]  = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str]  = mapped_column(String(255))
    created_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete")


class Session(Base):
    """A named conversation session — now owned by a user."""
    __tablename__ = "sessions"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    user_id:    Mapped[int]      = mapped_column(ForeignKey("users.id"))
    name:       Mapped[str]      = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user:  Mapped["User"]        = relationship("User", back_populates="sessions")
    turns: Mapped[list["Turn"]]  = relationship("Turn", back_populates="session", cascade="all, delete")


class Turn(Base):
    """A single Q&A pair within a session."""
    __tablename__ = "turns"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int]      = mapped_column(ForeignKey("sessions.id"))
    question:   Mapped[str]      = mapped_column(Text)
    answer:     Mapped[str]      = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"]   = relationship("Session", back_populates="turns")