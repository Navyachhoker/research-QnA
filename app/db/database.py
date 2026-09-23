from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# check_same_thread=False is a SQLite-specific pysqlite connect arg (lets
# the connection be used across FastAPI's threadpool). Passing it to
# Postgres's driver raises TypeError, so it's only applied when the
# configured DATABASE_URL is actually SQLite -- switching to Postgres for
# deployment is then just a DATABASE_URL change, no code change needed.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()