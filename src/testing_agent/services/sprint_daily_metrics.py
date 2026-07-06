from __future__ import annotations

from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.sprint import Sprint
from testing_agent.models.sprint_daily_metrics import SprintDailyMetrics
from testing_agent.repositories.sprint_daily_metrics import SprintDailyMetricsRepository


def dump_metric(metric: SprintDailyMetrics) -> dict[str, Any]:
    return {
        "projectId": metric.project_id,
        "sprintId": metric.sprint_id,
        "snapshotDate": metric.snapshot_date,
        "function": {
            "total": metric.function_case_total,
            "executed": metric.function_case_executed,
            "pending": metric.function_case_pending,
            "success": metric.function_case_success,
            "failed": metric.function_case_failed,
        },
        "api": {
            "total": metric.api_case_total,
            "executed": metric.api_case_executed,
            "pending": metric.api_case_pending,
            "success": metric.api_case_success,
            "failed": metric.api_case_failed,
        },
        "ui": {
            "total": metric.ui_case_total,
            "executed": metric.ui_case_executed,
            "pending": metric.ui_case_pending,
            "success": metric.ui_case_success,
            "failed": metric.ui_case_failed,
        },
        "bug": {
            "total": metric.bug_total,
            "resolved": metric.bug_resolved,
            "unresolved": metric.bug_unresolved,
            "fatal": metric.bug_fatal,
            "serious": metric.bug_serious,
            "normal": metric.bug_normal,
            "suggestion": metric.bug_suggestion,
        },
        "createdAt": metric.created_at,
        "updatedAt": metric.updated_at,
    }


class SprintDailyMetricsService:
    def __init__(self, repository: SprintDailyMetricsRepository):
        self.repository = repository

    async def get_owned_sprint(self, user_id: str, sprint_id: str) -> Sprint:
        sprint = await self.repository.get_sprint(sprint_id)
        if sprint is None:
            raise ErrNotFound
        project = await self.repository.get_project(sprint.project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden
        return sprint

    async def list(self, sprint_id: str, user_id: str) -> list[dict]:
        await self.get_owned_sprint(user_id, sprint_id)
        rows = await self.repository.list(sprint_id)
        return [dump_metric(row) for row in rows]

    async def get(self, sprint_id: str, snapshot_date: str, user_id: str) -> dict:
        await self.get_owned_sprint(user_id, sprint_id)
        metric = await self.repository.get(sprint_id, snapshot_date)
        if metric is None:
            raise ErrNotFound
        return dump_metric(metric)

    async def upsert(
        self, sprint_id: str, snapshot_date: str, body: dict[str, Any], user_id: str
    ) -> dict:
        sprint = await self.get_owned_sprint(user_id, sprint_id)
        metric = await self.repository.get(sprint_id, snapshot_date)
        if metric is None:
            metric = SprintDailyMetrics(
                metric_id=new_id(),
                project_id=sprint.project_id,
                sprint_id=sprint_id,
                snapshot_date=snapshot_date,
            )
            self.repository.add(metric)
        for key, value in body.items():
            snake = "".join(
                [f"_{char.lower()}" if char.isupper() else char for char in key]
            ).lstrip("_")
            if hasattr(metric, snake):
                setattr(metric, snake, value)
        await self.repository.commit()
        await self.repository.refresh(metric)
        return dump_metric(metric)
