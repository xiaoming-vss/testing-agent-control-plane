from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> User | None:
        return await self.session.scalar(select(User).where(User.nickname == name))

    async def get_by_user_id(self, user_id: str) -> User | None:
        return await self.session.scalar(select(User).where(User.user_id == user_id))

    def add(self, user: User) -> None:
        self.session.add(user)

    async def delete(self, user: User) -> None:
        await self.session.delete(user)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, user: User) -> None:
        await self.session.refresh(user)
