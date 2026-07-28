from __future__ import annotations

from fastapi import APIRouter

from testing_agent.handlers.project import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from testing_agent.schemas.common import ApiResponse, EmptyData, ListResponse
from testing_agent.schemas.project import ProjectResponse

router = APIRouter()

router.post("/projects", response_model=ApiResponse[ProjectResponse])(create_project)
router.get("/projects", response_model=ApiResponse[ListResponse[ProjectResponse]])(list_projects)
router.get("/projects/{project_id}", response_model=ApiResponse[ProjectResponse])(
    get_project
)
router.patch("/projects/{project_id}", response_model=ApiResponse[ProjectResponse])(
    update_project
)
router.delete("/projects/{project_id}", response_model=ApiResponse[EmptyData])(
    delete_project
)
