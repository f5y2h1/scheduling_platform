"""
JWT Token 工具模块
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: int, username: str) -> str:
    """生成访问令牌"""
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION)
    payload = {
        "sub": str(user_id),
        "username": username,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, username: str) -> str:
    """生成刷新令牌"""
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_REFRESH_EXPIRATION)
    payload = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """验证 Token 并返回 payload"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])


def get_user_id_from_token(token: str) -> int:
    """从 Token 中提取用户ID"""
    payload = verify_token(token)
    return int(payload.get("sub"))


def get_username_from_token(token: str) -> str:
    """从 Token 中提取用户名"""
    payload = verify_token(token)
    return payload.get("username")
