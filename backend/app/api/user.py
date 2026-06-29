"""用户管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.utils.auth import get_current_user, get_admin_user

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@router.get("", response_model=ApiResponse[PageResult[dict]])
async def list_users(
    page: int = 1, size: int = 20, keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """用户列表"""
    query = select(User)
    if keyword:
        query = query.where(User.username.ilike(f"%{keyword}%"))
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)
    users = (await db.execute(query)).scalars().all()

    return ApiResponse.ok(PageResult(
        records=[{"id": u.id, "username": u.username, "real_name": u.real_name,
                   "email": u.email, "phone": u.phone, "role": u.role,
                   "status": u.status, "created_at": str(u.created_at)} for u in users],
        total=total, page=page, size=size,
        total_pages=(total + size - 1) // size if size else 0,
    ))


@router.get("/roles/list", response_model=ApiResponse)
async def get_roles():
    return ApiResponse.ok([
        {"code": "ADMIN", "name": "系统管理员"},
        {"code": "MANAGER", "name": "部门经理"},
        {"code": "OPERATOR", "name": "操作员"},
        {"code": "USER", "name": "普通用户"},
    ])


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db),
                   _: User = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ApiResponse.ok({"id": user.id, "username": user.username,
                           "real_name": user.real_name, "email": user.email, "role": user.role})


@router.post("", response_model=ApiResponse)
async def create_user(data: dict, db: AsyncSession = Depends(get_db),
                       _: User = Depends(get_admin_user)):
    existing = (await db.execute(select(User).where(User.username == data["username"]))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data["username"],
        password=pwd_context.hash(data.get("password", "123456")),
        real_name=data.get("real_name"),
        email=data.get("email"),
        phone=data.get("phone"),
        role=data.get("role", "USER"),
        status=data.get("status", 1),
    )
    db.add(user)
    await db.flush()
    return ApiResponse.ok({"id": user.id}, message="创建成功")


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(user_id: int, data: dict, db: AsyncSession = Depends(get_db),
                       _: User = Depends(get_admin_user)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for field in ["real_name", "email", "phone", "role", "department", "avatar"]:
        if field in data and data[field] is not None:
            setattr(user, field, data[field])
    if "status" in data:
        user.status = data["status"]
    await db.flush()
    return ApiResponse.ok(message="更新成功")


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db),
                       _: User = Depends(get_admin_user)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.flush()
    return ApiResponse.ok(message="删除成功")
