from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.function_test_case import FunctionTestCase
from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.resource_binding import ResourceBinding
from testing_agent.models.sprint import Sprint


class FunctionTestCaseRepository:
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

    async def get_case(self, case_id: str) -> FunctionTestCase | None:
        return await self.session.scalar(
            select(FunctionTestCase).where(
                FunctionTestCase.case_id == case_id,
                FunctionTestCase.deleted_at.is_(None),
            )
        )

    async def list_by_suite(self, suite_id: str) -> list[FunctionTestCase]:
        return list(
            (
                await self.session.scalars(
                    select(FunctionTestCase)
                    .where(
                        FunctionTestCase.suite_id == suite_id,
                        FunctionTestCase.deleted_at.is_(None),
                    )
                    .order_by(FunctionTestCase.order_no)
                )
            ).all()
        )

    async def get_active_binding(
        self,
        resource_type: str,
        resource_id: str,
    ) -> ResourceBinding | None:
        return await self.session.scalar(
            select(ResourceBinding)
            .where(
                ResourceBinding.local_resource_type == resource_type,
                ResourceBinding.local_resource_id == resource_id,
                ResourceBinding.status == "active",
                ResourceBinding.deleted_at.is_(None),
            )
            .order_by(ResourceBinding.id.asc())
            .limit(1)
        )

    def add(self, case: FunctionTestCase) -> None:
        self.session.add(case)

    def soft_delete(self, case: FunctionTestCase, deleted_at: datetime) -> None:
        case.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, case: FunctionTestCase) -> None:
        await self.session.refresh(case)
