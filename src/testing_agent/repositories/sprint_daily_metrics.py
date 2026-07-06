from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.project import Project
from testing_agent.models.sprint import Sprint
from testing_agent.models.sprint_daily_metrics import SprintDailyMetrics


class SprintDailyMetricsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_sprint(self, sprint_id: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.sprint_id == sprint_id, Sprint.deleted_at.is_(None))
        )

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def list(self, sprint_id: str) -> list[SprintDailyMetrics]:
        return list(
            (
                await self.session.scalars(
                    select(SprintDailyMetrics)
                    .where(SprintDailyMetrics.sprint_id == sprint_id)
                    .order_by(SprintDailyMetrics.snapshot_date.asc())
                )
            ).all()
        )

    async def get(self, sprint_id: str, snapshot_date: str) -> SprintDailyMetrics | None:
        return await self.session.scalar(
            select(SprintDailyMetrics).where(
                SprintDailyMetrics.sprint_id == sprint_id,
                SprintDailyMetrics.snapshot_date == snapshot_date,
            )
        )

    def add(self, metric: SprintDailyMetrics) -> None:
        self.session.add(metric)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, metric: SprintDailyMetrics) -> None:
        await self.session.refresh(metric)
