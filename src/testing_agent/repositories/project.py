from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_by_id(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def get_active_by_user_and_name(self, user_id: str, name: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(
                Project.user_id == user_id,
                Project.name == name,
                Project.deleted_at.is_(None),
            )
        )

    async def list_active_by_user(self, user_id: str) -> list[Project]:
        return list(
            (
                await self.session.scalars(
                    select(Project)
                    .where(Project.user_id == user_id, Project.deleted_at.is_(None))
                    .order_by(Project.created_at.desc())
                )
            ).all()
        )

    def add(self, project: Project) -> None:
        self.session.add(project)

    def soft_delete(self, project: Project, deleted_at: datetime) -> None:
        project.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, project: Project) -> None:
        await self.session.refresh(project)
