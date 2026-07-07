# backend/routers/auth.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.services.auth_service import (
    get_user_by_email, create_user,
    verify_password, create_token, get_current_user
)
from app.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email:    EmailStr
    password: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


@router.post("/register")
def register(req: RegisterRequest, db: DBSession = Depends(get_db)):
    if get_user_by_email(db, req.email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    user  = create_user(db, req.email, req.password)
    token = create_token(user.id, user.email)
    return {"access_token": token, "token_type": "bearer", "email": user.email}


@router.post("/login")
def login(req: LoginRequest, db: DBSession = Depends(get_db)):
    user = get_user_by_email(db, req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_token(user.id, user.email)
    return {"access_token": token, "token_type": "bearer", "email": user.email}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    """Return the currently logged-in user's info."""
    return {"id": current_user.id, "email": current_user.email}