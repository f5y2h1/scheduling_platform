"""履约管理 API"""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.fulfillment import Fulfillment
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.utils.auth import get_current_user

router = APIRouter()


def _f_to_dict(f: Fulfillment) -> dict:
    return {
        "id": f.id, "fulfillment_no": f.fulfillment_no, "order_no": f.order_no,
        "type": f.type, "status": f.status,
        "carrier_name": f.carrier_name, "tracking_number": f.tracking_number,
        "warehouse_name": f.warehouse_name,
        "origin_address": f.origin_address, "destination_address": f.destination_address,
        "estimated_delivery": str(f.estimated_delivery) if f.estimated_delivery else None,
        "actual_delivery": str(f.actual_delivery) if f.actual_delivery else None,
        "created_at": str(f.created_at) if f.created_at else None,
        "updated_at": str(f.updated_at) if f.updated_at else None,
    }


@router.get("")
async def list_fulfillments(page: int = 1, size: int = 20, status: str | None = None,
                            db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    query = select(Fulfillment)
    if status:
        query = query.where(Fulfillment.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(Fulfillment.created_at.desc()).offset((page - 1) * size).limit(size)
    items = (await db.execute(query)).scalars().all()
    return ApiResponse.ok(PageResult(
        records=[_f_to_dict(f) for f in items], total=total, page=page, size=size,
        total_pages=(total + size - 1) // size if size else 0,
    ))


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    total = (await db.execute(select(func.count()).select_from(Fulfillment))).scalar() or 0
    transit = (await db.execute(select(func.count()).where(Fulfillment.status == "IN_TRANSIT"))).scalar() or 0
    signed = (await db.execute(select(func.count()).where(Fulfillment.status == "SIGNED"))).scalar() or 0
    return ApiResponse.ok({"total": total, "in_transit": transit, "delivered": signed})


@router.get("/{f_id}")
async def get_fulfillment(f_id: int, db: AsyncSession = Depends(get_db),
                          _: User = Depends(get_current_user)):
    r = await db.execute(select(Fulfillment).where(Fulfillment.id == f_id))
    f = r.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="不存在")
    return ApiResponse.ok(_f_to_dict(f))


@router.post("")
async def create_fulfillment(data: dict, db: AsyncSession = Depends(get_db),
                             _: User = Depends(get_current_user)):
    f = Fulfillment(
        fulfillment_no=f"FL{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        order_no=data.get("order_no"),
        origin_address=data.get("origin_address"),
        destination_address=data.get("destination_address"),
        status="PENDING",
    )
    db.add(f)
    await db.flush()
    return ApiResponse.ok(_f_to_dict(f), message="创建成功")


@router.put("/{f_id}/status")
async def update_status(f_id: int, data: dict, db: AsyncSession = Depends(get_db),
                        _: User = Depends(get_current_user)):
    r = await db.execute(select(Fulfillment).where(Fulfillment.id == f_id))
    f = r.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="不存在")
    f.status = data["status"]
    if data["status"] == "SIGNED":
        f.actual_delivery = datetime.datetime.now(datetime.timezone.utc)
        f.signed_at = datetime.datetime.now(datetime.timezone.utc)
    await db.flush()
    return ApiResponse.ok(_f_to_dict(f), message="状态更新成功")


@router.put("/{f_id}/tracking")
async def update_tracking(f_id: int, data: dict, db: AsyncSession = Depends(get_db),
                          _: User = Depends(get_current_user)):
    r = await db.execute(select(Fulfillment).where(Fulfillment.id == f_id))
    f = r.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="不存在")
    f.tracking_number = data.get("tracking_number")
    f.carrier_name = data.get("carrier_name")
    if f.status == "PENDING":
        f.status = "SHIPPED"
    await db.flush()
    return ApiResponse.ok(_f_to_dict(f), message="物流更新成功")
