from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.ai_generate_task import AiGenerateTask, ApiCaseGenerateTaskRun
from testing_agent.models.api_assert_rule import ApiAssertRule
from testing_agent.models.api_case import ApiCase
from testing_agent.models.api_collection import ApiCollection
from testing_agent.models.api_extract_rule import ApiExtractRule
from testing_agent.models.function_test_case import FunctionTestCase
from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.sprint import Sprint
from testing_agent.models.ui_test_case import UiTestCase
from testing_agent.models.ui_test_suite import UiTestSuite
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

    async def list_api_cases(self, collection_id: str) -> list[ApiCase]:
        return list(
            (
                await self.session.scalars(
                    select(ApiCase).where(
                        ApiCase.collection_id == collection_id,
                        ApiCase.deleted_at.is_(None),
                    )
                )
            ).all()
        )

    async def list_api_extract_rules(self, case_id: str) -> list[ApiExtractRule]:
        return list(
            (
                await self.session.scalars(
                    select(ApiExtractRule)
                    .where(
                        ApiExtractRule.case_id == case_id,
                        ApiExtractRule.deleted_at.is_(None),
                    )
                    .order_by(ApiExtractRule.order_no, ApiExtractRule.id)
                )
            ).all()
        )

    async def list_api_assert_rules(self, case_id: str) -> list[ApiAssertRule]:
        return list(
            (
                await self.session.scalars(
                    select(ApiAssertRule)
                    .where(
                        ApiAssertRule.case_id == case_id,
                        ApiAssertRule.deleted_at.is_(None),
                    )
                    .order_by(ApiAssertRule.order_no, ApiAssertRule.id)
                )
            ).all()
        )

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

    async def get_active_task_by_project_sprint_type(
        self, project_id: str, sprint_id: str, task_type: str
    ) -> AiGenerateTask | None:
        return await self.session.scalar(
            select(AiGenerateTask).where(
                AiGenerateTask.project_id == project_id,
                AiGenerateTask.sprint_id == sprint_id,
                AiGenerateTask.task_type == task_type,
                AiGenerateTask.deleted_at.is_(None),
            )
        )

    async def list_runs_by_project_sprint_task_type(
        self, project_id: str, sprint_id: str, task_type: str
    ) -> list[ApiCaseGenerateTaskRun]:
        return list(
            (
                await self.session.scalars(
                    select(ApiCaseGenerateTaskRun)
                    .join(AiGenerateTask, AiGenerateTask.task_id == ApiCaseGenerateTaskRun.task_id)
                    .where(
                        ApiCaseGenerateTaskRun.project_id == project_id,
                        ApiCaseGenerateTaskRun.sprint_id == sprint_id,
                        AiGenerateTask.task_type == task_type,
                        AiGenerateTask.deleted_at.is_(None),
                    )
                    .order_by(ApiCaseGenerateTaskRun.created_at.desc())
                )
            ).all()
        )

    async def get_run(self, run_id: str) -> ApiCaseGenerateTaskRun | None:
        return await self.session.scalar(
            select(ApiCaseGenerateTaskRun).where(ApiCaseGenerateTaskRun.run_id == run_id)
        )

    async def get_run_for_update(self, run_id: str) -> ApiCaseGenerateTaskRun | None:
        return await self.session.scalar(
            select(ApiCaseGenerateTaskRun)
            .where(ApiCaseGenerateTaskRun.run_id == run_id)
            .with_for_update()
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

    async def get_function_suite_by_requirement_and_name(
        self, requirement_id: str, name: str
    ) -> FunctionTestSuite | None:
        return await self.session.scalar(
            select(FunctionTestSuite)
            .where(
                FunctionTestSuite.requirement_id == requirement_id,
                FunctionTestSuite.name == name,
                FunctionTestSuite.deleted_at.is_(None),
            )
            .with_for_update()
        )

    async def get_function_case_by_suite_and_title(
        self, suite_id: str, title: str
    ) -> FunctionTestCase | None:
        return await self.session.scalar(
            select(FunctionTestCase).where(
                FunctionTestCase.suite_id == suite_id,
                FunctionTestCase.title == title,
                FunctionTestCase.deleted_at.is_(None),
            )
        )

    async def list_function_cases(self, suite_id: str) -> list[FunctionTestCase]:
        return list(
            (
                await self.session.scalars(
                    select(FunctionTestCase)
                    .where(
                        FunctionTestCase.suite_id == suite_id,
                        FunctionTestCase.deleted_at.is_(None),
                    )
                    .order_by(FunctionTestCase.order_no, FunctionTestCase.id)
                    .with_for_update()
                )
            ).all()
        )

    async def max_function_case_order_by_suite(self, suite_id: str) -> int:
        value = await self.session.scalar(
            select(func.max(FunctionTestCase.order_no)).where(
                FunctionTestCase.suite_id == suite_id,
                FunctionTestCase.deleted_at.is_(None),
            )
        )
        return int(value or 0)

    async def get_ui_suite(self, suite_id: str) -> UiTestSuite | None:
        return await self.session.scalar(
            select(UiTestSuite)
            .where(
                UiTestSuite.suite_id == suite_id,
                UiTestSuite.deleted_at.is_(None),
            )
            .with_for_update()
        )

    async def list_ui_cases(self, suite_id: str) -> list[UiTestCase]:
        return list(
            (
                await self.session.scalars(
                    select(UiTestCase)
                    .where(
                        UiTestCase.suite_id == suite_id,
                        UiTestCase.deleted_at.is_(None),
                    )
                    .order_by(UiTestCase.order_no, UiTestCase.id)
                    .with_for_update()
                )
            ).all()
        )

    def add(self, row: object) -> None:
        self.session.add(row)

    def add_all(self, rows: list[object]) -> None:
        self.session.add_all(rows)

    async def delete(self, row: object) -> None:
        await self.session.delete(row)

    async def flush(self) -> None:
        await self.session.flush()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, row: object) -> None:
        await self.session.refresh(row)
