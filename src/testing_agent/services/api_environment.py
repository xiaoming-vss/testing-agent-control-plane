from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.api_environment import ApiEnvironment
from testing_agent.repositories.api_environment import ApiEnvironmentRepository
from testing_agent.schemas.api_environment import ApiEnvironmentRequest, ApiEnvironmentResponse
from testing_agent.services.common import apply_patch, dump, list_payload


class ApiEnvironmentService:
    def __init__(self, repository: ApiEnvironmentRepository):
        self.repository = repository

    async def ensure_project_owner(self, user_id: str, project_id: str) -> None:
        project = await self.repository.get_project(project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden

    async def get_owned_entity(self, user_id: str, environment_id: str) -> ApiEnvironment:
        environment = await self.repository.get_environment(environment_id)
        if environment is None:
            raise ErrNotFound
        await self.ensure_project_owner(user_id, environment.project_id)
        return environment

    async def create(self, user_id: str, project_id: str, body: ApiEnvironmentRequest) -> dict:
        await self.ensure_project_owner(user_id, project_id)
        environment = ApiEnvironment(
            environment_id=new_id(),
            project_id=project_id,
            **body.model_dump(by_alias=False),
        )
        self.repository.add(environment)
        await self.repository.commit()
        await self.repository.refresh(environment)
        return dump(ApiEnvironmentResponse, environment)

    async def list(self, user_id: str, project_id: str) -> dict[str, Any]:
        await self.ensure_project_owner(user_id, project_id)
        rows = await self.repository.list_by_project(project_id)
        return list_payload([dump(ApiEnvironmentResponse, row) for row in rows])

    async def get(self, user_id: str, environment_id: str) -> dict:
        return dump(ApiEnvironmentResponse, await self.get_owned_entity(user_id, environment_id))

    async def update(self, user_id: str, environment_id: str, body: dict[str, Any]) -> dict:
        environment = await self.get_owned_entity(user_id, environment_id)
        apply_patch(environment, body, {"name", "base_url", "description", "is_default"})
        await self.repository.commit()
        await self.repository.refresh(environment)
        return dump(ApiEnvironmentResponse, environment)

    async def delete(self, user_id: str, environment_id: str) -> dict:
        environment = await self.get_owned_entity(user_id, environment_id)
        self.repository.soft_delete(environment, datetime.now(UTC))
        await self.repository.commit()
        return {}

