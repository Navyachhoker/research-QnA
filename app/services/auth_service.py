# backend/services/auth_service.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DBSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import User
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Password ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ────────────────────────────────────────────────────────────────────────

def create_token(user_id: int, email: str) -> str:
    """Create a signed JWT that expires in JWT_EXPIRE_HOURS."""
    payload = {
        "sub":   str(user_id),
        "email": email,
        "exp":   datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises HTTPException on failure."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── User CRUD ──────────────────────────────────────────────────────────────────

def get_user_by_email(db: DBSession, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: DBSession, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── FastAPI Dependency ─────────────────────────────────────────────────────────

def get_current_user(
    token: str        = Depends(oauth2_scheme),
    db:    DBSession  = Depends(get_db),
) -> User:
    """
    FastAPI dependency — inject into any protected route.
    Decodes the JWT, loads the user from DB, returns the User object.
    """
    payload = decode_token(token)
    user    = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


def hash_password(plain: str) -> str:
    # bcrypt max is 72 bytes — truncate to be safe
    return pwd_context.hash(plain[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)