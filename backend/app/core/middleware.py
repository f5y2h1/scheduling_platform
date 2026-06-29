"""
中间件层
提供请求日志、异常处理、认证拦截等功能
"""
import time
from typing import Callable

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException, AuthenticationError, AuthorizationError, NotFoundError, ValidationError, ConflictError, AIError
from app.core.logger import logger


async def request_log_middleware(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    path = request.url.path
    method = request.method

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"[{method}] {path} {response.status_code} {process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[{method}] {path} ERROR {process_time:.2f}s - {str(e)}")
        raise


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": None}
        )
    elif isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.code,
            content={"code": exc.code, "message": exc.message, "data": None}
        )
    elif isinstance(exc, AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": exc.message, "data": None}
        )
    elif isinstance(exc, AuthorizationError):
        return JSONResponse(
            status_code=403,
            content={"code": 403, "message": exc.message, "data": None}
        )
    elif isinstance(exc, NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"code": 404, "message": exc.message, "data": None}
        )
    elif isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": exc.message, "data": None}
        )
    elif isinstance(exc, ConflictError):
        return JSONResponse(
            status_code=409,
            content={"code": 409, "message": exc.message, "data": None}
        )
    elif isinstance(exc, AIError):
        return JSONResponse(
            status_code=503,
            content={"code": 503, "message": exc.message, "data": None}
        )

    if settings.DEBUG:
        logger.error(f"未处理异常: {exc}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": str(exc), "data": None}
        )

    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )