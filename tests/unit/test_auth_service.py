import os

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-tests-only")

import time
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from jose import jwt as jose_jwt

from app.config import settings
from app.services import auth_service


def test_hash_password_is_not_plaintext():
    hashed = auth_service.hash_password("mypassword123")
    assert hashed != "mypassword123"
    assert hashed.startswith("$2b$")  # bcrypt marker


def test_verify_password_correct_and_incorrect():
    hashed = auth_service.hash_password("correct-password")
    assert auth_service.verify_password("correct-password", hashed) is True
    assert auth_service.verify_password("wrong-password", hashed) is False


def test_verify_password_handles_very_long_password():
    long_password = "a" * 200
    hashed = auth_service.hash_password(long_password)
    assert auth_service.verify_password(long_password, hashed) is True


def test_create_and_decode_access_token_roundtrip():
    token = auth_service.create_access_token(user_id="user-123", email="a@example.com")
    payload = auth_service.decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["email"] == "a@example.com"


def test_decode_access_token_rejects_garbage():
    with pytest.raises(HTTPException) as exc_info:
        auth_service.decode_access_token("not.a.valid.jwt")
    assert exc_info.value.status_code == 401


def test_decode_access_token_rejects_expired_token():
    expired_payload = {
        "sub": "user-123",
        "email": "a@example.com",
        "exp": int(time.time()) - 3600,
    }
    expired_token = jose_jwt.encode(
        expired_payload, settings.require_jwt_secret(), algorithm=settings.jwt_algorithm
    )

    with pytest.raises(HTTPException) as exc_info:
        auth_service.decode_access_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_decode_access_token_rejects_wrong_signature():
    token = jose_jwt.encode(
        {"sub": "x", "email": "x@example.com"}, "a-totally-different-secret", algorithm="HS256"
    )
    with pytest.raises(HTTPException) as exc_info:
        auth_service.decode_access_token(token)
    assert exc_info.value.status_code == 401


def test_create_access_token_requires_jwt_secret():
    with patch.object(settings, "jwt_secret_key", None):
        with pytest.raises(RuntimeError):
            auth_service.create_access_token(user_id="u1", email="a@example.com")


def test_create_access_token_requires_jwt_secret():
    with patch.object(settings, "jwt_secret_key", None):
        with pytest.raises(RuntimeError):
            auth_service.create_access_token(user_id="u1", email="a@example.com")


# --- Regression: auth_service normalizes email case defensively ---
# (belt-and-suspenders for the schema-level normalization in
# app/api/schemas/auth.py -- see tests/integration/test_auth_api.py for
# the end-to-end register/login reproduction of the original bug.)


def test_register_user_normalizes_email_case(test_db):
    db = test_db()
    try:
        user = auth_service.register_user(db, email="MixedCase@Example.com", password="password123")
        assert user.email == "mixedcase@example.com"
    finally:
        db.close()


def test_authenticate_user_normalizes_email_case(test_db):
    db = test_db()
    try:
        auth_service.register_user(db, email="CaseTest@Example.com", password="password123")
        user = auth_service.authenticate_user(db, email="casetest@example.com", password="password123")
        assert user.email == "casetest@example.com"
    finally:
        db.close()