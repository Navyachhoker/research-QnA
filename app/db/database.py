from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


def _normalize_database_url(url: str) -> str:
    # Render (and Heroku, and some other managed-Postgres providers) hand
    # out connection strings starting with "postgres://". libpq accepts
    # that scheme, but SQLAlchemy >=1.4 dropped support for it and raises
    # `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres`
    # at engine-creation time -- i.e. the app fails to even start. This
    # has nothing to do with the login-specific bug this module also
    # fixes, but it's a real, easy-to-hit deployment failure mode for
    # this exact stack, so it's corrected here once rather than relying
    # on the platform's connection string being in the form SQLAlchemy
    # expects.
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


_database_url = _normalize_database_url(settings.database_url)

# check_same_thread=False is a SQLite-specific pysqlite connect arg (lets
# the connection be used across FastAPI's threadpool). Passing it to
# Postgres's driver raises TypeError, so it's only applied when the
# configured DATABASE_URL is actually SQLite -- switching to Postgres for
# deployment is then just a DATABASE_URL change, no code change needed.
_connect_args = {"check_same_thread": False} if _database_url.startswith("sqlite") else {}

engine = create_engine(_database_url, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_existing_user_emails() -> None:
    """
    One-time, idempotent cleanup for rows written before email
    normalization existed: any user whose stored email has uppercase
    characters or stray whitespace gets rewritten to the canonical
    (stripped, lowercased) form, so they can still log in once
    login/register both normalize case.

    This project doesn't use Alembic (see the note on `create_all`
    below) so there's no migration system to hang this off of; running
    it unconditionally at startup is the equivalent lightweight
    approach, safe to run on every boot because it's a no-op once every
    row is already normalized.

    If two existing rows would normalize to the same email (e.g.
    "user@x.com" and "User@x.com" both already exist as separate rows --
    only possible for accounts created before this fix), that pair is
    left untouched and logged, since silently merging or deleting one is
    not a safe default; it needs a human decision.
    """
    import logging

    from app.db.models import User

    logger = logging.getLogger("researchgpt")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        normalized_to_users: dict[str, list[User]] = {}
        for user in users:
            normalized_to_users.setdefault(user.email.strip().lower(), []).append(user)

        changed = 0
        for normalized_email, rows in normalized_to_users.items():
            if len(rows) > 1:
                logger.warning(
                    "Skipping email normalization for %d accounts that would collide on %r "
                    "after lowercasing -- resolve manually.",
                    len(rows),
                    normalized_email,
                )
                continue
            (user,) = rows
            if user.email != normalized_email:
                user.email = normalized_email
                changed += 1

        if changed:
            db.commit()
            logger.info("Normalized email casing for %d existing user account(s).", changed)
    finally:
        db.close()