from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.ai_generate_task import AiGenerateTask, ApiCaseGenerateTaskRun
from testing_agent.models.api_case import ApiCase
from testing_agent.models.api_collection import ApiCollection
from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.sprint import Sprint
from testing_agent.models.worker_task import WorkerTask


class AiGenerateTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def get_sprint(self, sprint_id: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.sprint_id == sprint_id, Sprint.deleted_at.is_(None))
        )

    async def get_requirement(self, requirement_id: str) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.requirement_id == requirement_id,
                Requirement.deleted_at.is_(None),
            )
        )

    async def get_collection(self, collection_id: str) -> ApiCollection | None:
        return await self.session.scalar(
            select(ApiCollection).where(
                ApiCollection.collection_id == collection_id,
                ApiCollection.deleted_at.is_(None),
            )
        )

    async def exists_case_by_collection_and_name(self, collection_id: str, name: str) -> bool:
        row = await self.session.scalar(
            select(ApiCase.case_id).where(
                ApiCase.collection_id == collection_id,
                ApiCase.name == name,
                ApiCase.deleted_at.is_(None),
            )
        )
        return row is not None

    async def get_task(self, task_id: str) -> AiGenerateTask | None:
        return await self.session.scalar(
            select(AiGenerateTask).where(
                AiGenerateTask.task_id == task_id,
                AiGenerateTask.deleted_at.is_(None),
            )
        )

    async def list_tasks(self, project_id: str, task_type: str) -> list[AiGenerateTask]:
        return list(
            (
                await self.session.scalars(
                    select(AiGenerateTask)
                    .where(
                        AiGenerateTask.project_id == project_id,
                        AiGenerateTask.task_type == task_type,
                        AiGenerateTask.deleted_at.is_(None),
                    )
                    .order_by(AiGenerateTask.created_at.desc())
                )
            ).all()
        )

    async def get_run(self, run_id: str) -> ApiCaseGenerateTaskRun | None:
        return await self.session.scalar(
            select(ApiCaseGenerateTaskRun).where(ApiCaseGenerateTaskRun.run_id == run_id)
        )

    async def list_runs(self, task_id: str) -> list[ApiCaseGenerateTaskRun]:
        return list(
            (
                await self.session.scalars(
                    select(ApiCaseGenerateTaskRun)
                    .where(ApiCaseGenerateTaskRun.task_id == task_id)
                    .order_by(ApiCaseGenerateTaskRun.created_at.desc())
                )
            ).all()
        )

    async def get_latest_worker_task_by_run_id(self, run_id: str) -> WorkerTask | None:
        return await self.session.scalar(
            select(WorkerTask)
            .where(WorkerTask.domain == "ai", WorkerTask.run_id == run_id)
            .order_by(WorkerTask.created_at.desc(), WorkerTask.id.desc())
        )

    def add(self, row: object) -> None:
        self.session.add(row)

    def add_all(self, rows: list[object]) -> None:
        self.session.add_all(rows)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, row: object) -> None:
        await self.session.refresh(row)
