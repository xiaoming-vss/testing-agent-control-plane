from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.ai_generate_task import ApiCaseGenerateTaskRun
from testing_agent.models.api_case_run import ApiCaseRun
from testing_agent.models.api_collection_run import ApiCollectionRun, ApiCollectionRunItem
from testing_agent.models.integration_connection import IntegrationConnection
from testing_agent.models.project_skill_space import ProjectSkillSpace
from testing_agent.models.requirement import Requirement
from testing_agent.models.ui_test_suite_run import UiTestSuiteRunItem
from testing_agent.models.worker_task import WorkerTask


class WorkerTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def claim_pending(self, domain: str) -> WorkerTask | None:
        return await self.session.scalar(
            select(WorkerTask)
            .where(WorkerTask.domain == domain, WorkerTask.status == "pending")
            .order_by(WorkerTask.created_at.asc())
        )

    async def get_api_item(self, item_id: str) -> ApiCollectionRunItem | None:
        return await self.session.scalar(
            select(ApiCollectionRunItem).where(ApiCollectionRunItem.item_id == item_id)
        )

    async def get_api_collection_run(self, collection_run_id: str) -> ApiCollectionRun | None:
        return await self.session.scalar(
            select(ApiCollectionRun).where(
                ApiCollectionRun.collection_run_id == collection_run_id
            )
        )

    async def get_api_run(self, run_id: str) -> ApiCaseRun | None:
        return await self.session.scalar(select(ApiCaseRun).where(ApiCaseRun.run_id == run_id))

    def add(self, row: ApiCaseRun) -> None:
        self.session.add(row)

    async def get_ui_item(self, item_id: str) -> UiTestSuiteRunItem | None:
        return await self.session.scalar(
            select(UiTestSuiteRunItem).where(UiTestSuiteRunItem.item_id == item_id)
        )

    async def list_project_skills(self, project_id: str) -> list[ProjectSkillSpace]:
        return list(
            (
                await self.session.scalars(
                    select(ProjectSkillSpace)
                    .where(
                        ProjectSkillSpace.project_id == project_id,
                        ProjectSkillSpace.deleted_at.is_(None),
                    )
                    .order_by(
                        ProjectSkillSpace.is_default.desc(),
                        ProjectSkillSpace.created_at.desc(),
                    )
                )
            ).all()
        )

    async def get_llm_connection(self, connection_id: str) -> IntegrationConnection | None:
        return await self.session.scalar(
            select(IntegrationConnection).where(
                IntegrationConnection.connection_id == connection_id,
                IntegrationConnection.provider == "llm",
                IntegrationConnection.deleted_at.is_(None),
            )
        )

    async def get_ai_run(self, run_id: str) -> ApiCaseGenerateTaskRun | None:
        return await self.session.scalar(
            select(ApiCaseGenerateTaskRun).where(ApiCaseGenerateTaskRun.run_id == run_id)
        )

    async def get_requirement(self, requirement_id: str) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.requirement_id == requirement_id,
                Requirement.deleted_at.is_(None),
            )
        )

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, row: object) -> None:
        await self.session.refresh(row)
