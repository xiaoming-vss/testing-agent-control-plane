from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.function_test_case import FunctionTestCase
from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.repositories.function_test_case import FunctionTestCaseRepository
from testing_agent.schemas.function_test_case import FunctionCaseRequest, FunctionCaseResponse
from testing_agent.services.api_collection import (
    import_items,
    parse_import_payload,
    read_import_payload,
)
from testing_agent.services.common import apply_patch, dump


class FunctionTestCaseService:
    def __init__(self, repository: FunctionTestCaseRepository):
        self.repository = repository

    async def get_owned_suite(self, user_id: str, suite_id: str) -> FunctionTestSuite:
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
        return suite

    async def get_owned_entity(self, user_id: str, case_id: str) -> FunctionTestCase:
        case = await self.repository.get_case(case_id)
        if case is None:
            raise ErrNotFound
        await self.get_owned_suite(user_id, case.suite_id)
        return case

    async def create(self, user_id: str, suite_id: str, body: FunctionCaseRequest) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        case = FunctionTestCase(
            case_id=new_id(),
            suite_id=suite_id,
            **body.model_dump(by_alias=False),
        )
        self.repository.add(case)
        await self.repository.commit()
        await self.repository.refresh(case)
        return dump(FunctionCaseResponse, case)

    async def import_cases(self, user_id: str, suite_id: str, payload: Any, file: Any) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        parsed = await read_import_payload(payload, file)
        created = 0
        for index, item in enumerate(import_items(parsed, "cases", "functionCases", "testcases")):
            if not isinstance(item, dict):
                continue
            self.repository.add(
                FunctionTestCase(
                    case_id=new_id(),
                    suite_id=suite_id,
                    module=str(item.get("module") or ""),
                    title=str(
                        item.get("title") or item.get("name") or f"Function Case {index + 1}"
                    ),
                    preconditions=str(
                        item.get("preconditions") or item.get("precondition") or ""
                    ),
                    steps=str(item.get("steps") or ""),
                    expected_results=str(
                        item.get("expectedResults") or item.get("expected_results") or ""
                    ),
                    priority=str(item.get("priority") or ""),
                    case_type=str(item.get("caseType") or item.get("case_type") or ""),
                    order_no=int(item.get("orderNo", item.get("order_no", index))),
                )
            )
            created += 1
        await self.repository.commit()
        return {"imported": created}

    async def import_to_zentao(self, user_id: str, suite_id: str, payload: Any) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        return {"suiteId": suite_id, "status": "queued", "request": parse_import_payload(payload)}

    async def list(self, user_id: str, suite_id: str) -> list[dict]:
        await self.get_owned_suite(user_id, suite_id)
        rows = await self.repository.list_by_suite(suite_id)
        return [dump(FunctionCaseResponse, row) for row in rows]

    async def get(self, user_id: str, case_id: str) -> dict:
        return dump(FunctionCaseResponse, await self.get_owned_entity(user_id, case_id))

    async def update(self, user_id: str, case_id: str, body: dict[str, Any]) -> dict:
        case = await self.get_owned_entity(user_id, case_id)
        apply_patch(
            case,
            body,
            {
                "module",
                "title",
                "preconditions",
                "steps",
                "expected_results",
                "priority",
                "case_type",
                "order_no",
            },
        )
        await self.repository.commit()
        await self.repository.refresh(case)
        return dump(FunctionCaseResponse, case)

    async def delete(self, user_id: str, case_id: str) -> dict:
        case = await self.get_owned_entity(user_id, case_id)
        self.repository.soft_delete(case, datetime.now(UTC))
        await self.repository.commit()
        return {}
