from __future__ import annotations

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.sprint import Sprint
from testing_agent.models.ui_test_case import UiTestCase
from testing_agent.models.ui_test_case_run import UiTestCaseRun
from testing_agent.models.ui_test_suite import UiTestSuite
from testing_agent.models.ui_test_suite_run import UiTestSuiteRun, UiTestSuiteRunItem
from testing_agent.models.worker_task import WorkerTask
from testing_agent.repositories.ui_test_case_run import UiTestCaseRunRepository
from testing_agent.schemas.ui_run import (
    DebugRunUiCaseRequest,
    RunUiSuiteRequest,
    UiCaseRunResponse,
    UiSuiteRunResponse,
)
from testing_agent.services.common import dump


class UiCaseRunContext:
    def __init__(
        self,
        case: UiTestCase,
        suite: UiTestSuite,
        requirement: Requirement,
        sprint: Sprint,
        project: Project,
    ):
        self.case = case
        self.suite = suite
        self.requirement = requirement
        self.sprint = sprint
        self.project = project


class UiSuiteRunContext:
    def __init__(
        self,
        suite: UiTestSuite,
        requirement: Requirement,
        sprint: Sprint,
        project: Project,
    ):
        self.suite = suite
        self.requirement = requirement
        self.sprint = sprint
        self.project = project


def dump_case_run(run: UiTestCaseRun) -> dict:
    data = dump(UiCaseRunResponse, run)
    data["success"] = run.status in {"success", "passed", "completed"}
    return data


def dump_suite_run(run: UiTestSuiteRun) -> dict:
    data = dump(UiSuiteRunResponse, run)
    data["success"] = run.status in {"success", "passed", "completed"}
    return data


class UiTestCaseRunService:
    def __init__(self, repository: UiTestCaseRunRepository):
        self.repository = repository

    async def get_owned_suite(self, user_id: str, suite_id: str) -> UiSuiteRunContext:
        suite = await self.repository.get_suite(suite_id)
        if suite is None:
            raise ErrNotFound
        requirement = await self.repository.get_requirement(suite.requirement_id)
        if requirement is None:
            raise ErrNotFound
        sprint = await self.repository.get_sprint(requirement.sprint_id)
        if sprint is None:
            raise ErrNotFound
        project = await self.repository.get_project(sprint.project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden
        return UiSuiteRunContext(suite, requirement, sprint, project)

    async def get_owned_case(self, user_id: str, case_id: str) -> UiCaseRunContext:
        case = await self.repository.get_case(case_id)
        if case is None:
            raise ErrNotFound
        suite_context = await self.get_owned_suite(user_id, case.suite_id)
        return UiCaseRunContext(
            case,
            suite_context.suite,
            suite_context.requirement,
            suite_context.sprint,
            suite_context.project,
        )

    async def ensure_project_owner(self, user_id: str, project_id: str) -> None:
        project = await self.repository.get_project(project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden

    async def debug_run_case(
        self, user_id: str, case_id: str, _: DebugRunUiCaseRequest
    ) -> dict:
        context = await self.get_owned_case(user_id, case_id)
        run = UiTestCaseRun(
            run_id=new_id(),
            case_id=context.case.case_id,
            suite_id=context.suite.suite_id,
            requirement_id=context.requirement.requirement_id,
            sprint_id=context.sprint.sprint_id,
            project_id=context.project.project_id,
            trigger_user_id=user_id,
            trigger_type="manual",
            status="pending",
            snapshot_json={},
            step_results_json=[],
        )
        task = WorkerTask(
            domain="ui",
            task_id=new_id(),
            task_type="case_debug",
            run_id=run.run_id,
            suite_id=context.suite.suite_id,
            case_id=context.case.case_id,
            status="pending",
        )
        self.repository.add_all([run, task])
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_case_run(run)

    async def get_case_run(self, user_id: str, run_id: str) -> dict:
        run = await self.repository.get_case_run(run_id)
        if run is None:
            raise ErrNotFound
        await self.ensure_project_owner(user_id, run.project_id)
        return dump_case_run(run)

    async def run_suite(self, user_id: str, suite_id: str, _: RunUiSuiteRequest) -> dict:
        context = await self.get_owned_suite(user_id, suite_id)
        cases = await self.repository.list_cases(suite_id)
        run = UiTestSuiteRun(
            suite_run_id=new_id(),
            suite_id=suite_id,
            requirement_id=context.requirement.requirement_id,
            sprint_id=context.sprint.sprint_id,
            project_id=context.project.project_id,
            trigger_user_id=user_id,
            trigger_type="manual",
            status="pending",
            total_count=len(cases),
            snapshot_json={},
            summary_json={},
        )
        task = WorkerTask(
            domain="ui",
            task_id=new_id(),
            task_type="suite_run",
            run_id=run.suite_run_id,
            suite_id=suite_id,
            status="pending",
        )
        self.repository.add_all([run, task])
        await self.repository.flush()
        for case in cases:
            self.repository.add(
                UiTestSuiteRunItem(
                    item_id=new_id(),
                    suite_run_id=run.suite_run_id,
                    case_id=case.case_id,
                    order_no=case.order_no,
                    status="pending",
                )
            )
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_suite_run(run)

    async def list_suite_runs(self, user_id: str, suite_id: str) -> list[dict]:
        await self.get_owned_suite(user_id, suite_id)
        rows = await self.repository.list_suite_runs(suite_id)
        return [dump_suite_run(row) for row in rows]

    async def get_suite_run(self, user_id: str, suite_run_id: str) -> dict:
        run = await self.repository.get_suite_run(suite_run_id)
        if run is None:
            raise ErrNotFound
        await self.ensure_project_owner(user_id, run.project_id)
        return dump_suite_run(run)

    async def suite_report(self, user_id: str, suite_run_id: str) -> dict:
        run = await self.repository.get_suite_run(suite_run_id)
        if run is None:
            raise ErrNotFound
        await self.ensure_project_owner(user_id, run.project_id)
        items = await self.repository.list_suite_items(suite_run_id)
        data = dump_suite_run(run)
        data["items"] = [
            {
                "itemId": item.item_id,
                "caseId": item.case_id,
                "status": item.status,
                "orderNo": item.order_no,
            }
            for item in items
        ]
        return data
