from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime
from typing import Any, Optional

from passlib.context import CryptContext
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.auth.jwt_utils import create_access_token
from app.db import tables
from app.exceptions import InvalidInputError
from app.services.email_service import EmailService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        password = raw[:72].decode("utf-8", errors="ignore")
    if not password:
        password = "x"
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _gen_verification_token() -> str:
    return secrets.token_urlsafe(32)


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        email_service: EmailService,
        _logger: Optional[logging.Logger] = None,
    ):
        self.db = db
        self._email = email_service
        self._logger = _logger or logger

    async def register_user(self, username: str, email: str, password: str) -> dict:
        u = (username or "").strip()
        e = (email or "").strip().lower()
        if not u or not e or "@" not in e:
            raise InvalidInputError("Valid username and email are required")
        if not password or len(password) < 8:
            raise InvalidInputError("Password must be at least 8 characters")
        raw = password.encode("utf-8")
        if len(raw) > 72:
            password = raw[:72].decode("utf-8", errors="ignore") or "x"
        h = _hash_password(password)
        verification_token = _gen_verification_token()
        token_hash = hashlib.sha256(verification_token.encode()).hexdigest()
        now = datetime.utcnow()
        try:
            await self.db.execute(
                insert(tables.users).values(
                    username=u,
                    email=e,
                    password_hash=h,
                    is_active=True,
                    email_verification_token=token_hash,
                    created_at=now,
                    updated_at=now,
                )
            )
            await self.db.commit()
        except IntegrityError as ex:
            await self.db.rollback()
            raise InvalidInputError("Username or email already in use") from ex
        r = await self.db.execute(
            select(
                tables.users.c.id,
                tables.users.c.username,
                tables.users.c.email,
            ).where(tables.users.c.email == e)
        )
        row = r.mappings().first()
        if not row:
            raise InvalidInputError("Failed to create user")
        try:
            await self._email.send_verification_email(e, verification_token)
        except Exception as exc:  # noqa: BLE001
            self._logger.exception("Failed to send verification email: %s", exc)
        self._logger.info("Registered user id=%s %s (verification sent)", row["id"], e)
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "email_verified": False,
            "message": (
                "Registration successful. Please check your email for a verification link "
                "before signing in."
            ),
        }

    async def verify_email(self, token: str) -> bool:
        if not (token or "").strip():
            raise InvalidInputError("Invalid verification token")
        token_hash = hashlib.sha256(token.strip().encode()).hexdigest()
        r = await self.db.execute(
            select(tables.users.c.id, tables.users.c.email_verified_at).where(
                tables.users.c.email_verification_token == token_hash
            )
        )
        row = r.mappings().first()
        if not row:
            raise InvalidInputError("Invalid verification token")
        if row["email_verified_at"] is not None:
            return True
        now = datetime.utcnow()
        await self.db.execute(
            update(tables.users)
            .where(tables.users.c.id == row["id"])
            .values(
                email_verified_at=now,
                email_verification_token=None,
                updated_at=now,
            )
        )
        await self.db.commit()
        self._logger.info("Email verified for user id=%s", row["id"])
        return True

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        e = (email or "").strip().lower()
        r = await self.db.execute(
            select(
                tables.users.c.id,
                tables.users.c.username,
                tables.users.c.email,
                tables.users.c.password_hash,
                tables.users.c.is_active,
                tables.users.c.email_verified_at,
            ).where(tables.users.c.email == e)
        )
        row = r.mappings().first()
        if not row:
            return None
        if not row["is_active"]:
            raise InvalidInputError("Account is inactive")
        if not _verify_password(password, row["password_hash"]):
            return None
        token = create_access_token(
            sub=row["id"], email=row["email"], username=row["username"]
        )
        self._logger.info("Authenticated id=%s %s", row["id"], e)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "is_active": bool(row["is_active"]),
                "email_verified": row["email_verified_at"] is not None,
            },
        }

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        r = await self.db.execute(
            select(
                tables.users.c.id,
                tables.users.c.username,
                tables.users.c.email,
                tables.users.c.is_active,
                tables.users.c.email_verified_at,
            ).where(tables.users.c.id == user_id)
        )
        row = r.mappings().first()
        if not row:
            return None
        if not row["is_active"]:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "is_active": bool(row["is_active"]),
            "email_verified": row["email_verified_at"] is not None,
        }

    async def user_exists(self, user_id: int) -> bool:
        r = await self.db.execute(
            select(tables.users.c.id).where(tables.users.c.id == user_id).limit(1)
        )
        return r.first() is not None
