from __future__ import annotations

from fastapi import Depends

from testing_agent.api.deps import get_current_user_id, get_project_service
from testing_agent.core.errors import success_payload
from testing_agent.schemas.project import CreateProjectRequest, UpdateProjectRequest
from testing_agent.services.project import ProjectService


async def create_project(
    body: CreateProjectRequest,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
):
    return success_payload(await service.create(user_id, body))


async def list_projects(
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
):
    return success_payload(await service.list(user_id))


async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
):
    return success_payload(await service.get(user_id, project_id))


async def update_project(
    project_id: str,
    body: UpdateProjectRequest,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
):
    return success_payload(await service.update(user_id, project_id, body))


async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
):
    return success_payload(await service.delete(user_id, project_id))
