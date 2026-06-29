"""认证相关 Schema"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=6, max_length=64)
    real_name: str = Field(..., min_length=1)
    email: str | None = None
    phone: str | None = None


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    avatar: str | None = None
    role: str = "USER"


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 86400
    user: UserInfo


class TokenRefreshRequest(BaseModel):
    refresh_token: str
