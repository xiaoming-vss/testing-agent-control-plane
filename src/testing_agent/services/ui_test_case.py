from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.ui_test_case import UiTestCase
from testing_agent.models.ui_test_suite import UiTestSuite
from testing_agent.repositories.ui_test_case import UiTestCaseRepository
from testing_agent.schemas.ui_test_case import UiCaseRequest, UiCaseResponse
from testing_agent.services.api_collection import (
    import_items,
    normalize_json_value,
    read_import_payload,
)
from testing_agent.services.common import apply_patch, dump, list_payload


class UiTestCaseService:
    def __init__(self, repository: UiTestCaseRepository):
        self.repository = repository

    async def get_owned_suite(self, user_id: str, suite_id: str) -> UiTestSuite:
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

    async def get_owned_entity(self, user_id: str, case_id: str) -> UiTestCase:
        case = await self.repository.get_case(case_id)
        if case is None:
            raise ErrNotFound
        await self.get_owned_suite(user_id, case.suite_id)
        return case

    async def create(self, user_id: str, suite_id: str, body: UiCaseRequest) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        case = UiTestCase(
            case_id=new_id(),
            suite_id=suite_id,
            **body.model_dump(by_alias=False),
        )
        self.repository.add(case)
        await self.repository.commit()
        await self.repository.refresh(case)
        return dump(UiCaseResponse, case)

    async def import_cases(self, user_id: str, suite_id: str, payload: Any, file: Any) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        parsed = await read_import_payload(payload, file)
        created = 0
        for index, item in enumerate(import_items(parsed, "cases", "uiCases")):
            if not isinstance(item, dict):
                continue
            self.repository.add(
                UiTestCase(
                    case_id=new_id(),
                    suite_id=suite_id,
                    name=str(item.get("name") or item.get("title") or f"UI Case {index + 1}"),
                    enabled=bool(item.get("enabled", True)),
                    order_no=int(item.get("orderNo", item.get("order_no", index))),
                    steps_json=normalize_json_value(
                        item.get("stepsJson") or item.get("steps") or []
                    ),
                )
            )
            created += 1
        await self.repository.commit()
        return {"imported": created}

    async def list(self, user_id: str, suite_id: str) -> dict[str, Any]:
        await self.get_owned_suite(user_id, suite_id)
        rows = await self.repository.list_by_suite(suite_id)
        return list_payload([dump(UiCaseResponse, row) for row in rows])

    async def get(self, user_id: str, case_id: str) -> dict:
        return dump(UiCaseResponse, await self.get_owned_entity(user_id, case_id))

    async def update(self, user_id: str, case_id: str, body: dict[str, Any]) -> dict:
        case = await self.get_owned_entity(user_id, case_id)
        apply_patch(case, body, {"name", "enabled", "order_no", "steps_json"})
        await self.repository.commit()
        await self.repository.refresh(case)
        return dump(UiCaseResponse, case)

    async def delete(self, user_id: str, case_id: str) -> dict:
        case = await self.get_owned_entity(user_id, case_id)
        self.repository.soft_delete(case, datetime.now(UTC))
        await self.repository.commit()
        return {}

