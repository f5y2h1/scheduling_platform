"""
LangGraph 业务工具定义
使用 LangChain @tool 装饰器封装业务操作
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.supplier import Supplier


@tool
async def query_inventory(product_name: Optional[str] = None, warehouse_name: Optional[str] = None) -> List[Dict]:
    """
    查询库存信息
    
    Args:
        product_name: 商品名称（模糊匹配）
        warehouse_name: 仓库名称（模糊匹配）
    
    Returns:
        库存列表，包含商品名称、SKU、仓库、库存数量、安全库存、可用库存、状态
    """
    async with async_session_factory() as session:
        query = select(Inventory)
        if product_name:
            query = query.where(Inventory.product_name.ilike(f"%{product_name}%"))
        if warehouse_name:
            query = query.where(Inventory.warehouse_name.ilike(f"%{warehouse_name}%"))
        
        result = await session.execute(query)
        items = result.scalars().all()
        
        return [{
            "product_name": i.product_name,
            "sku_code": i.sku_code,
            "warehouse_name": i.warehouse_name,
            "quantity": i.quantity,
            "safety_stock": i.safety_stock,
            "available_quantity": i.available_quantity,
            "status": i.status,
        } for i in items]


@tool
async def query_low_stock() -> List[Dict]:
    """
    查询低库存商品列表
    
    Returns:
        低库存商品列表
    """
    async with async_session_factory() as session:
        result = await session.execute(select(Inventory).where(Inventory.status == "LOW"))
        items = result.scalars().all()
        
        return [{
            "product_name": i.product_name,
            "sku_code": i.sku_code,
            "warehouse_name": i.warehouse_name,
            "available_quantity": i.available_quantity,
            "safety_stock": i.safety_stock,
        } for i in items]


@tool
async def query_orders(status: Optional[str] = None) -> List[Dict]:
    """
    查询订单信息
    
    Args:
        status: 订单状态（PENDING/SHIPPED/DELIVERED/CANCELLED）
    
    Returns:
        订单列表
    """
    async with async_session_factory() as session:
        query = select(Order)
        if status:
            query = query.where(Order.status == status)
        
        result = await session.execute(query)
        items = result.scalars().all()
        
        return [{
            "id": i.id,
            "order_no": i.order_no,
            "customer_name": i.customer_name,
            "product_name": i.product_name,
            "quantity": i.quantity,
            "status": i.status,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        } for i in items]


@tool
async def query_suppliers(keyword: Optional[str] = None) -> List[Dict]:
    """
    查询供应商信息
    
    Args:
        keyword: 供应商名称或联系人（模糊匹配）
    
    Returns:
        供应商列表
    """
    async with async_session_factory() as session:
        query = select(Supplier)
        if keyword:
            query = query.where(
                Supplier.name.ilike(f"%{keyword}%") | 
                Supplier.contact_person.ilike(f"%{keyword}%")
            )
        
        result = await session.execute(query)
        items = result.scalars().all()
        
        return [{
            "name": i.name,
            "contact_person": i.contact_person,
            "contact_phone": i.contact_phone,
            "email": i.email,
            "location": i.location,
            "rating": i.rating,
            "status": i.status,
        } for i in items]


@tool
async def stock_in_operation(inv_id: int, quantity: int) -> Dict:
    """
    执行入库操作
    
    Args:
        inv_id: 库存记录ID
        quantity: 入库数量
    
    Returns:
        操作结果和更新后的库存信息
    """
    async with async_session_factory() as session:
        result = await session.execute(select(Inventory).where(Inventory.id == inv_id))
        inv = result.scalar_one_or_none()
        
        if not inv:
            return {"success": False, "message": "库存记录不存在"}
        
        inv.quantity += quantity
        inv.available_quantity = inv.quantity - inv.locked_quantity
        
        if inv.available_quantity <= 0:
            inv.status = "OUT_OF_STOCK"
        elif inv.available_quantity <= inv.safety_stock:
            inv.status = "LOW"
        elif inv.available_quantity > inv.safety_stock * 3:
            inv.status = "OVERSTOCK"
        else:
            inv.status = "NORMAL"
        
        await session.commit()
        await session.refresh(inv)
        
        return {
            "success": True,
            "message": f"成功入库 {quantity} 件",
            "inventory": {
                "product_name": inv.product_name,
                "warehouse_name": inv.warehouse_name,
                "quantity": inv.quantity,
                "available_quantity": inv.available_quantity,
                "status": inv.status,
            }
        }


@tool
async def stock_out_operation(inv_id: int, quantity: int) -> Dict:
    """
    执行出库操作
    
    Args:
        inv_id: 库存记录ID
        quantity: 出库数量
    
    Returns:
        操作结果和更新后的库存信息
    """
    async with async_session_factory() as session:
        result = await session.execute(select(Inventory).where(Inventory.id == inv_id))
        inv = result.scalar_one_or_none()
        
        if not inv:
            return {"success": False, "message": "库存记录不存在"}
        
        if inv.available_quantity < quantity:
            return {"success": False, "message": f"库存不足，当前可用: {inv.available_quantity}"}
        
        inv.quantity -= quantity
        inv.available_quantity = inv.quantity - inv.locked_quantity
        
        if inv.available_quantity <= 0:
            inv.status = "OUT_OF_STOCK"
        elif inv.available_quantity <= inv.safety_stock:
            inv.status = "LOW"
        elif inv.available_quantity > inv.safety_stock * 3:
            inv.status = "OVERSTOCK"
        else:
            inv.status = "NORMAL"
        
        await session.commit()
        await session.refresh(inv)
        
        return {
            "success": True,
            "message": f"成功出库 {quantity} 件",
            "inventory": {
                "product_name": inv.product_name,
                "warehouse_name": inv.warehouse_name,
                "quantity": inv.quantity,
                "available_quantity": inv.available_quantity,
                "status": inv.status,
            }
        }


def get_all_tools() -> List:
    """获取所有业务工具列表"""
    return [
        query_inventory,
        query_low_stock,
        query_orders,
        query_suppliers,
        stock_in_operation,
        stock_out_operation,
    ]
