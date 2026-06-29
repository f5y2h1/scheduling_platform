"""认证 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse, UserInfo, TokenRefreshRequest
from app.schemas.common import ApiResponse

router = APIRouter()
# pbkdf2_sha256：无密码长度限制，稳定可靠
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)

    return ApiResponse.ok(LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserInfo(
            id=user.id, username=user.username,
            real_name=user.real_name, avatar=user.avatar, role=user.role,
        ),
    ))


@router.post("/register", response_model=ApiResponse[LoginResponse])
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=req.username,
        password=pwd_context.hash(req.password),
        real_name=req.real_name,
        email=req.email,
        phone=req.phone,
        role="USER",
        status=1,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)

    return ApiResponse.ok(LoginResponse(
        access_token=access_token, refresh_token=refresh_token,
        user=UserInfo(id=user.id, username=user.username, real_name=user.real_name, role=user.role),
    ))


@router.post("/refresh", response_model=ApiResponse[LoginResponse])
async def refresh(req: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    """刷新 Token"""
    try:
        payload = verify_token(req.refresh_token)
        user_id = int(payload.get("sub"))
        username = payload.get("username")
    except Exception:
        raise HTTPException(status_code=401, detail="刷新令牌无效")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)

    return ApiResponse.ok(LoginResponse(
        access_token=access_token, refresh_token=refresh_token,
        user=UserInfo(id=user.id, username=user.username, real_name=user.real_name, role=user.role),
    ))


@router.post("/logout", response_model=ApiResponse)
async def logout():
    return ApiResponse.ok(message="已退出")
