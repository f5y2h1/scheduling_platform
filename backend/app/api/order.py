"""订单管理 API"""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.core.database import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_orders(
    page: int = 1, size: int = 20, status: str | None = None, keyword: str | None = None,
    db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    if keyword:
        query = query.where(Order.customer_name.ilike(f"%{keyword}%"))
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    query = query.order_by(Order.created_at.desc()).offset((page - 1) * size).limit(size)
    orders = (await db.execute(query)).scalars().all()
    return ApiResponse.ok(PageResult(
        records=[_order_to_dict(o) for o in orders],
        total=total, page=page, size=size,
        total_pages=(total + size - 1) // size if size else 0,
    ))


@router.get("/stats")
async def order_stats(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    total = (await db.execute(select(func.count()).select_from(Order))).scalar() or 0
    pending = (await db.execute(select(func.count()).where(Order.status == "PENDING"))).scalar() or 0
    shipping = (await db.execute(select(func.count()).where(Order.status == "SHIPPING"))).scalar() or 0
    delivered = (await db.execute(select(func.count()).where(Order.status == "DELIVERED"))).scalar() or 0
    return ApiResponse.ok({"total": total, "pending": pending, "shipping": shipping, "delivered": delivered})


@router.get("/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db),
                    _: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return ApiResponse.ok(_order_to_dict(order))


@router.post("")
async def create_order(data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    order = Order(
        order_no=data.get("order_no") or f"SO{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        customer_name=data.get("customer_name"),
        product_name=data.get("product_name"),
        quantity=data.get("quantity", 1),
        unit_price=Decimal(str(data["unit_price"])) if data.get("unit_price") else None,
        total_amount=Decimal(str(data.get("total_amount", 0))),
        warehouse_name=data.get("warehouse_name"),
        shipping_address=data.get("shipping_address"),
        remark=data.get("remark"),
        created_by=current_user.username,
        status="PENDING",
    )
    if order.unit_price and order.quantity and not order.total_amount:
        order.total_amount = order.unit_price * order.quantity
    db.add(order)
    await db.flush()
    return ApiResponse.ok(_order_to_dict(order), message="创建成功")


@router.put("/{order_id}")
async def update_order(order_id: int, data: dict, db: AsyncSession = Depends(get_db),
                       _: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    for field in ["customer_name", "product_name", "quantity", "shipping_address", "remark"]:
        if field in data and data[field] is not None:
            setattr(order, field, data[field])
    await db.flush()
    return ApiResponse.ok(_order_to_dict(order), message="更新成功")


@router.put("/{order_id}/status")
async def update_status(order_id: int, data: dict, db: AsyncSession = Depends(get_db),
                        _: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = data["status"]
    if data["status"] == "SHIPPED":
        order.shipped_date = datetime.datetime.now(datetime.timezone.utc)
    if data["status"] == "DELIVERED":
        order.delivered_date = datetime.datetime.now(datetime.timezone.utc)
    await db.flush()
    return ApiResponse.ok(_order_to_dict(order), message="状态更新成功")


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db),
                       _: User = Depends(get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status not in ("PENDING", "CONFIRMED"):
        raise HTTPException(status_code=400, detail="当前状态不允许取消")
    order.status = "CANCELLED"
    await db.flush()
    return ApiResponse.ok(message="已取消")


def _order_to_dict(o: Order) -> dict:
    return {
        "id": o.id, "order_no": o.order_no, "order_type": o.order_type,
        "status": o.status, "customer_name": o.customer_name,
        "product_name": o.product_name, "quantity": o.quantity,
        "unit_price": float(o.unit_price) if o.unit_price else None,
        "total_amount": float(o.total_amount) if o.total_amount else None,
        "warehouse_name": o.warehouse_name, "shipping_address": o.shipping_address,
        "remark": o.remark, "created_by": o.created_by,
        "created_at": str(o.created_at) if o.created_at else None,
        "updated_at": str(o.updated_at) if o.updated_at else None,
    }
