from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)


class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    email_verified: bool
    message: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    email_verified: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic


class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResponse(BaseModel):
    message: str
