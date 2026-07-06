from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.sprint import Sprint


class FunctionTestSuiteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_requirement(self, requirement_id: str) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.requirement_id == requirement_id,
                Requirement.deleted_at.is_(None),
            )
        )

    async def get_sprint(self, sprint_id: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.sprint_id == sprint_id, Sprint.deleted_at.is_(None))
        )

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def get_suite(self, suite_id: str) -> FunctionTestSuite | None:
        return await self.session.scalar(
            select(FunctionTestSuite).where(
                FunctionTestSuite.suite_id == suite_id,
                FunctionTestSuite.deleted_at.is_(None),
            )
        )

    async def list_by_requirement(self, requirement_id: str) -> list[FunctionTestSuite]:
        return list(
            (
                await self.session.scalars(
                    select(FunctionTestSuite)
                    .where(
                        FunctionTestSuite.requirement_id == requirement_id,
                        FunctionTestSuite.deleted_at.is_(None),
                    )
                    .order_by(FunctionTestSuite.created_at.desc())
                )
            ).all()
        )

    def add(self, suite: FunctionTestSuite) -> None:
        self.session.add(suite)

    def soft_delete(self, suite: FunctionTestSuite, deleted_at: datetime) -> None:
        suite.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, suite: FunctionTestSuite) -> None:
        await self.session.refresh(suite)

