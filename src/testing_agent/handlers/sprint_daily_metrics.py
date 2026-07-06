from __future__ import annotations

from fastapi import Depends

from testing_agent.api.deps import get_current_user_id, get_sprint_daily_metrics_service
from testing_agent.core.errors import success_payload
from testing_agent.schemas.sprint_daily_metrics import SprintDailyMetricRequest
from testing_agent.services.sprint_daily_metrics import SprintDailyMetricsService


async def list_sprint_daily_metrics(
    sprint_id: str,
    user_id: str = Depends(get_current_user_id),
    service: SprintDailyMetricsService = Depends(get_sprint_daily_metrics_service),
):
    return success_payload(await service.list(sprint_id, user_id))


async def get_sprint_daily_metric(
    sprint_id: str,
    snapshot_date: str,
    user_id: str = Depends(get_current_user_id),
    service: SprintDailyMetricsService = Depends(get_sprint_daily_metrics_service),
):
    return success_payload(await service.get(sprint_id, snapshot_date, user_id))


async def upsert_sprint_daily_metric(
    sprint_id: str,
    snapshot_date: str,
    body: SprintDailyMetricRequest,
    user_id: str = Depends(get_current_user_id),
    service: SprintDailyMetricsService = Depends(get_sprint_daily_metrics_service),
):
    return success_payload(
        await service.upsert(
            sprint_id,
            snapshot_date,
            body.model_dump(by_alias=False, exclude_none=True),
            user_id,
        )
    )

