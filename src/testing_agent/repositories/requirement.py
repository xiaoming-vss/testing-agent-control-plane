from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.requirement import Requirement


class RequirementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_by_id(self, requirement_id: str) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.requirement_id == requirement_id,
                Requirement.deleted_at.is_(None),
            )
        )

    async def get_active_by_sprint_and_name(
        self, sprint_id: str, name: str
    ) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.sprint_id == sprint_id,
                Requirement.name == name,
                Requirement.deleted_at.is_(None),
            )
        )

    async def get_by_sprint_and_name_unscoped(
        self, sprint_id: str, name: str
    ) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.sprint_id == sprint_id,
                Requirement.name == name,
            )
        )

    async def list_active_by_sprint(self, sprint_id: str) -> list[Requirement]:
        return list(
            (
                await self.session.scalars(
                    select(Requirement)
                    .where(Requirement.sprint_id == sprint_id, Requirement.deleted_at.is_(None))
                    .order_by(Requirement.created_at.desc())
                )
            ).all()
        )

    def add(self, requirement: Requirement) -> None:
        self.session.add(requirement)

    def soft_delete(self, requirement: Requirement, deleted_at: datetime) -> None:
        requirement.deleted_at = deleted_at

    def restore(self, requirement: Requirement) -> None:
        requirement.deleted_at = None
        self.session.add(requirement)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, requirement: Requirement) -> None:
        await self.session.refresh(requirement)
