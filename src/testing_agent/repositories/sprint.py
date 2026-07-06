from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.sprint import Sprint


class SprintRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_by_id(self, sprint_id: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.sprint_id == sprint_id, Sprint.deleted_at.is_(None))
        )

    async def get_active_by_project_and_name(self, project_id: str, name: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(
                Sprint.project_id == project_id,
                Sprint.name == name,
                Sprint.deleted_at.is_(None),
            )
        )

    async def list_active_by_project(self, project_id: str) -> list[Sprint]:
        return list(
            (
                await self.session.scalars(
                    select(Sprint)
                    .where(Sprint.project_id == project_id, Sprint.deleted_at.is_(None))
                    .order_by(Sprint.created_at.desc())
                )
            ).all()
        )

    def add(self, sprint: Sprint) -> None:
        self.session.add(sprint)

    def soft_delete(self, sprint: Sprint, deleted_at: datetime) -> None:
        sprint.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, sprint: Sprint) -> None:
        await self.session.refresh(sprint)
