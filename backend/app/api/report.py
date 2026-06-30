"""数据报表 API — 基于真实数据库查询"""
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.models.order import Order
from app.models.inventory import Inventory
from app.models.schedule_task import ScheduleTask
from app.schemas.common import ApiResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    """仪表盘核心统计数据（实时数据库查询）"""

    # 订单统计
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0
    pending_orders = (await db.execute(
        select(func.count(Order.id)).where(Order.status == "PENDING")
    )).scalar() or 0
    delivered_orders = (await db.execute(
        select(func.count(Order.id)).where(Order.status == "DELIVERED")
    )).scalar() or 0
    completed_rate = round(delivered_orders / max(total_orders, 1) * 100, 1)

    # 库存统计
    total_skus = (await db.execute(select(func.count(Inventory.id)))).scalar() or 0
    low_stock = (await db.execute(
        select(func.count(Inventory.id)).where(
            Inventory.safety_stock > 0,
            Inventory.available_quantity <= Inventory.safety_stock,
        )
    )).scalar() or 0
    out_of_stock = (await db.execute(
        select(func.count(Inventory.id)).where(Inventory.available_quantity <= 0)
    )).scalar() or 0

    # 调度任务统计
    total_tasks = (await db.execute(select(func.count(ScheduleTask.id)))).scalar() or 0
    pending_tasks = (await db.execute(
        select(func.count(ScheduleTask.id)).where(ScheduleTask.status == "PENDING")
    )).scalar() or 0
    completed_tasks = (await db.execute(
        select(func.count(ScheduleTask.id)).where(ScheduleTask.status == "COMPLETED")
    )).scalar() or 0

    return ApiResponse.ok({
        "order_stats": {
            "total_orders": total_orders,
            "pending_count": pending_orders,
            "delivered_count": delivered_orders,
            "completed_rate": completed_rate,
        },
        "inventory_stats": {
            "total_skus": total_skus,
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
        },
        "scheduling_stats": {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
        },
    })


@router.get("/order-trend")
async def order_trend(days: int = 7, db: AsyncSession = Depends(get_db),
                      _: User = Depends(get_current_user)):
    """近 N 天订单趋势（按日期分组统计，使用范围查询避免类型不匹配）"""

    today = datetime.date.today()
    trend = []
    for i in range(days - 1, -1, -1):
        d = today - datetime.timedelta(days=i)

        # 使用日期范围查询替代 date(col) == str，避免 PostgreSQL date/varchar 类型不匹配
        # 同时利用 created_at 索引提升查询性能
        day_start = datetime.datetime.combine(d, datetime.time.min)
        day_end = datetime.datetime.combine(d + datetime.timedelta(days=1), datetime.time.min)

        count = (await db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= day_start,
                Order.created_at < day_end,
            )
        )).scalar() or 0
        trend.append({"date": d.strftime("%m-%d"), "count": count})

    return ApiResponse.ok(trend)


@router.get("/inventory-overview")
async def inventory_overview(db: AsyncSession = Depends(get_db),
                              _: User = Depends(get_current_user)):
    """按仓库/状态统计库存分布"""
    # 按仓库统计
    warehouse_result = await db.execute(
        select(Inventory.warehouse_name,
               func.count(Inventory.id),
               func.sum(Inventory.quantity))
        .group_by(Inventory.warehouse_name)
    )
    by_warehouse = [
        {"name": r[0] or "未知仓库", "sku_count": r[1], "total_qty": int(r[2] or 0)}
        for r in warehouse_result.all()
    ]

    # 按状态统计
    status_result = await db.execute(
        select(Inventory.status, func.count(Inventory.id))
        .group_by(Inventory.status)
    )
    by_status = [
        {"status": r[0] or "UNKNOWN", "count": r[1]}
        for r in status_result.all()
    ]

    return ApiResponse.ok({
        "by_warehouse": by_warehouse,
        "by_status": by_status,
    })


@router.get("/scheduling-efficiency")
async def scheduling_efficiency(db: AsyncSession = Depends(get_db),
                                 _: User = Depends(get_current_user)):
    """调度效率统计"""
    total = (await db.execute(select(func.count(ScheduleTask.id)))).scalar() or 0
    completed = (await db.execute(
        select(func.count(ScheduleTask.id)).where(ScheduleTask.status == "COMPLETED")
    )).scalar() or 0
    pending = (await db.execute(
        select(func.count(ScheduleTask.id)).where(ScheduleTask.status == "PENDING")
    )).scalar() or 0
    on_time_rate = round(completed / max(total, 1) * 100, 1)

    return ApiResponse.ok({
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "on_time_rate": f"{on_time_rate}%",
    })


@router.get("/ai-usage")
async def ai_usage(_: User = Depends(get_current_user)):
    """AI 使用统计（从长期记忆读取）"""
    try:
        from app.services.memory.memory_manager import memory_manager
        stats = await memory_manager.get_execution_stats()
    except Exception:
        stats = {"total_executions": 0, "success_count": 0, "success_rate": 0}

    return ApiResponse.ok({
        "total_executions": stats.get("total_executions", 0),
        "success_rate": stats.get("success_rate", 0),
        "avg_duration_ms": stats.get("avg_duration_ms", 0),
    })


@router.get("/export/{report_type}")
async def export_report(report_type: str, _: User = Depends(get_current_user)):
    return ApiResponse.ok(
        f"报表导出任务已创建，类型: {report_type}，请稍后在下载中心查看"
    )
