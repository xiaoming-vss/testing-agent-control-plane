from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.repositories.function_test_suite import FunctionTestSuiteRepository
from testing_agent.schemas.function_test_suite import FunctionSuiteRequest, FunctionSuiteResponse
from testing_agent.services.common import apply_patch, dump, list_payload


class FunctionTestSuiteService:
    def __init__(self, repository: FunctionTestSuiteRepository):
        self.repository = repository

    async def ensure_requirement_owner(self, user_id: str, requirement_id: str) -> None:
        requirement = await self.repository.get_requirement(requirement_id)
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

    async def get_owned_entity(self, user_id: str, suite_id: str) -> FunctionTestSuite:
        suite = await self.repository.get_suite(suite_id)
        if suite is None:
            raise ErrNotFound
        await self.ensure_requirement_owner(user_id, suite.requirement_id)
        return suite

    async def create(self, user_id: str, requirement_id: str, body: FunctionSuiteRequest) -> dict:
        await self.ensure_requirement_owner(user_id, requirement_id)
        suite = FunctionTestSuite(
            suite_id=new_id(),
            requirement_id=requirement_id,
            name=body.name,
            description=body.description,
        )
        self.repository.add(suite)
        await self.repository.commit()
        await self.repository.refresh(suite)
        return dump(FunctionSuiteResponse, suite)

    async def list(self, user_id: str, requirement_id: str) -> dict[str, Any]:
        await self.ensure_requirement_owner(user_id, requirement_id)
        rows = await self.repository.list_by_requirement(requirement_id)
        return list_payload([dump(FunctionSuiteResponse, row) for row in rows])

    async def get(self, user_id: str, suite_id: str) -> dict:
        return dump(FunctionSuiteResponse, await self.get_owned_entity(user_id, suite_id))

    async def update(self, user_id: str, suite_id: str, body: dict[str, Any]) -> dict:
        suite = await self.get_owned_entity(user_id, suite_id)
        apply_patch(suite, body, {"name", "description"})
        await self.repository.commit()
        await self.repository.refresh(suite)
        return dump(FunctionSuiteResponse, suite)

    async def delete(self, user_id: str, suite_id: str) -> dict:
        suite = await self.get_owned_entity(user_id, suite_id)
        self.repository.soft_delete(suite, datetime.now(UTC))
        await self.repository.commit()
        return {}

