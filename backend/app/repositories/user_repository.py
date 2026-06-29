"""
用户 Repository
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_by(username=username)

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.list(skip=skip, limit=limit, status=1)

    async def count_by_role(self, role: str) -> int:
        return await self.count(role=role)

    async def search(self, keyword: str, skip: int = 0, limit: int = 100) -> list[User]:
        query = (
            select(User)
            .where(
                (User.username.ilike(f"%{keyword}%"))
                | (User.real_name.ilike(f"%{keyword}%"))
                | (User.email.ilike(f"%{keyword}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()