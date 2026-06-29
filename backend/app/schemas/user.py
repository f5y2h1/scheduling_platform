"""用户相关 Schema"""
from datetime import datetime

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    real_name: str = Field(..., min_length=1, max_length=64, description="真实姓名")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, max_length=20, description="手机号")
    role: str = Field("USER", description="角色")
    department: str | None = Field(None, description="部门")


class UserUpdateRequest(BaseModel):
    real_name: str | None = Field(None, description="真实姓名")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, max_length=20, description="手机号")
    role: str | None = Field(None, description="角色")
    department: str | None = Field(None, description="部门")
    status: int | None = Field(None, description="状态")


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str | None
    email: str | None
    phone: str | None
    avatar: str | None
    role: str
    department: str | None
    status: int
    created_at: datetime
    updated_at: datetime


class UserQueryRequest(BaseModel):
    keyword: str | None = None
    role: str | None = None
    status: int | None = None