"""库存管理 API"""
import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.inventory import Inventory
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.utils.auth import get_current_user

router = APIRouter()


def _serialize_dt(v):
    """datetime → ISO 字符串，确保 JSON 可序列化"""
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        return v.isoformat()
    return str(v)


def _inv_to_dict(i: Inventory) -> dict:
    """显式字段序列化，避免 datetime 等类型被 raw 塞进 dict 导致 JSON 序列化 500"""
    return {
        "id": i.id,
        "product_id": i.product_id,
        "product_name": i.product_name,
        "sku_code": i.sku_code,
        "warehouse_id": i.warehouse_id,
        "warehouse_name": i.warehouse_name,
        "quantity": i.quantity,
        "safety_stock": i.safety_stock,
        "locked_quantity": i.locked_quantity,
        "available_quantity": i.available_quantity,
        "status": i.status,
        "last_check_date": _serialize_dt(i.last_check_date),
        "created_at": _serialize_dt(i.created_at),
        "updated_at": _serialize_dt(i.updated_at),
    }


@router.get("")
async def list_inventory(page: int = 1, size: int = 20, keyword: str | None = None,
                         db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    query = select(Inventory)
    if keyword:
        query = query.where(Inventory.product_name.ilike(f"%{keyword}%"))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(Inventory.updated_at.desc()).offset((page - 1) * size).limit(size)
    items = (await db.execute(query)).scalars().all()
    return ApiResponse.ok(PageResult(
        records=[_inv_to_dict(i) for i in items],
        total=total, page=page, size=size,
        total_pages=(total + size - 1) // size if size else 0,
    ))


@router.get("/alerts")
async def alerts(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    r = await db.execute(select(Inventory).where(Inventory.status == "LOW"))
    return ApiResponse.ok([_inv_to_dict(i) for i in r.scalars().all()])


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    total = (await db.execute(select(func.count()).select_from(Inventory))).scalar() or 0
    low = (await db.execute(select(func.count()).where(Inventory.status == "LOW"))).scalar() or 0
    out = (await db.execute(select(func.count()).where(Inventory.status == "OUT_OF_STOCK"))).scalar() or 0
    return ApiResponse.ok({"total": total, "low_stock_count": low, "out_of_stock_count": out})


@router.get("/{inv_id}")
async def get_inventory(inv_id: int, db: AsyncSession = Depends(get_db),
                        _: User = Depends(get_current_user)):
    r = await db.execute(select(Inventory).where(Inventory.id == inv_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="不存在")
    return ApiResponse.ok(_inv_to_dict(item))


@router.post("")
async def create_inventory(data: dict, db: AsyncSession = Depends(get_db),
                           _: User = Depends(get_current_user)):
    qty = data.get("quantity", 0)
    safety = data.get("safety_stock", int(qty * 0.3))
    locked = data.get("locked_quantity", 0)
    inv = Inventory(
        product_name=data.get("product_name"), sku_code=data.get("sku_code"),
        warehouse_name=data.get("warehouse_name"), quantity=qty,
        safety_stock=safety, locked_quantity=locked,
        available_quantity=qty - locked,
        status=_calc_status(qty - locked, safety),
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return ApiResponse.ok(_inv_to_dict(inv), message="创建成功")


@router.put("/{inv_id}")
async def update_inventory(inv_id: int, data: dict, db: AsyncSession = Depends(get_db),
                           _: User = Depends(get_current_user)):
    r = await db.execute(select(Inventory).where(Inventory.id == inv_id))
    inv = r.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="不存在")
    if "quantity" in data:
        inv.quantity = data["quantity"]
    if "safety_stock" in data:
        inv.safety_stock = data["safety_stock"]
    if "locked_quantity" in data:
        inv.locked_quantity = data["locked_quantity"]
    inv.available_quantity = inv.quantity - inv.locked_quantity
    inv.status = _calc_status(inv.available_quantity, inv.safety_stock)
    await db.commit()
    await db.refresh(inv)
    return ApiResponse.ok(_inv_to_dict(inv), message="更新成功")


@router.post("/{inv_id}/stock-in")
async def stock_in(inv_id: int, data: dict, db: AsyncSession = Depends(get_db),
                   _: User = Depends(get_current_user)):
    r = await db.execute(select(Inventory).where(Inventory.id == inv_id))
    inv = r.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="不存在")
    qty = data.get("quantity", 0)
    inv.quantity += qty
    inv.available_quantity = inv.quantity - inv.locked_quantity
    inv.status = _calc_status(inv.available_quantity, inv.safety_stock)
    await db.commit()
    await db.refresh(inv)
    return ApiResponse.ok(_inv_to_dict(inv), message=f"入库{qty}件")


@router.post("/{inv_id}/stock-out")
async def stock_out(inv_id: int, data: dict, db: AsyncSession = Depends(get_db),
                    _: User = Depends(get_current_user)):
    r = await db.execute(select(Inventory).where(Inventory.id == inv_id))
    inv = r.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="不存在")
    qty = data.get("quantity", 0)
    if inv.available_quantity < qty:
        raise HTTPException(status_code=400, detail=f"库存不足，当前可用: {inv.available_quantity}")
    inv.quantity -= qty
    inv.available_quantity = inv.quantity - inv.locked_quantity
    inv.status = _calc_status(inv.available_quantity, inv.safety_stock)
    await db.commit()
    await db.refresh(inv)
    return ApiResponse.ok(_inv_to_dict(inv), message=f"出库{qty}件")


def _calc_status(available: int, safety: int) -> str:
    if available <= 0:
        return "OUT_OF_STOCK"
    if available <= safety:
        return "LOW"
    if available > safety * 3:
        return "OVERSTOCK"
    return "NORMAL"
