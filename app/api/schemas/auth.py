from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="At least 8 characters")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Returned on successful login or register."""

    access_token: str
    token_type: str = "bearer"
    email: str


class UserResponse(BaseModel):
    """Returned by GET /auth/me."""

    user_id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
