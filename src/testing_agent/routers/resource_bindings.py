from __future__ import annotations

from fastapi import APIRouter

from testing_agent.handlers.resource_binding import (
    bind_project,
    bind_requirement,
    bind_sprint,
    list_project_bindings,
    list_requirement_bindings,
    list_sprint_bindings,
    unbind_project,
    unbind_requirement,
    unbind_sprint,
)
from testing_agent.schemas.common import ApiResponse, EmptyData
from testing_agent.schemas.resource_binding import ResourceBindingResponse

router = APIRouter()

router.post(
    "/projects/{project_id}/bindings",
    response_model=ApiResponse[ResourceBindingResponse],
)(bind_project)
router.get(
    "/projects/{project_id}/bindings",
    response_model=ApiResponse[list[ResourceBindingResponse]],
)(list_project_bindings)
router.delete(
    "/projects/{project_id}/bindings/{binding_id}",
    response_model=ApiResponse[EmptyData],
)(unbind_project)
router.post(
    "/sprints/{sprint_id}/bindings",
    response_model=ApiResponse[ResourceBindingResponse],
)(bind_sprint)
router.get(
    "/sprints/{sprint_id}/bindings",
    response_model=ApiResponse[list[ResourceBindingResponse]],
)(list_sprint_bindings)
router.delete(
    "/sprints/{sprint_id}/bindings/{binding_id}",
    response_model=ApiResponse[EmptyData],
)(unbind_sprint)
router.post(
    "/requirements/{requirement_id}/bindings",
    response_model=ApiResponse[ResourceBindingResponse],
)(bind_requirement)
router.get(
    "/requirements/{requirement_id}/bindings",
    response_model=ApiResponse[list[ResourceBindingResponse]],
)(list_requirement_bindings)
router.delete(
    "/requirements/{requirement_id}/bindings/{binding_id}",
    response_model=ApiResponse[EmptyData],
)(unbind_requirement)
