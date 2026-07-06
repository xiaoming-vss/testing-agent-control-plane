from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.api_environment import ApiEnvironment
from testing_agent.models.project import Project


class ApiEnvironmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def get_environment(self, environment_id: str) -> ApiEnvironment | None:
        return await self.session.scalar(
            select(ApiEnvironment).where(
                ApiEnvironment.environment_id == environment_id,
                ApiEnvironment.deleted_at.is_(None),
            )
        )

    async def list_by_project(self, project_id: str) -> list[ApiEnvironment]:
        return list(
            (
                await self.session.scalars(
                    select(ApiEnvironment)
                    .where(
                        ApiEnvironment.project_id == project_id,
                        ApiEnvironment.deleted_at.is_(None),
                    )
                    .order_by(ApiEnvironment.created_at.desc())
                )
            ).all()
        )

    def add(self, environment: ApiEnvironment) -> None:
        self.session.add(environment)

    def soft_delete(self, environment: ApiEnvironment, deleted_at: datetime) -> None:
        environment.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, environment: ApiEnvironment) -> None:
        await self.session.refresh(environment)

