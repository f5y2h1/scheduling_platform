"""调度中心 API"""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schedule_task import ScheduleTask
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.utils.auth import get_current_user

router = APIRouter()


def _task_to_dict(t: ScheduleTask) -> dict:
    return {
        "id": t.id, "task_no": t.task_no, "task_type": t.task_type,
        "status": t.status, "order_no": t.order_no,
        "from_warehouse_name": t.from_warehouse_name,
        "to_warehouse_name": t.to_warehouse_name,
        "product_name": t.product_name, "quantity": t.quantity,
        "ai_suggestion": t.ai_suggestion, "ai_model_used": t.ai_model_used,
        "approved_by": t.approved_by,
        "approved_at": str(t.approved_at) if t.approved_at else None,
        "remark": t.remark,
        "created_at": str(t.created_at) if t.created_at else None,
        "updated_at": str(t.updated_at) if t.updated_at else None,
    }


@router.get("")
async def list_tasks(page: int = 1, size: int = 20, status: str | None = None,
                     db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    query = select(ScheduleTask)
    if status:
        query = query.where(ScheduleTask.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(ScheduleTask.created_at.desc()).offset((page - 1) * size).limit(size)
    tasks = (await db.execute(query)).scalars().all()
    return ApiResponse.ok(PageResult(
        records=[_task_to_dict(t) for t in tasks], total=total, page=page, size=size,
        total_pages=(total + size - 1) // size if size else 0,
    ))


@router.get("/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db),
                   _: User = Depends(get_current_user)):
    r = await db.execute(select(ScheduleTask).where(ScheduleTask.id == task_id))
    t = r.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="不存在")
    return ApiResponse.ok(_task_to_dict(t))


@router.post("")
async def create_task(data: dict, db: AsyncSession = Depends(get_db),
                      _: User = Depends(get_current_user)):
    task = ScheduleTask(
        task_no=f"ST{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        task_type=data.get("task_type", "DISPATCH"),
        order_no=data.get("order_no"),
        from_warehouse_name=data.get("from_warehouse_name"),
        to_warehouse_name=data.get("to_warehouse_name"),
        product_name=data.get("product_name"),
        quantity=data.get("quantity", 1),
        remark=data.get("remark"),
        status="PENDING",
    )
    db.add(task)
    await db.flush()
    return ApiResponse.ok(_task_to_dict(task), message="创建成功")


@router.post("/{task_id}/ai-suggest")
async def ai_suggest(task_id: int, data: dict, db: AsyncSession = Depends(get_db),
                     _: User = Depends(get_current_user)):
    r = await db.execute(select(ScheduleTask).where(ScheduleTask.id == task_id))
    task = r.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="不存在")

    from app.services.ai.agent_orchestrator import orchestrator
    query = f"订单{task.order_no}需要从{task.from_warehouse_name}调度{task.product_name}{task.quantity}件到{task.to_warehouse_name}，请给出调度方案建议。"
    result = await orchestrator.invoke_agent("scheduling_decision", data.get("model"), query)

    task.ai_suggestion = str(result.get("result", ""))
    task.ai_model_used = data.get("model") or "default"
    task.status = "AI_SUGGESTED"
    await db.flush()
    return ApiResponse.ok(_task_to_dict(task), message="AI方案已生成")


@router.post("/{task_id}/approve")
async def approve(task_id: int, data: dict, db: AsyncSession = Depends(get_db),
                  _: User = Depends(get_current_user)):
    r = await db.execute(select(ScheduleTask).where(ScheduleTask.id == task_id))
    task = r.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="不存在")
    approved = data.get("approved", True)
    task.status = "APPROVED" if approved else "REJECTED"
    task.approved_by = data.get("username", "admin")
    task.approved_at = datetime.datetime.now(datetime.timezone.utc)
    await db.flush()
    return ApiResponse.ok(_task_to_dict(task), message="已审批")


@router.post("/{task_id}/execute")
async def execute(task_id: int, db: AsyncSession = Depends(get_db),
                  _: User = Depends(get_current_user)):
    r = await db.execute(select(ScheduleTask).where(ScheduleTask.id == task_id))
    task = r.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="不存在")
    if task.status != "APPROVED":
        raise HTTPException(status_code=400, detail="只有已审批任务可执行")
    task.status = "EXECUTING"
    await db.flush()
    return ApiResponse.ok(_task_to_dict(task), message="开始执行")


@router.post("/{task_id}/complete")
async def complete(task_id: int, db: AsyncSession = Depends(get_db),
                   _: User = Depends(get_current_user)):
    r = await db.execute(select(ScheduleTask).where(ScheduleTask.id == task_id))
    task = r.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="不存在")
    task.status = "COMPLETED"
    await db.flush()
    return ApiResponse.ok(_task_to_dict(task), message="已完成")
