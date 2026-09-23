"""
Regression tests for app/db/database.py.

Covers two deployment-risk fixes made alongside the email-case-mismatch
login bug:

1. `_normalize_database_url` -- Render (and other managed-Postgres
   providers) issue connection strings starting with "postgres://", which
   SQLAlchemy >=1.4 refuses to load a dialect for. Left unhandled, this
   crashes the app at startup on any redeploy where Render regenerates
   the connection string in that form.
2. `normalize_existing_user_emails` -- rewrites any already-stored user
   email to its canonical (stripped, lowercased) form, so accounts
   created before login/register normalized case aren't locked out.
"""

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-tests-only")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")

import tempfile
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, _normalize_database_url, normalize_existing_user_emails
from app.db.models import User
from app.services.auth_service import hash_password


def test_normalize_database_url_rewrites_postgres_scheme():
    assert _normalize_database_url("postgres://user:pw@host/db") == "postgresql://user:pw@host/db"


def test_normalize_database_url_leaves_postgresql_scheme_untouched():
    url = "postgresql://user:pw@host/db"
    assert _normalize_database_url(url) == url


def test_normalize_database_url_leaves_sqlite_untouched():
    url = "sqlite:///./researchgpt.db"
    assert _normalize_database_url(url) == url


def test_normalize_existing_user_emails_fixes_mixed_case_rows(monkeypatch):
    db_path = os.path.join(tempfile.gettempdir(), f"test_normalize_{uuid.uuid4().hex}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    db.add(User(user_id="u1", email="Legacy@Example.com ", hashed_password=hash_password("pw")))
    db.add(User(user_id="u2", email="already-clean@example.com", hashed_password=hash_password("pw")))
    db.commit()
    db.close()

    monkeypatch.setattr("app.db.database.SessionLocal", TestingSessionLocal)
    normalize_existing_user_emails()

    db = TestingSessionLocal()
    try:
        emails = {u.user_id: u.email for u in db.query(User).all()}
    finally:
        db.close()
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)

    assert emails["u1"] == "legacy@example.com"
    assert emails["u2"] == "already-clean@example.com"


def test_normalize_existing_user_emails_skips_case_collisions(monkeypatch):
    """Two rows that would collide on lowercase are left alone rather than
    silently merged/deleted -- that needs a human decision, not an
    automatic one at startup."""
    db_path = os.path.join(tempfile.gettempdir(), f"test_normalize_collision_{uuid.uuid4().hex}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    db.add(User(user_id="u1", email="Dupe@Example.com", hashed_password=hash_password("pw")))
    db.add(User(user_id="u2", email="dupe@example.com", hashed_password=hash_password("pw")))
    db.commit()
    db.close()

    monkeypatch.setattr("app.db.database.SessionLocal", TestingSessionLocal)
    normalize_existing_user_emails()  # should not raise, and should not touch either row

    db = TestingSessionLocal()
    try:
        emails = {u.user_id: u.email for u in db.query(User).all()}
    finally:
        db.close()
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)

    assert emails["u1"] == "Dupe@Example.com"
    assert emails["u2"] == "dupe@example.com"