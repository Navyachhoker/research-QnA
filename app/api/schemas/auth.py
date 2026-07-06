# backend/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr                        # validates it's actually an email format
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Password must be at least 6 characters"
    )


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Returned on successful login or register."""
    access_token: str
    token_type:   str = "bearer"
    email:        str


class UserResponse(BaseModel):
    """Returned by GET /auth/me."""
    id:         int
    email:      str
    created_at: datetime

    model_config = {"from_attributes": True}   # allows .model_validate(orm_object)