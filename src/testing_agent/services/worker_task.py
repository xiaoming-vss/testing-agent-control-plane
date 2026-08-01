from __future__ import annotations

from datetime import UTC, datetime, timedelta

from testing_agent.core.errors import ErrBadRequest, ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.api_case_run import ApiCaseRun
from testing_agent.repositories.worker_task import WorkerTaskRepository
from testing_agent.schemas.workers import (
    WorkerClaimRequest,
    WorkerProgressRequest,
    WorkerTaskEventRequest,
)
from testing_agent.services.worker import (
    LEASE_SECONDS,
    apply_event_to_task,
    build_snapshot,
    complete_domain_run,
    final_run_status,
    find_task,
    json_text,
    llm_credentials_payload,
    parse_event_time,
    project_skill_worker_payload,
    save_extracted_environment_vars,
    task_payload,
    update_item_counts,
    update_task_claimed,
    update_ui_item_counts,
)

AI_LEASE_SECONDS = 30
AI_WAITING_REVIEW_STAGES = {
    "requirement_analysis",
    "case_names",
    "extracting_text",
    "writing_requirement",
}


def ensure_worker_match(task, worker_id: str | None) -> None:
    if not worker_id or not worker_id.strip():
        raise ErrBadRequest
    if task.worker_id and task.worker_id != worker_id:
        raise ErrForbidden


def ensure_task_id(task, body: WorkerTaskEventRequest) -> None:
    if body.task_id and body.task_id != task.task_id:
        raise ErrBadRequest


def ensure_final_status(status: str | None, allowed: set[str]) -> str:
    value = final_run_status(status)
    if value not in allowed:
        raise ErrBadRequest
    return value


class WorkerTaskService:
    def __init__(self, repository: WorkerTaskRepository):
        self.repository = repository

    async def claim(self, domain: str, body: WorkerClaimRequest) -> dict | None:
        task = await self.repository.claim_pending(domain)
        if task is None:
            return None
        await update_task_claimed(task, body)
        if domain == "api":
            if task.collection_run_id:
                run = await self.repository.get_api_collection_run(task.collection_run_id)
            else:
                run = await self.repository.get_api_run(task.run_id)
            if run is None:
                raise ErrNotFound
            run.status = "queued"
        if domain == "ai":
            task.lease_expires_at = datetime.now(UTC) + timedelta(seconds=AI_LEASE_SECONDS)
            run = await self.repository.get_ai_run(task.run_id)
            if run is None:
                raise ErrNotFound
            run.status = "claimed"
            if run.checkpoint_enabled:
                run.stage_status = "running"
            await self.repository.commit()
            await self.repository.refresh(task)
            payload = {
                "taskId": task.task_id,
                "taskType": task.task_type,
                "runId": task.run_id,
                "generateTaskId": task.generate_task_id,
                "projectId": run.project_id,
                "sprintId": run.sprint_id,
                "requirementId": run.requirement_id,
                "llmConnectionId": task.llm_connection_id,
                "checkpointEnabled": run.checkpoint_enabled,
                "currentStage": run.current_stage,
                "leaseSeconds": AI_LEASE_SECONDS,
            }
            if run.checkpoint_enabled:
                payload["configJson"] = json_text(getattr(run, "config_json", {}) or {})
            return payload
        await self.repository.commit()
        await self.repository.refresh(task)
        payload = task_payload(task)
        payload["leaseSeconds"] = LEASE_SECONDS
        return payload

    async def snapshot(self, domain: str, task_id: str) -> dict:
        task = await find_task(self.repository.session, domain, task_id)
        return await build_snapshot(self.repository.session, domain, task)

    async def started(self, domain: str, task_id: str, body: WorkerTaskEventRequest) -> dict:
        task = await find_task(self.repository.session, domain, task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        started_at = parse_event_time(body.started_at)
        if body.started_at and started_at is None:
            raise ErrBadRequest
        await apply_event_to_task(task, body, "running")
        if started_at is not None:
            task.started_at = started_at
            task.heartbeat_at = started_at
            task.lease_expires_at = started_at + timedelta(seconds=LEASE_SECONDS)
        if domain == "api":
            if task.collection_run_id:
                run = await self.repository.get_api_collection_run(task.collection_run_id)
            else:
                run = await self.repository.get_api_run(task.run_id)
            if run:
                run.status = "running"
                if getattr(run, "started_at", None) is None:
                    run.started_at = started_at or datetime.now(UTC)
        if domain == "ai":
            run = await self.repository.get_ai_run(task.run_id)
            if run is None:
                raise ErrNotFound
            run.status = "running"
            run.started_at = parse_event_time(body.started_at) or datetime.now(UTC)
            if run.checkpoint_enabled:
                run.stage_status = "running"
        await self.repository.commit()
        return {"taskId": task_id, "workerId": body.worker_id}

    async def heartbeat(self, domain: str, task_id: str, body: WorkerTaskEventRequest) -> dict:
        task = await find_task(self.repository.session, domain, task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        heartbeat_at = parse_event_time(body.heartbeat_at)
        if body.heartbeat_at and heartbeat_at is None:
            raise ErrBadRequest
        await apply_event_to_task(task, body, task.status)
        if heartbeat_at is not None:
            task.heartbeat_at = heartbeat_at
            task.lease_expires_at = heartbeat_at + timedelta(seconds=LEASE_SECONDS)
        await self.repository.commit()
        return {"taskId": task_id, "workerId": body.worker_id}

    async def complete(self, domain: str, task_id: str, body: WorkerTaskEventRequest) -> dict:
        task = await find_task(self.repository.session, domain, task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        status = ensure_final_status(body.status, {"success", "failed", "error", "canceled"})
        await apply_event_to_task(task, body, status)
        await complete_domain_run(self.repository.session, domain, task, body)
        await self.repository.commit()
        return {"taskId": task_id, "workerId": body.worker_id, "status": status}

    async def start_api_collection_item(
        self, task_id: str, item_id: str, body: WorkerTaskEventRequest
    ) -> dict:
        task = await find_task(self.repository.session, "api", task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        if task.task_type != "api_collection_run":
            raise ErrBadRequest
        item = await self.repository.get_api_item(item_id)
        if item is None:
            raise ErrNotFound
        item.status = "running"
        item.started_at = parse_event_time(body.started_at) or datetime.now(UTC)
        await self.repository.commit()
        return {"taskId": task_id, "itemId": item_id, "workerId": body.worker_id}

    async def complete_api_collection_item(
        self, task_id: str, item_id: str, body: WorkerTaskEventRequest
    ) -> dict:
        task = await find_task(self.repository.session, "api", task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        if task.task_type != "api_collection_run":
            raise ErrBadRequest
        status = ensure_final_status(body.status, {"success", "failed", "error", "skipped"})
        item = await self.repository.get_api_item(item_id)
        if item is None:
            raise ErrNotFound
        collection_run = await self.repository.get_api_collection_run(item.collection_run_id)
        if collection_run is None:
            raise ErrNotFound
        item.status = status
        started_at = parse_event_time(body.started_at)
        finished_at = parse_event_time(body.finished_at) or datetime.now(UTC)
        case_run = ApiCaseRun(
            run_id=new_id(),
            collection_run_id=item.collection_run_id,
            case_id=body.case_id or item.case_id,
            collection_id=task.collection_id,
            requirement_id=collection_run.requirement_id,
            sprint_id=collection_run.sprint_id,
            project_id=collection_run.project_id,
            environment_id=collection_run.environment_id,
            trigger_user_id=collection_run.trigger_user_id,
            trigger_type="collection",
            status=item.status,
            request_snapshot_json=body.request or {},
            response_snapshot_json=body.response or {},
            runtime_vars_json=body.runtime_vars_json or {},
            extract_results_json=body.extract_results or [],
            assert_results_json=body.assert_results or body.step_results or [],
            error_message=body.error_message or "",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=body.duration_ms or 0,
        )
        self.repository.add(case_run)
        await save_extracted_environment_vars(
            self.repository.session,
            collection_run.environment_id,
            body.extract_results,
        )
        item.case_run_id = case_run.run_id
        item.started_at = started_at
        item.error_message = body.error_message or ""
        item.finished_at = finished_at
        if body.duration_ms is not None:
            item.duration_ms = body.duration_ms
        await update_item_counts(self.repository.session, item.collection_run_id)
        await self.repository.commit()
        return {"taskId": task_id, "itemId": item_id, "status": item.status}

    async def start_ui_suite_item(
        self, task_id: str, item_id: str, body: WorkerTaskEventRequest
    ) -> dict:
        task = await find_task(self.repository.session, "ui", task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        item = await self.repository.get_ui_item(item_id)
        if item is None:
            raise ErrNotFound
        item.status = "running"
        item.started_at = parse_event_time(body.started_at) or datetime.now(UTC)
        await self.repository.commit()
        return {"taskId": task_id, "itemId": item_id, "workerId": body.worker_id}

    async def complete_ui_suite_item(
        self, task_id: str, item_id: str, body: WorkerTaskEventRequest
    ) -> dict:
        task = await find_task(self.repository.session, "ui", task_id)
        ensure_worker_match(task, body.worker_id)
        ensure_task_id(task, body)
        item = await self.repository.get_ui_item(item_id)
        if item is None:
            raise ErrNotFound
        item.status = final_run_status(body.status)
        item.snapshot_json = body.snapshot_json or item.snapshot_json
        item.step_results_json = body.step_results or item.step_results_json
        item.current_url = body.current_url or item.current_url
        item.error_message = body.error_message or ""
        item.finished_at = parse_event_time(body.finished_at) or datetime.now(UTC)
        if body.duration_ms is not None:
            item.duration_ms = body.duration_ms
        await update_ui_item_counts(self.repository.session, item.suite_run_id)
        await self.repository.commit()
        return {"taskId": task_id, "itemId": item_id, "status": item.status}

    async def list_project_skills(self, project_id: str) -> dict:
        rows = await self.repository.list_project_skills(project_id)
        return {
            "projectId": project_id,
            "skills": [project_skill_worker_payload(row) for row in rows],
        }

    async def _ai_worker_task(self, task_id: str):
        if hasattr(self.repository, "get_worker_task"):
            task = await self.repository.get_worker_task("ai", task_id)
            if task is None:
                raise ErrNotFound
            return task
        return await find_task(self.repository.session, "ai", task_id)


    async def llm_credentials(self, task_id: str) -> dict:
        task = await find_task(self.repository.session, "ai", task_id)
        connection = None
        if task.llm_connection_id:
            connection = await self.repository.get_llm_connection(task.llm_connection_id)
        return llm_credentials_payload(task_id, connection)

    async def requirement_document(self, task_id: str):
        task = await self._ai_worker_task(task_id)
        if task.task_type not in {
            "requirement_analysis", "functional_case_generate", "ui_case_generate"
        }:
            raise ErrNotFound
        run = await self.repository.get_ai_run(task.run_id)
        if run is None or not run.requirement_id:
            raise ErrNotFound
        if (
            task.task_type == "ui_case_generate"
            and run.task_id != task.generate_task_id
        ):
            raise ErrNotFound
        requirement = await self.repository.get_requirement(run.requirement_id)
        if requirement is None or not requirement.document_storage_path:
            raise ErrNotFound
        return requirement

    async def source_archive(self, task_id: str):
        task = await self._ai_worker_task(task_id)
        if task.task_type != "ui_case_generate":
            raise ErrNotFound
        run = await self.repository.get_ai_run(task.run_id)
        if (
            run is None
            or run.task_id != task.generate_task_id
            or not run.task_id
        ):
            raise ErrNotFound
        archive = await self.repository.get_source_archive(run.task_id)
        if archive is None:
            raise ErrNotFound
        return archive


    async def progress(self, task_id: str, body: WorkerProgressRequest) -> dict:
        task = await find_task(self.repository.session, "ai", task_id)
        if not body.worker_id.strip():
            raise ErrBadRequest
        if task.worker_id and task.worker_id != body.worker_id:
            raise ErrForbidden
        if body.task_id and body.task_id != task.task_id:
            raise ErrBadRequest
        run = await self.repository.get_ai_run(task.run_id)
        if run:
            if body.run_id and body.run_id != run.run_id:
                raise ErrBadRequest
            now = datetime.now(UTC)
            next_task_status = "running"
            next_run_status = "running"
            next_stage_status = run.stage_status
            if run.checkpoint_enabled and body.stage_status == "waiting_review":
                if not body.current_stage or body.current_stage != run.current_stage:
                    raise ErrBadRequest
                if run.current_stage not in AI_WAITING_REVIEW_STAGES:
                    raise ErrBadRequest
                next_task_status = "success"
                next_run_status = "waiting_review"
                next_stage_status = "waiting_review"
            elif run.checkpoint_enabled and body.stage_status:
                if not body.current_stage or body.current_stage != run.current_stage:
                    raise ErrBadRequest
                next_stage_status = body.stage_status

            task.status = next_task_status
            task.heartbeat_at = now
            task.lease_expires_at = now + timedelta(seconds=AI_LEASE_SECONDS)
            if next_task_status == "success":
                task.finished_at = now
                task.lease_expires_at = now
            run.status = next_run_status
            if body.current_stage is not None:
                run.current_stage = body.current_stage
            if run.checkpoint_enabled:
                run.stage_status = next_stage_status
            elif body.stage_status is not None:
                run.stage_status = body.stage_status
            if body.config_json is not None:
                run.config_json = body.config_json
            if body.result_yaml is not None:
                run.result_yaml = body.result_yaml
            if body.result_summary_json is not None:
                run.result_summary_json = body.result_summary_json
            if body.error_message is not None:
                task.error_message = body.error_message
                run.error_message = body.error_message
        await self.repository.commit()
        return {"taskId": task_id}
