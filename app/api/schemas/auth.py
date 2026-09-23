from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


def _normalize_email(value: str) -> str:
    # EmailStr already lowercases the *domain* (it's case-insensitive per
    # the DNS spec) but deliberately leaves the local part (before the
    # "@") exactly as typed, since RFC 5321 technically allows local
    # parts to be case-sensitive. In practice almost no mail provider
    # treats them that way, and leaving this unnormalized is exactly what
    # causes "register works, login 401s" bugs: a user types
    # "User@example.com" once and "user@example.com" another time (or a
    # password manager/autofill does it for them) and the two no longer
    # match a case-sensitive `WHERE email = :email` lookup. Normalizing
    # once here, at the API boundary, means every downstream consumer
    # (service layer, DB queries, JWT payload) only ever sees one
    # canonical form.
    return value.strip().lower()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="At least 8 characters")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


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