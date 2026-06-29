"""通用 Pydantic 模型"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "success") -> "ApiResponse":
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "error") -> "ApiResponse":
        return cls(code=code, message=message, data=None)


class PageResult(BaseModel, Generic[T]):
    records: list[T] = []
    total: int = 0
    page: int = 1
    size: int = 20
    total_pages: int = 0


class TokenData(BaseModel):
    user_id: int
    username: str
    type: str = "access"
