"""
调度任务 Repository
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule_task import ScheduleTask
from app.repositories.base_repository import BaseRepository


class ScheduleTaskRepository(BaseRepository[ScheduleTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(ScheduleTask, db)

    async def get_by_task_no(self, task_no: str) -> ScheduleTask | None:
        return await self.get_by(task_no=task_no)

    async def get_by_order_no(self, order_no: str) -> list[ScheduleTask]:
        query = select(ScheduleTask).where(ScheduleTask.order_no == order_no)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> list[ScheduleTask]:
        return await self.list(skip=skip, limit=limit, status=status)