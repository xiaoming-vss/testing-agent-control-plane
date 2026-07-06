from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.sprint import Sprint
from testing_agent.models.ui_test_case import UiTestCase
from testing_agent.models.ui_test_suite import UiTestSuite


class UiTestCaseRepository:
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

    async def get_suite(self, suite_id: str) -> UiTestSuite | None:
        return await self.session.scalar(
            select(UiTestSuite).where(
                UiTestSuite.suite_id == suite_id,
                UiTestSuite.deleted_at.is_(None),
            )
        )

    async def get_case(self, case_id: str) -> UiTestCase | None:
        return await self.session.scalar(
            select(UiTestCase).where(
                UiTestCase.case_id == case_id,
                UiTestCase.deleted_at.is_(None),
            )
        )

    async def list_by_suite(self, suite_id: str) -> list[UiTestCase]:
        return list(
            (
                await self.session.scalars(
                    select(UiTestCase)
                    .where(UiTestCase.suite_id == suite_id, UiTestCase.deleted_at.is_(None))
                    .order_by(UiTestCase.order_no)
                )
            ).all()
        )

    def add(self, case: UiTestCase) -> None:
        self.session.add(case)

    def soft_delete(self, case: UiTestCase, deleted_at: datetime) -> None:
        case.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, case: UiTestCase) -> None:
        await self.session.refresh(case)

