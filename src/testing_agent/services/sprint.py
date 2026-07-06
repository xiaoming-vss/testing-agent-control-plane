from __future__ import annotations

from datetime import UTC, datetime

from testing_agent.core.errors import ErrNotFound, ErrSprintNameAlreadyUse
from testing_agent.core.sid import new_id
from testing_agent.models.sprint import Sprint
from testing_agent.repositories.sprint import SprintRepository
from testing_agent.schemas.sprint import CreateSprintRequest, SprintResponse, UpdateSprintRequest
from testing_agent.services.project import ProjectService


def dump_sprint(sprint: Sprint) -> dict:
    return SprintResponse.model_validate(sprint).model_dump(by_alias=True, mode="json")


def parse_api_time(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SprintService:
    def __init__(self, sprints: SprintRepository, projects: ProjectService):
        self.sprints = sprints
        self.projects = projects

    async def get_owned_entity(self, user_id: str, sprint_id: str) -> Sprint:
        sprint = await self.sprints.get_active_by_id(sprint_id)
        if sprint is None:
            raise ErrNotFound
        await self.projects.get_owned_entity(user_id, sprint.project_id)
        return sprint

    async def create(self, user_id: str, project_id: str, body: CreateSprintRequest) -> dict:
        await self.projects.get_owned_entity(user_id, project_id)
        exists = await self.sprints.get_active_by_project_and_name(project_id, body.name)
        if exists is not None:
            raise ErrSprintNameAlreadyUse
        sprint = Sprint(
            sprint_id=new_id(),
            project_id=project_id,
            name=body.name,
            description=body.description,
            status="running",
            start_time=parse_api_time(body.start_time),
            end_time=parse_api_time(body.end_time),
        )
        self.sprints.add(sprint)
        await self.sprints.commit()
        await self.sprints.refresh(sprint)
        return dump_sprint(sprint)

    async def list(self, user_id: str, project_id: str) -> list[dict]:
        await self.projects.get_owned_entity(user_id, project_id)
        rows = await self.sprints.list_active_by_project(project_id)
        return [dump_sprint(row) for row in rows]

    async def get(self, user_id: str, sprint_id: str) -> dict:
        return dump_sprint(await self.get_owned_entity(user_id, sprint_id))

    async def update(self, user_id: str, sprint_id: str, body: UpdateSprintRequest) -> dict:
        sprint = await self.get_owned_entity(user_id, sprint_id)
        if body.name is not None:
            sprint.name = body.name
        if body.description is not None:
            sprint.description = body.description
        if body.status is not None:
            sprint.status = body.status
        if body.start_time is not None:
            sprint.start_time = parse_api_time(body.start_time)
        if body.end_time is not None:
            sprint.end_time = parse_api_time(body.end_time)
        await self.sprints.commit()
        await self.sprints.refresh(sprint)
        return dump_sprint(sprint)

    async def delete(self, user_id: str, sprint_id: str) -> dict:
        sprint = await self.get_owned_entity(user_id, sprint_id)
        self.sprints.soft_delete(sprint, datetime.now(UTC))
        await self.sprints.commit()
        return {}
