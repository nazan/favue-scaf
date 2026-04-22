"""
Registration, login (JWT), and current user.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

from app.auth.jwt_utils import decode_access_token
from app.exceptions import InvalidInputError
from app.log_setup import get_app_logger
from app.schemas.user_schema import (
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserPublic,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.service_init import get_user_service
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_user_from_bearer_token(token: str, user_service: UserService) -> Optional[dict]:
    try:
        payload = decode_access_token(token)
        sub = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError, KeyError):
        return None
    return await user_service.get_user_by_id(sub)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = await get_user_from_bearer_token(token, user_service)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    user_service: UserService = Depends(get_user_service),
    logger: logging.Logger = Depends(get_app_logger),
):
    try:
        r = await user_service.register_user(
            body.username, body.email, body.password
        )
        return RegisterResponse(
            id=r["id"],
            username=r["username"],
            email=r["email"],
            email_verified=r["email_verified"],
            message=r["message"],
        )
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        logger.error("register: %s", e)
        raise HTTPException(status_code=400, detail="Registration failed") from e


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    logger: logging.Logger = Depends(get_app_logger),
):
    """Use OAuth2 `username` field for **email** (see frontend login form)."""
    try:
        result = await user_service.authenticate(form_data.username, form_data.password)
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    u = result["user"]
    return LoginResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        user=UserPublic(**u),
    )


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    body: VerifyEmailRequest,
    user_service: UserService = Depends(get_user_service),
    logger: logging.Logger = Depends(get_app_logger),
):
    """Verify email using the token from the link (see transactional email in logs in development)."""
    try:
        await user_service.verify_email(body.token)
        return VerifyEmailResponse(message="Email verified successfully.")
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        logger.error("verify-email: %s", e)
        raise HTTPException(status_code=400, detail="Email verification failed") from e


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserPublic(**current_user)
