from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.db.database import get_db
from app.db.models import User
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, email=payload.email, password=payload.password)
    token = auth_service.create_access_token(user.user_id, user.email)
    return TokenResponse(access_token=token, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, email=payload.email, password=payload.password)
    token = auth_service.create_access_token(user.user_id, user.email)
    return TokenResponse(access_token=token, email=user.email)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user
