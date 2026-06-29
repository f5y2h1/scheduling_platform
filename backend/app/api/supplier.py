"""供应商管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.utils.auth import get_current_user

router = APIRouter()


def _s_to_dict(s: Supplier) -> dict:
    return {
        "id": s.id, "name": s.name, "code": s.code, "type": s.type,
        "status": s.status, "contact_name": s.contact_name,
        "contact_phone": s.contact_phone, "contact_email": s.contact_email,
        "address": s.address, "rating": s.rating,
        "cooperation_years": s.cooperation_years,
        "on_time_delivery_rate": s.on_time_delivery_rate,
        "quality_pass_rate": s.quality_pass_rate,
        "created_at": str(s.created_at) if s.created_at else None,
        "updated_at": str(s.updated_at) if s.updated_at else None,
    }


@router.get("")
async def list_suppliers(page: int = 1, size: int = 20, keyword: str | None = None,
                         db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    query = select(Supplier)
    if keyword:
        query = query.where(Supplier.name.ilike(f"%{keyword}%"))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(Supplier.rating.desc()).offset((page - 1) * size).limit(size)
    items = (await db.execute(query)).scalars().all()
    return ApiResponse.ok(PageResult(
        records=[_s_to_dict(s) for s in items], total=total, page=page, size=size,
        total_pages=(total + size - 1) // size if size else 0,
    ))


@router.get("/{s_id}")
async def get_supplier(s_id: int, db: AsyncSession = Depends(get_db),
                       _: User = Depends(get_current_user)):
    r = await db.execute(select(Supplier).where(Supplier.id == s_id))
    s = r.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="不存在")
    return ApiResponse.ok(_s_to_dict(s))


@router.post("")
async def create_supplier(data: dict, db: AsyncSession = Depends(get_db),
                          _: User = Depends(get_current_user)):
    s = Supplier(
        name=data["name"], code=data.get("code"), type=data.get("type"),
        contact_name=data.get("contact_name"), contact_phone=data.get("contact_phone"),
        contact_email=data.get("contact_email"), address=data.get("address"),
        status=data.get("status", "ACTIVE"),
    )
    db.add(s)
    await db.flush()
    return ApiResponse.ok(_s_to_dict(s), message="创建成功")


@router.put("/{s_id}")
async def update_supplier(s_id: int, data: dict, db: AsyncSession = Depends(get_db),
                          _: User = Depends(get_current_user)):
    r = await db.execute(select(Supplier).where(Supplier.id == s_id))
    s = r.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="不存在")
    for field in ["name", "contact_name", "contact_phone", "contact_email", "address",
                   "rating", "on_time_delivery_rate", "quality_pass_rate"]:
        if field in data and data[field] is not None:
            setattr(s, field, data[field])
    await db.flush()
    return ApiResponse.ok(_s_to_dict(s), message="更新成功")


@router.put("/{s_id}/status")
async def update_status(s_id: int, data: dict, db: AsyncSession = Depends(get_db),
                        _: User = Depends(get_current_user)):
    r = await db.execute(select(Supplier).where(Supplier.id == s_id))
    s = r.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="不存在")
    s.status = data["status"]
    await db.flush()
    return ApiResponse.ok(message="状态更新成功")
