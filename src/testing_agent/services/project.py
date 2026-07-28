from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound, ErrProjectNameAlreadyUse
from testing_agent.core.sid import new_id
from testing_agent.models.project import Project
from testing_agent.repositories.project import ProjectRepository
from testing_agent.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
from testing_agent.services.common import list_payload


def dump_project(project: Project) -> dict:
    return ProjectResponse.model_validate(project).model_dump(by_alias=True, mode="json")


class ProjectService:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    async def get_owned_entity(self, user_id: str, project_id: str) -> Project:
        project = await self.projects.get_active_by_id(project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden
        return project

    async def create(self, user_id: str, body: CreateProjectRequest) -> dict:
        exists = await self.projects.get_active_by_user_and_name(user_id, body.name)
        if exists is not None:
            raise ErrProjectNameAlreadyUse
        project = Project(
            project_id=new_id(),
            user_id=user_id,
            name=body.name,
            description=body.description,
        )
        self.projects.add(project)
        await self.projects.commit()
        await self.projects.refresh(project)
        return dump_project(project)

    async def list(self, user_id: str) -> dict[str, Any]:
        rows = await self.projects.list_active_by_user(user_id)
        return list_payload([dump_project(row) for row in rows])

    async def get(self, user_id: str, project_id: str) -> dict:
        return dump_project(await self.get_owned_entity(user_id, project_id))

    async def update(self, user_id: str, project_id: str, body: UpdateProjectRequest) -> dict:
        project = await self.get_owned_entity(user_id, project_id)
        if body.name is not None and body.name != project.name:
            exists = await self.projects.get_active_by_user_and_name(user_id, body.name)
            if exists is not None:
                raise ErrProjectNameAlreadyUse
            project.name = body.name
        if body.description is not None:
            project.description = body.description
        await self.projects.commit()
        await self.projects.refresh(project)
        return dump_project(project)

    async def delete(self, user_id: str, project_id: str) -> dict:
        project = await self.get_owned_entity(user_id, project_id)
        self.projects.soft_delete(project, datetime.now(UTC))
        await self.projects.commit()
        return {}
