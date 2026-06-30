"""
LangGraph 业务工具定义
使用 LangChain @tool 装饰器封装业务操作
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.core.logger import logger
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.supplier import Supplier


def _calc_status(available: int, safety: int) -> str:
    """计算库存状态"""
    if available <= 0:
        return "OUT_OF_STOCK"
    if available <= safety:
        return "LOW"
    if available > safety * 3:
        return "OVERSTOCK"
    return "NORMAL"


@tool
async def query_inventory(
    product_name: Optional[str] = None,
    warehouse_name: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """
    查询库存信息列表
    
    Args:
        product_name: 商品名称（模糊匹配，可为空）
        warehouse_name: 仓库名称（模糊匹配，可为空）
        status: 库存状态筛选（NORMAL/LOW/OVERSTOCK/OUT_OF_STOCK，可为空）
    
    Returns:
        包含库存列表的字典
    """
    async with async_session_factory() as session:
        query = select(Inventory)
        conditions = []
        if product_name:
            conditions.append(Inventory.product_name.ilike(f"%{product_name}%"))
        if warehouse_name:
            conditions.append(Inventory.warehouse_name.ilike(f"%{warehouse_name}%"))
        if status:
            conditions.append(Inventory.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await session.execute(query.order_by(Inventory.updated_at.desc()))
        items = result.scalars().all()
        
        data = [{
            "id": i.id,
            "product_name": i.product_name,
            "sku_code": i.sku_code,
            "warehouse_name": i.warehouse_name,
            "quantity": i.quantity,
            "safety_stock": i.safety_stock,
            "available_quantity": i.available_quantity,
            "locked_quantity": i.locked_quantity,
            "status": i.status,
        } for i in items]
        
        logger.info(f"[query_inventory] 查询完成，条件: product={product_name}, warehouse={warehouse_name}, status={status}, 找到 {len(data)} 条记录")
        
        return {
            "success": True,
            "data": data,
            "message": f"查询成功，找到 {len(data)} 条库存记录" if data else "未找到匹配的库存记录",
            "total": len(data),
        }


@tool
async def query_low_stock() -> Dict:
    """
    查询低库存商品列表（可用库存低于或等于安全库存的商品）
    
    Returns:
        包含低库存商品列表的字典
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(Inventory).where(
                and_(
                    Inventory.safety_stock > 0,
                    Inventory.available_quantity <= Inventory.safety_stock
                )
            ).order_by(Inventory.available_quantity.asc())
        )
        items = result.scalars().all()
        
        data = [{
            "id": i.id,
            "product_name": i.product_name,
            "sku_code": i.sku_code,
            "warehouse_name": i.warehouse_name,
            "available_quantity": i.available_quantity,
            "safety_stock": i.safety_stock,
            "shortage": max(0, i.safety_stock - i.available_quantity),
            "status": i.status,
        } for i in items]
        
        logger.info(f"[query_low_stock] 查询完成，找到 {len(data)} 条低库存商品")
        
        return {
            "success": True,
            "data": data,
            "message": f"查询成功，找到 {len(data)} 条低库存商品" if data else "当前暂无低于安全库存的商品",
            "total": len(data),
        }


@tool
async def query_inventory_stats() -> Dict:
    """
    查询库存统计信息，包括总商品数、低库存数量、缺货数量等
    
    Returns:
        包含库存统计信息的字典
    """
    async with async_session_factory() as session:
        total = (await session.execute(select(func.count(Inventory.id)))).scalar() or 0
        low_count = (await session.execute(
            select(func.count(Inventory.id)).where(
                and_(
                    Inventory.safety_stock > 0,
                    Inventory.available_quantity <= Inventory.safety_stock
                )
            )
        )).scalar() or 0
        out_count = (await session.execute(
            select(func.count(Inventory.id)).where(Inventory.available_quantity <= 0)
        )).scalar() or 0
        overstock_count = (await session.execute(
            select(func.count(Inventory.id)).where(Inventory.status == "OVERSTOCK")
        )).scalar() or 0
        
        stats = {
            "total": total,
            "low_stock_count": low_count,
            "out_of_stock_count": out_count,
            "overstock_count": overstock_count,
        }
        
        logger.info(f"[query_inventory_stats] 统计结果: {stats}")
        
        return {
            "success": True,
            "data": stats,
            "message": f"库存统计：总计 {total} 种商品，其中低库存 {low_count} 种，缺货 {out_count} 种",
            "total": total,
        }


@tool
async def query_orders(
    status: Optional[str] = None,
    customer_name: Optional[str] = None,
    keyword: Optional[str] = None
) -> Dict:
    """
    查询订单信息列表
    
    Args:
        status: 订单状态筛选（PENDING/SHIPPED/DELIVERED/CANCELLED，可为空）
        customer_name: 客户名称（模糊匹配，可为空）
        keyword: 关键词搜索（可搜索订单号、客户名、商品名，可为空）
    
    Returns:
        包含订单列表的字典
    """
    async with async_session_factory() as session:
        query = select(Order)
        conditions = []
        if status:
            conditions.append(Order.status == status)
        if customer_name:
            conditions.append(Order.customer_name.ilike(f"%{customer_name}%"))
        if keyword:
            conditions.append(
                or_(
                    Order.order_no.ilike(f"%{keyword}%"),
                    Order.customer_name.ilike(f"%{keyword}%"),
                    Order.product_name.ilike(f"%{keyword}%")
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await session.execute(query.order_by(Order.created_at.desc()))
        items = result.scalars().all()
        
        data = [{
            "id": i.id,
            "order_no": i.order_no,
            "customer_name": i.customer_name,
            "product_name": i.product_name,
            "quantity": i.quantity,
            "unit_price": float(i.unit_price) if i.unit_price else None,
            "total_amount": float(i.total_amount) if i.total_amount else None,
            "warehouse_name": i.warehouse_name,
            "status": i.status,
            "created_at": str(i.created_at) if i.created_at else None,
        } for i in items]
        
        logger.info(f"[query_orders] 查询完成，条件: status={status}, keyword={keyword}, 找到 {len(data)} 条记录")
        
        return {
            "success": True,
            "data": data,
            "message": f"查询成功，找到 {len(data)} 条订单记录" if data else "未找到匹配的订单记录",
            "total": len(data),
        }


@tool
async def query_order_stats() -> Dict:
    """
    查询订单统计信息，包括各状态的订单数量
    
    Returns:
        包含订单统计信息的字典
    """
    async with async_session_factory() as session:
        total = (await session.execute(select(func.count(Order.id)))).scalar() or 0
        pending = (await session.execute(select(func.count(Order.id)).where(Order.status == "PENDING"))).scalar() or 0
        shipped = (await session.execute(select(func.count(Order.id)).where(Order.status == "SHIPPED"))).scalar() or 0
        delivered = (await session.execute(select(func.count(Order.id)).where(Order.status == "DELIVERED"))).scalar() or 0
        cancelled = (await session.execute(select(func.count(Order.id)).where(Order.status == "CANCELLED"))).scalar() or 0
        
        stats = {
            "total": total,
            "pending": pending,
            "shipped": shipped,
            "delivered": delivered,
            "cancelled": cancelled,
        }
        
        logger.info(f"[query_order_stats] 统计结果: {stats}")
        
        return {
            "success": True,
            "data": stats,
            "message": f"订单统计：总计 {total} 单，其中待处理 {pending} 单，已发货 {shipped} 单，已送达 {delivered} 单，已取消 {cancelled} 单",
            "total": total,
        }


@tool
async def query_suppliers(
    keyword: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """
    查询供应商信息列表
    
    Args:
        keyword: 供应商名称或联系人（模糊匹配，可为空）
        status: 供应商状态（ACTIVE/INACTIVE，可为空）
    
    Returns:
        包含供应商列表的字典
    """
    async with async_session_factory() as session:
        query = select(Supplier)
        conditions = []
        if keyword:
            conditions.append(
                or_(
                    Supplier.name.ilike(f"%{keyword}%"),
                    Supplier.contact_name.ilike(f"%{keyword}%")
                )
            )
        if status:
            conditions.append(Supplier.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await session.execute(query.order_by(Supplier.rating.desc()))
        items = result.scalars().all()
        
        data = [{
            "id": i.id,
            "name": i.name,
            "code": i.code,
            "contact_name": i.contact_name,
            "contact_phone": i.contact_phone,
            "contact_email": i.contact_email,
            "address": i.address,
            "rating": i.rating,
            "status": i.status,
        } for i in items]
        
        logger.info(f"[query_suppliers] 查询完成，keyword={keyword}, 找到 {len(data)} 条记录")
        
        return {
            "success": True,
            "data": data,
            "message": f"查询成功，找到 {len(data)} 条供应商记录" if data else "未找到匹配的供应商记录",
            "total": len(data),
        }


@tool
async def stock_in_operation(inv_id: int, quantity: int) -> Dict:
    """
    执行库存入库操作
    
    Args:
        inv_id: 库存记录ID
        quantity: 入库数量（正整数）
    
    Returns:
        操作结果和更新后的库存信息
    """
    if quantity <= 0:
        return {"success": False, "message": "入库数量必须大于0"}
    
    async with async_session_factory() as session:
        result = await session.execute(select(Inventory).where(Inventory.id == inv_id))
        inv = result.scalar_one_or_none()
        
        if not inv:
            logger.warning(f"[stock_in_operation] 库存记录不存在，inv_id={inv_id}")
            return {"success": False, "message": "库存记录不存在"}
        
        old_qty = inv.quantity
        old_status = inv.status
        
        inv.quantity += quantity
        inv.available_quantity = inv.quantity - inv.locked_quantity
        inv.status = _calc_status(inv.available_quantity, inv.safety_stock)
        
        await session.commit()
        await session.refresh(inv)
        
        logger.info(f"[stock_in_operation] 入库成功，inv_id={inv_id}, 旧数量={old_qty}, 新数量={inv.quantity}, 旧状态={old_status}, 新状态={inv.status}")
        
        return {
            "success": True,
            "message": f"成功入库 {quantity} 件，{inv.product_name}（{inv.sku_code}）当前库存：{inv.quantity} 件",
            "data": {
                "id": inv.id,
                "product_name": inv.product_name,
                "sku_code": inv.sku_code,
                "warehouse_name": inv.warehouse_name,
                "quantity": inv.quantity,
                "available_quantity": inv.available_quantity,
                "status": inv.status,
            }
        }


@tool
async def stock_out_operation(inv_id: int, quantity: int) -> Dict:
    """
    执行库存出库操作
    
    Args:
        inv_id: 库存记录ID
        quantity: 出库数量（正整数）
    
    Returns:
        操作结果和更新后的库存信息
    """
    if quantity <= 0:
        return {"success": False, "message": "出库数量必须大于0"}
    
    async with async_session_factory() as session:
        result = await session.execute(select(Inventory).where(Inventory.id == inv_id))
        inv = result.scalar_one_or_none()
        
        if not inv:
            logger.warning(f"[stock_out_operation] 库存记录不存在，inv_id={inv_id}")
            return {"success": False, "message": "库存记录不存在"}
        
        if inv.available_quantity < quantity:
            logger.warning(f"[stock_out_operation] 库存不足，inv_id={inv_id}, 可用={inv.available_quantity}, 请求={quantity}")
            return {"success": False, "message": f"库存不足，当前可用库存：{inv.available_quantity} 件"}
        
        old_qty = inv.quantity
        old_status = inv.status
        
        inv.quantity -= quantity
        inv.available_quantity = inv.quantity - inv.locked_quantity
        inv.status = _calc_status(inv.available_quantity, inv.safety_stock)
        
        await session.commit()
        await session.refresh(inv)
        
        logger.info(f"[stock_out_operation] 出库成功，inv_id={inv_id}, 旧数量={old_qty}, 新数量={inv.quantity}, 旧状态={old_status}, 新状态={inv.status}")
        
        return {
            "success": True,
            "message": f"成功出库 {quantity} 件，{inv.product_name}（{inv.sku_code}）当前库存：{inv.quantity} 件",
            "data": {
                "id": inv.id,
                "product_name": inv.product_name,
                "sku_code": inv.sku_code,
                "warehouse_name": inv.warehouse_name,
                "quantity": inv.quantity,
                "available_quantity": inv.available_quantity,
                "status": inv.status,
            }
        }


@tool
async def create_order_operation(
    customer_name: str,
    product_name: str,
    quantity: int,
    warehouse_name: str,
    shipping_address: str,
    unit_price: Optional[float] = None,
    remark: Optional[str] = None
) -> Dict:
    """
    创建新订单
    
    Args:
        customer_name: 客户名称
        product_name: 商品名称
        quantity: 订购数量
        warehouse_name: 仓库名称
        shipping_address: 收货地址
        unit_price: 单价（可选）
        remark: 备注（可选）
    
    Returns:
        创建结果和新订单信息
    """
    import datetime
    
    if not customer_name or not product_name or quantity <= 0:
        return {"success": False, "message": "客户名称、商品名称和数量不能为空，且数量必须大于0"}
    
    async with async_session_factory() as session:
        from decimal import Decimal
        
        total_amount = None
        if unit_price and unit_price > 0:
            total_amount = Decimal(str(unit_price * quantity))
        
        order = Order(
            order_no=f"SO{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            customer_name=customer_name,
            product_name=product_name,
            quantity=quantity,
            unit_price=Decimal(str(unit_price)) if unit_price else None,
            total_amount=total_amount,
            warehouse_name=warehouse_name,
            shipping_address=shipping_address,
            remark=remark,
            status="PENDING",
        )
        
        session.add(order)
        await session.flush()
        await session.refresh(order)
        await session.commit()
        
        logger.info(f"[create_order_operation] 订单创建成功，order_no={order.order_no}")
        
        return {
            "success": True,
            "message": f"订单创建成功，订单号：{order.order_no}",
            "data": {
                "id": order.id,
                "order_no": order.order_no,
                "customer_name": order.customer_name,
                "product_name": order.product_name,
                "quantity": order.quantity,
                "unit_price": float(order.unit_price) if order.unit_price else None,
                "total_amount": float(order.total_amount) if order.total_amount else None,
                "warehouse_name": order.warehouse_name,
                "status": order.status,
            }
        }


@tool
async def update_order_status_operation(order_id: int, new_status: str) -> Dict:
    """
    更新订单状态
    
    Args:
        order_id: 订单ID
        new_status: 新状态（PENDING/SHIPPED/DELIVERED/CANCELLED）
    
    Returns:
        更新结果和订单信息
    """
    import datetime
    
    valid_statuses = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
    if new_status not in valid_statuses:
        return {"success": False, "message": f"无效的订单状态，可选状态：{', '.join(valid_statuses)}"}
    
    async with async_session_factory() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            logger.warning(f"[update_order_status_operation] 订单不存在，order_id={order_id}")
            return {"success": False, "message": "订单不存在"}
        
        old_status = order.status
        order.status = new_status
        
        if new_status == "SHIPPED":
            order.shipped_date = datetime.datetime.now(datetime.timezone.utc)
        elif new_status == "DELIVERED":
            order.delivered_date = datetime.datetime.now(datetime.timezone.utc)
        
        await session.commit()
        await session.refresh(order)
        
        logger.info(f"[update_order_status_operation] 订单状态更新成功，order_id={order_id}, {old_status} -> {new_status}")
        
        return {
            "success": True,
            "message": f"订单状态已更新：{old_status} → {new_status}",
            "data": {
                "id": order.id,
                "order_no": order.order_no,
                "status": order.status,
            }
        }


@tool
async def cancel_order_operation(order_id: int) -> Dict:
    """
    取消订单
    
    Args:
        order_id: 订单ID
    
    Returns:
        操作结果
    """
    async with async_session_factory() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            logger.warning(f"[cancel_order_operation] 订单不存在，order_id={order_id}")
            return {"success": False, "message": "订单不存在"}
        
        if order.status not in ("PENDING", "CONFIRMED"):
            return {"success": False, "message": f"当前状态（{order.status}）不允许取消，仅待处理和已确认状态的订单可以取消"}
        
        old_status = order.status
        order.status = "CANCELLED"
        
        await session.commit()
        
        logger.info(f"[cancel_order_operation] 订单已取消，order_id={order_id}, {old_status} -> CANCELLED")
        
        return {
            "success": True,
            "message": f"订单 {order.order_no} 已成功取消",
        }


def get_all_tools() -> List:
    """获取所有业务工具列表"""
    return [
        query_inventory,
        query_low_stock,
        query_inventory_stats,
        query_orders,
        query_order_stats,
        query_suppliers,
        stock_in_operation,
        stock_out_operation,
        create_order_operation,
        update_order_status_operation,
        cancel_order_operation,
    ]
