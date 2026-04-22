"""JWT creation and validation (HS256)."""

from __future__ import annotations

import time

from jose import jwt

from app.config import settings


def create_access_token(*, sub: int, email: str, username: str) -> str:
    exp = int(time.time()) + int(settings.jwt_access_token_expire_minutes * 60)
    return jwt.encode(
        {"sub": str(sub), "email": email, "username": username, "exp": exp},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
