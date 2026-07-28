from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from fastapi.encoders import jsonable_encoder

from testing_agent.core.errors import (
    ErrApiCaseGenerateTaskRunReviewed,
    ErrBadRequest,
    ErrForbidden,
    ErrNotFound,
)
from testing_agent.core.sid import new_id
from testing_agent.models.ai_generate_task import AiGenerateTask, ApiCaseGenerateTaskRun
from testing_agent.models.api_assert_rule import ApiAssertRule
from testing_agent.models.api_case import ApiCase
from testing_agent.models.api_extract_rule import ApiExtractRule
from testing_agent.models.function_test_case import FunctionTestCase
from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.models.worker_task import WorkerTask
from testing_agent.repositories.ai_generate_task import AiGenerateTaskRepository
from testing_agent.repositories.sprint_daily_metrics import SprintDailyMetricsRepository
from testing_agent.schemas.requirement import normalize_document_type
from testing_agent.services.api_collection import (
    import_items,
    int_value,
    normalize_import_body_type,
    normalize_import_method,
    normalize_json_value,
    parse_import_payload,
    require_string_map,
    validate_api_collection_import_payload,
)
from testing_agent.services.common import list_payload
from testing_agent.services.requirement import dump_requirement
from testing_agent.services.sprint_daily_metrics import SprintDailyMetricsService
from testing_agent.services.test_report_pdf import markdown_to_pdf_bytes


def task_type_for(kind: str) -> str:
    if kind == "function":
        return "functional_case_generate"
    if kind == "requirement_analysis":
        return "requirement_analysis"
    if kind == "test_report":
        return "test_report_generate"
    return "api_case_generate"


FUNCTION_CASE_REVIEWABLE_STAGES = {"requirement_analysis", "case_names"}
FUNCTION_CASE_REVIEW_READY_STATUSES = {"waiting_review", "saved"}
FUNCTION_CASE_NEXT_STAGE = {
    "requirement_analysis": "case_names",
    "case_names": "detailed_cases",
}
REQUIREMENT_ANALYSIS_INITIAL_STAGE = "extracting_text"
REQUIREMENT_ANALYSIS_FINAL_STAGE = "feature_understanding"
REQUIREMENT_ANALYSIS_FINAL_RUN_STAGES = {REQUIREMENT_ANALYSIS_FINAL_STAGE, "completed"}
REQUIREMENT_ANALYSIS_REVIEWABLE_STAGES = {"extracting_text", "writing_requirement"}
REQUIREMENT_ANALYSIS_REVIEW_READY_STATUSES = {"waiting_review", "saved"}
REQUIREMENT_ANALYSIS_NEXT_STAGE = {
    "extracting_text": "writing_requirement",
    "writing_requirement": "feature_understanding",
}
REVISION_INSTRUCTION_FIELD = "revisionInstruction"
DEFAULT_FUNCTION_CASE_MODULE = "未分组"
MAX_IMPORTED_SUITE_ID_SUMMARY_LENGTH = 180


def next_function_case_stage(stage: str) -> str | None:
    return FUNCTION_CASE_NEXT_STAGE.get(stage)


def next_requirement_analysis_stage(stage: str) -> str | None:
    return REQUIREMENT_ANALYSIS_NEXT_STAGE.get(stage)


def dump_task(task: AiGenerateTask) -> dict[str, Any]:
    return {
        "taskId": task.task_id,
        "taskType": task.task_type,
        "name": task.name,
        "projectId": task.project_id,
        "sprintId": task.sprint_id,
        "requirementId": task.requirement_id,
        "creatorUserId": task.creator_user_id,
        "sourceType": task.source_type,
        "sourceContent": task.source_content,
        "instruction": task.instruction,
    }


def dump_run(run: ApiCaseGenerateTaskRun) -> dict[str, Any]:
    return {
        "runId": run.run_id,
        "taskId": run.task_id,
        "requirementId": run.requirement_id,
        "sprintId": run.sprint_id,
        "projectId": run.project_id,
        "triggerUserId": run.trigger_user_id,
        "triggerType": run.trigger_type,
        "status": run.status,
        "checkpointEnabled": run.checkpoint_enabled,
        "currentStage": run.current_stage,
        "stageStatus": run.stage_status,
        "snapshotJson": run.snapshot_json or {},
        "errorMessage": run.error_message,
        "configJson": run.config_json or {},
        "resultYaml": run.result_yaml,
        "resultSummaryJson": run.result_summary_json or {},
        "reviewStatus": run.review_status,
        "importedCollectionId": run.imported_collection_id,
        "reviewerUserId": run.reviewer_user_id,
        "reviewedAt": run.reviewed_at,
        "reviewComment": run.review_comment,
        "durationMs": run.duration_ms,
    }


def requirement_source_content(requirement: Any) -> str:
    document_content = str(getattr(requirement, "document_content", "") or "")
    if document_content.strip():
        return document_content
    storage_path = str(getattr(requirement, "document_storage_path", "") or "")
    if not storage_path:
        return document_content

    path = Path(storage_path)
    document_type = normalize_document_type(
        str(getattr(requirement, "document_type", "") or "text")
    )
    if document_type == "text" and path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return document_content


def requirement_document_download_url(requirement: Any, requirement_id: str) -> str:
    document_download_url = str(getattr(requirement, "document_download_url", "") or "")
    if document_download_url:
        return document_download_url

    resolved_requirement_id = str(
        getattr(requirement, "requirement_id", "") or requirement_id or ""
    )
    if not resolved_requirement_id:
        return ""
    return f"/v1/requirements/{resolved_requirement_id}/download"


def worker_requirement_document_download_url(worker_task_id: str) -> str:
    return f"/internal/ai-worker/tasks/{worker_task_id}/requirement-document"


def build_test_report_run_snapshot(
    task: AiGenerateTask,
    run_id: str,
    snapshot_date: str,
    daily_metrics: dict[str, Any],
    llm_connection_id: str,
    instruction: str | None = None,
) -> dict[str, Any]:
    return {
        "taskId": task.task_id,
        "runId": run_id,
        "taskType": task.task_type,
        "name": task.name,
        "projectId": task.project_id,
        "sprintId": task.sprint_id,
        "requirementId": task.requirement_id,
        "snapshotDate": snapshot_date,
        "llmConnectionId": llm_connection_id,
        "dailyMetrics": jsonable_encoder(daily_metrics),
        "instruction": task.instruction if instruction is None else instruction,
    }


async def build_generate_run_snapshot(
    repository: AiGenerateTaskRepository,
    kind: str,
    task: AiGenerateTask,
    run_id: str,
    instruction: str | None = None,
    worker_task_id: str | None = None,
) -> dict[str, Any]:
    source_content = task.source_content
    document_type = ""
    document_download_url = ""
    uses_requirement_document = False
    if kind in {"function", "requirement_analysis"}:
        requirement = await repository.get_requirement(task.requirement_id)
        if requirement is not None:
            uses_requirement_document = True
            document_type = normalize_document_type(str(requirement.document_type or "text"))
            document_download_url = (
                worker_requirement_document_download_url(worker_task_id)
                if worker_task_id
                else requirement_document_download_url(requirement, str(task.requirement_id or ""))
            )
            source_content = requirement_source_content(requirement)
            if not source_content and document_type == "docx":
                source_content = document_download_url
    snapshot = {
        "taskId": task.task_id,
        "runId": run_id,
        "taskType": task.task_type,
        "name": task.name,
        "projectId": task.project_id,
        "sprintId": task.sprint_id,
        "requirementId": task.requirement_id,
        "sourceContent": source_content,
        "instruction": task.instruction if instruction is None else instruction,
    }
    if uses_requirement_document:
        snapshot["documentType"] = document_type
        snapshot["documentDownloadUrl"] = document_download_url
    else:
        snapshot["sourceType"] = task.source_type
    return snapshot


def generated_payload(run: ApiCaseGenerateTaskRun | Any) -> dict[str, Any]:
    raw = run.result_yaml or ""
    if not raw.strip():
        raise ErrBadRequest
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ErrBadRequest from exc
    return parse_import_payload(data)


def generated_api_cases(run: ApiCaseGenerateTaskRun | Any) -> list[dict[str, Any]]:
    return [
        item
        for item in import_items(generated_payload(run), "cases", "apiCases")
        if isinstance(item, dict)
    ]


def generated_function_suites(run: ApiCaseGenerateTaskRun | Any) -> list[dict[str, Any]]:
    payload = generated_payload(run)
    raw_suites = payload.get("suites")
    if isinstance(raw_suites, list):
        return [suite for suite in raw_suites if isinstance(suite, dict)]
    cases = [
        item
        for item in import_items(payload, "cases", "functionCases", "testcases")
        if isinstance(item, dict)
    ]
    return [{"name": "AI Generated", "cases": cases}] if cases else []


def generated_function_cases(run: ApiCaseGenerateTaskRun | Any) -> list[dict[str, Any]]:
    payload = generated_payload(run)
    cases = [
        item
        for item in import_items(payload, "cases", "functionCases", "testcases")
        if isinstance(item, dict)
    ]
    if cases:
        return cases

    result: list[dict[str, Any]] = []
    raw_suites = payload.get("suites")
    if isinstance(raw_suites, list):
        for suite in raw_suites:
            if not isinstance(suite, dict):
                continue
            suite_name = str(suite.get("name") or "")
            suite_cases = suite.get("cases") if isinstance(suite.get("cases"), list) else []
            for item in suite_cases:
                if not isinstance(item, dict):
                    continue
                case = dict(item)
                if not case.get("case_module") and not case.get("module"):
                    case["module"] = suite_name
                result.append(case)
    return result


def first_present(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in item:
            return item[key]
    return None


def import_lines(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(line).strip() for line in value)
    return str(value).strip()


def normalize_function_case_module(value: Any) -> str:
    module = str(value or "").strip()
    return module or DEFAULT_FUNCTION_CASE_MODULE


def normalize_generated_function_case(item: dict[str, Any], index: int) -> dict[str, Any]:
    module = normalize_function_case_module(first_present(item, "case_module", "module"))
    title = str(first_present(item, "case_title", "title", "name") or "").strip()
    priority = str(first_present(item, "priority") or "")
    case_type = str(first_present(item, "case_type", "caseType") or "")
    if (
        not title
        or len(title) > 255
        or len(module) > 120
        or len(priority) > 20
        or len(case_type) > 50
    ):
        raise ErrBadRequest
    return {
        "module": module,
        "title": title,
        "preconditions": import_lines(first_present(item, "precondition", "preconditions")),
        "steps": import_lines(first_present(item, "test_steps", "steps")),
        "expected_results": import_lines(
            first_present(item, "expected_results", "expectedResults")
        ),
        "priority": priority,
        "case_type": case_type,
        "order_no": int(first_present(item, "orderNo", "order_no") or index),
    }


def compact_imported_suite_ids(suite_ids: list[str]) -> str:
    if not suite_ids:
        return ""
    joined = ",".join(suite_ids)
    if len(joined) <= MAX_IMPORTED_SUITE_ID_SUMMARY_LENGTH:
        return joined
    summary = f"{suite_ids[0]},+{len(suite_ids) - 1}"
    if len(summary) <= MAX_IMPORTED_SUITE_ID_SUMMARY_LENGTH:
        return summary
    if len(suite_ids[0]) <= MAX_IMPORTED_SUITE_ID_SUMMARY_LENGTH:
        return suite_ids[0]
    return suite_ids[0][:MAX_IMPORTED_SUITE_ID_SUMMARY_LENGTH]


def is_ai_run_reviewable(status: str) -> bool:
    return status in {"success", "failed", "error", "canceled"}


def bool_value(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def normalize_config_json(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ErrBadRequest from exc
        if isinstance(parsed, dict):
            return parsed
    raise ErrBadRequest


def normalize_function_stage_config(stage: str, value: Any) -> dict[str, Any]:
    config = dict(normalize_config_json(value))
    if stage == "case_names" and "categories" in config:
        case_names = config.get("caseNames")
        if not isinstance(case_names, dict):
            case_names = {}
        config["caseNames"] = {**case_names, "categories": config.pop("categories")}
    return config


def requirement_analysis_import_content(run: ApiCaseGenerateTaskRun | Any) -> str:
    result_yaml = str(run.result_yaml or "").strip()
    if result_yaml:
        return result_yaml
    summary = run.result_summary_json
    if isinstance(summary, str):
        summary_text = summary.strip()
        if summary_text:
            return summary_text
    elif summary:
        return json.dumps(summary, ensure_ascii=False, separators=(",", ":"))
    raise ErrBadRequest


class AiGenerateTaskService:
    def __init__(
        self,
        repository: AiGenerateTaskRepository,
        sprint_daily_metrics_service: SprintDailyMetricsService | None = None,
    ):
        self.repository = repository
        if sprint_daily_metrics_service is None and hasattr(repository, "session"):
            sprint_daily_metrics_service = SprintDailyMetricsService(
                SprintDailyMetricsRepository(repository.session)
            )
        self.sprint_daily_metrics_service = sprint_daily_metrics_service

    async def ensure_project_owner(self, user_id: str, project_id: str) -> None:
        project = await self.repository.get_project(project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden

    async def ensure_sprint_owner(self, user_id: str, sprint_id: str) -> None:
        sprint = await self.repository.get_sprint(sprint_id)
        if sprint is None:
            raise ErrNotFound
        await self.ensure_project_owner(user_id, sprint.project_id)

    async def ensure_requirement_owner(self, user_id: str, requirement_id: str) -> None:
        requirement = await self.repository.get_requirement(requirement_id)
        if requirement is None:
            raise ErrNotFound
        await self.ensure_sprint_owner(user_id, requirement.sprint_id)

    async def ensure_collection_owner(self, user_id: str, collection_id: str) -> None:
        collection = await self.repository.get_collection(collection_id)
        if collection is None:
            raise ErrNotFound
        await self.ensure_requirement_owner(user_id, collection.requirement_id)

    async def owned_task(
        self, user_id: str, task_id: str, kind: str | None = None
    ) -> AiGenerateTask:
        task = await self.repository.get_task(task_id)
        if task is None:
            raise ErrNotFound
        if kind and task.task_type != task_type_for(kind):
            raise ErrNotFound
        if task.creator_user_id != user_id:
            await self.ensure_project_owner(user_id, task.project_id)
        return task

    async def owned_run(
        self, user_id: str, run_id: str, kind: str | None = None
    ) -> ApiCaseGenerateTaskRun:
        run = await self.repository.get_run(run_id)
        if run is None:
            raise ErrNotFound
        task = await self.owned_task(user_id, run.task_id, kind)
        if task.project_id != run.project_id:
            raise ErrForbidden
        return run

    async def create(self, kind: str, project_id: str, body: dict[str, Any], user_id: str) -> dict:
        await self.ensure_project_owner(user_id, project_id)
        sprint_id = str(body.get("sprintId") or body.get("sprint_id") or "")
        requirement_id = str(body.get("requirementId") or body.get("requirement_id") or "")
        requirement = None
        if kind == "requirement_analysis":
            if not requirement_id:
                raise ErrBadRequest
            requirement = await self.repository.get_requirement(requirement_id)
            if requirement is None:
                raise ErrNotFound
            sprint = await self.repository.get_sprint(requirement.sprint_id)
            if sprint is None or sprint.project_id != project_id:
                raise ErrNotFound
            sprint_id = requirement.sprint_id
        if kind == "test_report":
            if not sprint_id:
                raise ErrBadRequest
            sprint = await self.repository.get_sprint(sprint_id)
            if sprint is None or sprint.project_id != project_id:
                raise ErrNotFound
            existing = await self.repository.get_active_task_by_project_sprint_type(
                project_id, sprint_id, task_type_for(kind)
            )
            if existing is not None:
                raise ErrBadRequest
        if sprint_id:
            await self.ensure_sprint_owner(user_id, sprint_id)
        if requirement_id:
            await self.ensure_requirement_owner(user_id, requirement_id)
        task = AiGenerateTask(
            task_id=new_id(),
            task_type=task_type_for(kind),
            name=str(
                body.get("name")
                or (
                    f"{requirement.name} analysis"
                    if kind == "requirement_analysis" and requirement is not None
                    else (
                        "test-report-generate-task"
                        if kind == "test_report"
                        else f"{kind}-case-generate-task"
                    )
                )
            ),
            project_id=project_id,
            sprint_id=sprint_id,
            requirement_id=requirement_id,
            creator_user_id=user_id,
            source_type=str(
                requirement.document_type
                if kind == "requirement_analysis" and requirement is not None
                else (
                    "daily_metrics"
                    if kind == "test_report"
                    else body.get("sourceType") or body.get("source_type") or "manual"
                )
            ),
            source_content=str(
                requirement.document_content
                if kind == "requirement_analysis" and requirement is not None
                else body.get("sourceContent") or body.get("source_content") or ""
            ),
            instruction=str(body.get("instruction") or ""),
        )
        self.repository.add(task)
        await self.repository.commit()
        await self.repository.refresh(task)
        return dump_task(task)

    async def list(self, kind: str, project_id: str, user_id: str) -> dict[str, Any]:
        await self.ensure_project_owner(user_id, project_id)
        rows = await self.repository.list_tasks(project_id, task_type_for(kind))
        return list_payload([dump_task(row) for row in rows])

    async def get(self, kind: str, task_id: str, user_id: str) -> dict:
        return dump_task(await self.owned_task(user_id, task_id, kind))

    async def update(self, kind: str, task_id: str, body: dict[str, Any], user_id: str) -> dict:
        task = await self.owned_task(user_id, task_id, kind)
        field_map = {
            "name": "name",
            "sourceType": "source_type",
            "source_type": "source_type",
            "sourceContent": "source_content",
            "source_content": "source_content",
            "instruction": "instruction",
        }
        for key, attr in field_map.items():
            if key in body:
                setattr(task, attr, body[key])
        await self.repository.commit()
        await self.repository.refresh(task)
        return dump_task(task)

    async def delete(self, kind: str, task_id: str, user_id: str) -> dict:
        task = await self.owned_task(user_id, task_id, kind)
        task.deleted_at = datetime.now(UTC)
        await self.repository.commit()
        return {}

    async def test_report_task_for_run(
        self, project_id: str, body: dict[str, Any], user_id: str
    ) -> AiGenerateTask:
        await self.ensure_project_owner(user_id, project_id)
        sprint_id = str(body.get("sprintId") or body.get("sprint_id") or "")
        if not sprint_id:
            raise ErrBadRequest
        sprint = await self.repository.get_sprint(sprint_id)
        if sprint is None or sprint.project_id != project_id:
            raise ErrNotFound
        existing = await self.repository.get_active_task_by_project_sprint_type(
            project_id, sprint_id, task_type_for("test_report")
        )
        if existing is not None:
            return existing
        sprint_name = str(getattr(sprint, "name", "") or "").strip()
        return AiGenerateTask(
            task_id=new_id(),
            task_type=task_type_for("test_report"),
            name=f"{sprint_name} 测试报告生成" if sprint_name else "测试报告生成",
            project_id=project_id,
            sprint_id=sprint_id,
            requirement_id="",
            creator_user_id=user_id,
            source_type="daily_metrics",
            source_content="",
            instruction="",
        )

    async def run_test_report(
        self, project_id: str, body: dict[str, Any] | None, user_id: str
    ) -> dict:
        body = body or {}
        llm_connection_id = str(body.get("connectionId") or body.get("llmConnectionId") or "")
        snapshot_date = str(body.get("snapshotDate") or body.get("snapshot_date") or "")
        if not llm_connection_id or not snapshot_date:
            raise ErrBadRequest
        task = await self.test_report_task_for_run(project_id, body, user_id)
        run_id = new_id()
        worker_task_id = new_id()
        if self.sprint_daily_metrics_service is None:
            raise ErrBadRequest
        daily_metrics = await self.sprint_daily_metrics_service.get(
            task.sprint_id, snapshot_date, user_id
        )
        run_instruction = body.get("instruction")
        snapshot = build_test_report_run_snapshot(
            task,
            run_id,
            snapshot_date,
            daily_metrics,
            llm_connection_id,
            None if run_instruction is None else str(run_instruction),
        )
        run = ApiCaseGenerateTaskRun(
            run_id=run_id,
            task_id=task.task_id,
            requirement_id="",
            sprint_id=task.sprint_id,
            project_id=task.project_id,
            trigger_user_id=user_id,
            trigger_type=str(body.get("triggerType") or "manual"),
            status="pending",
            checkpoint_enabled=False,
            current_stage="",
            stage_status="",
            snapshot_json=snapshot,
            config_json=normalize_config_json(body.get("configJson")),
            result_summary_json={},
        )
        worker_task = WorkerTask(
            domain="ai",
            task_id=worker_task_id,
            task_type=task.task_type,
            run_id=run.run_id,
            generate_task_id=task.task_id,
            llm_connection_id=llm_connection_id,
            status="pending",
        )
        rows: list[object] = [run, worker_task]
        if getattr(task, "id", None) is None:
            rows.insert(0, task)
        self.repository.add_all(rows)
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def list_test_report_runs(
        self, project_id: str, sprint_id: str, user_id: str
    ) -> dict[str, Any]:
        await self.ensure_project_owner(user_id, project_id)
        sprint = await self.repository.get_sprint(sprint_id)
        if sprint is None or sprint.project_id != project_id:
            raise ErrNotFound
        rows = await self.repository.list_runs_by_project_sprint_task_type(
            project_id, sprint_id, task_type_for("test_report")
        )
        return list_payload([dump_run(row) for row in rows])

    async def export_test_report_pdf(self, run_id: str, user_id: str) -> tuple[bytes, str]:
        run = await self.owned_run(user_id, run_id, "test_report")
        markdown = str(run.result_yaml or "").strip()
        if not markdown:
            raise ErrBadRequest
        snapshot = run.snapshot_json if isinstance(run.snapshot_json, dict) else {}
        title = str(snapshot.get("name") or "测试报告")
        filename = f"test-report-{run.run_id}.pdf"
        return markdown_to_pdf_bytes(markdown, title=title), filename

    async def run(self, kind: str, task_id: str, body: dict[str, Any] | None, user_id: str) -> dict:
        task = await self.owned_task(user_id, task_id, kind)
        body = body or {}
        llm_connection_id = str(body.get("connectionId") or body.get("llmConnectionId") or "")
        if not llm_connection_id:
            raise ErrBadRequest
        run_id = new_id()
        worker_task_id = new_id()
        run_instruction = body.get("instruction")
        if kind == "test_report":
            snapshot_date = str(body.get("snapshotDate") or body.get("snapshot_date") or "")
            if not snapshot_date:
                raise ErrBadRequest
            if self.sprint_daily_metrics_service is None:
                raise ErrBadRequest
            daily_metrics = await self.sprint_daily_metrics_service.get(
                task.sprint_id, snapshot_date, user_id
            )
            snapshot = build_test_report_run_snapshot(
                task,
                run_id,
                snapshot_date,
                daily_metrics,
                llm_connection_id,
                None if run_instruction is None else str(run_instruction),
            )
        else:
            snapshot = await build_generate_run_snapshot(
                self.repository,
                kind,
                task,
                run_id,
                None if run_instruction is None else str(run_instruction),
                worker_task_id=worker_task_id,
            )
        checkpoint_enabled = (
            True if kind == "requirement_analysis" else bool(body.get("checkpointEnabled", False))
        )
        current_stage = ""
        if checkpoint_enabled:
            if kind == "function":
                current_stage = "requirement_analysis"
            elif kind == "requirement_analysis":
                current_stage = REQUIREMENT_ANALYSIS_INITIAL_STAGE
        stage_status = "pending" if current_stage else ""
        run = ApiCaseGenerateTaskRun(
            run_id=run_id,
            task_id=task.task_id,
            requirement_id=task.requirement_id,
            sprint_id=task.sprint_id,
            project_id=task.project_id,
            trigger_user_id=user_id,
            trigger_type=str(body.get("triggerType") or "manual"),
            status="pending",
            checkpoint_enabled=checkpoint_enabled,
            current_stage=current_stage,
            stage_status=stage_status,
            snapshot_json=snapshot,
            config_json=normalize_config_json(body.get("configJson")),
            result_summary_json={},
        )
        worker_task = WorkerTask(
            domain="ai",
            task_id=worker_task_id,
            task_type=task.task_type,
            run_id=run.run_id,
            generate_task_id=task.task_id,
            llm_connection_id=llm_connection_id,
            status="pending",
        )
        self.repository.add_all([run, worker_task])
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def list_runs(self, kind: str, task_id: str, user_id: str) -> dict[str, Any]:
        await self.owned_task(user_id, task_id, kind)
        rows = await self.repository.list_runs(task_id)
        return list_payload([dump_run(row) for row in rows])

    async def import_requirement_analysis_run(self, run_id: str, user_id: str) -> dict:
        run = await self.owned_run(user_id, run_id, "requirement_analysis")
        if run.status != "success":
            raise ErrBadRequest
        requirement = await self.repository.get_requirement(run.requirement_id)
        if requirement is None:
            raise ErrNotFound
        await self.ensure_requirement_owner(user_id, requirement.requirement_id)
        requirement.document_content = requirement_analysis_import_content(run)
        await self.repository.commit()
        await self.repository.refresh(requirement)
        return dump_requirement(requirement)

    def generated_payload(self, run: ApiCaseGenerateTaskRun) -> dict[str, Any]:
        return generated_payload(run)

    async def import_generated_api_cases(
        self, user_id: str, run: ApiCaseGenerateTaskRun, collection_id: str
    ) -> None:
        await self.ensure_collection_owner(user_id, collection_id)
        cases = await validate_api_collection_import_payload(
            self.repository, collection_id, generated_payload(run)
        )
        for index, item in enumerate(cases):
            case_id = new_id()
            body_type = normalize_import_body_type(item.get("bodyType"))
            body_json = normalize_json_value(item.get("bodyJson"))
            body_text = str(item.get("bodyText") or "")
            if body_type == "raw":
                body_json = None
            elif body_type == "none":
                body_json = None
                body_text = ""
            self.repository.add(
                ApiCase(
                    case_id=case_id,
                    collection_id=collection_id,
                    name=str(item.get("name") or f"API Case {index + 1}"),
                    description=str(item.get("description") or ""),
                    enabled=bool_value(item.get("enabled"), True),
                    order_no=int_value(item.get("orderNo"), 0),
                    method=normalize_import_method(item.get("method")),
                    url_template=str(item.get("urlTemplate") or ""),
                    headers_json=require_string_map(item.get("headers"), f"cases[{index}].headers"),
                    query_json=require_string_map(item.get("query"), f"cases[{index}].query"),
                    body_type=body_type,
                    body_json=body_json,
                    body_text=body_text,
                    timeout_ms=int_value(item.get("timeoutMs"), 5000),
                    continue_on_failure=bool_value(item.get("continueOnFailure"), False),
                )
            )
            extract_rules = item.get("extractRules")
            if isinstance(extract_rules, list):
                for rule_index, rule in enumerate(extract_rules):
                    if not isinstance(rule, dict):
                        continue
                    self.repository.add(
                        ApiExtractRule(
                            extract_rule_id=new_id(),
                            case_id=case_id,
                            name=str(rule.get("name") or f"Extract Rule {rule_index + 1}"),
                            enabled=bool_value(rule.get("enabled"), True),
                            order_no=int(rule.get("orderNo", rule_index)),
                            source=str(rule.get("source") or ""),
                            source_expr=str(rule.get("sourceExpr") or ""),
                            var_key=str(rule.get("varKey") or ""),
                            default_value=str(rule.get("defaultValue") or ""),
                        )
                    )
            assert_rules = item.get("assertRules")
            if isinstance(assert_rules, list):
                for rule_index, rule in enumerate(assert_rules):
                    if not isinstance(rule, dict):
                        continue
                    self.repository.add(
                        ApiAssertRule(
                            assert_rule_id=new_id(),
                            case_id=case_id,
                            name=str(rule.get("name") or f"Assert Rule {rule_index + 1}"),
                            enabled=bool_value(rule.get("enabled"), True),
                            order_no=int(rule.get("orderNo", rule_index)),
                            assert_source=str(rule.get("assertSource") or ""),
                            target_expr=str(rule.get("targetExpr") or ""),
                            comparator=str(rule.get("comparator") or ""),
                            expected_value=str(rule.get("expectedValue") or ""),
                        )
                    )

    async def import_generated_function_cases(
        self, user_id: str, run: ApiCaseGenerateTaskRun
    ) -> list[str]:
        await self.ensure_requirement_owner(user_id, run.requirement_id)
        cases = generated_function_cases(run)
        if not cases:
            raise ErrBadRequest

        suites_by_name: dict[str, FunctionTestSuite] = {}
        max_order_by_suite_id: dict[str, int] = {}
        suite_ids: list[str] = []
        suite_id_set: set[str] = set()

        for case_index, raw_item in enumerate(cases):
            item = normalize_generated_function_case(raw_item, case_index)
            suite_name = item["module"]
            suite = suites_by_name.get(suite_name)
            if suite is None:
                suite = await self.repository.get_function_suite_by_requirement_and_name(
                    run.requirement_id, suite_name
                )
                if suite is None:
                    suite = FunctionTestSuite(
                        suite_id=new_id(),
                        requirement_id=run.requirement_id,
                        name=suite_name,
                        description="",
                    )
                    self.repository.add(suite)
                suites_by_name[suite_name] = suite
            if suite.suite_id not in suite_id_set:
                suite_ids.append(suite.suite_id)
                suite_id_set.add(suite.suite_id)

            existing = await self.repository.get_function_case_by_suite_and_title(
                suite.suite_id, item["title"]
            )
            if existing is not None:
                existing.module = suite.name
                existing.preconditions = item["preconditions"]
                existing.steps = item["steps"]
                existing.expected_results = item["expected_results"]
                existing.priority = item["priority"]
                existing.case_type = item["case_type"]
                continue

            max_order = max_order_by_suite_id.get(suite.suite_id)
            if max_order is None:
                max_order = await self.repository.max_function_case_order_by_suite(suite.suite_id)
            max_order += 1
            max_order_by_suite_id[suite.suite_id] = max_order

            self.repository.add(
                FunctionTestCase(
                    case_id=new_id(),
                    suite_id=suite.suite_id,
                    module=suite.name,
                    title=item["title"],
                    preconditions=item["preconditions"],
                    steps=item["steps"],
                    expected_results=item["expected_results"],
                    priority=item["priority"],
                    case_type=item["case_type"],
                    order_no=max_order,
                )
            )
        return suite_ids

    async def review(self, kind: str, run_id: str, body: dict[str, Any], user_id: str) -> dict:
        run = await self.owned_run(user_id, run_id, kind)
        if not is_ai_run_reviewable(run.status):
            raise ErrBadRequest
        if run.review_status != "pending":
            raise ErrApiCaseGenerateTaskRunReviewed
        action = str(
            body.get("action") or body.get("reviewStatus") or body.get("status") or "approve"
        )
        if action == "approved":
            action = "approve"
        if action == "rejected":
            action = "reject"
        run.review_comment = str(body.get("reviewComment") or body.get("comment") or "")
        run.reviewer_user_id = user_id
        run.reviewed_at = datetime.now(UTC)
        if action == "approve":
            if kind == "api":
                collection_id = str(body.get("collectionId") or body.get("collection_id") or "")
                if not collection_id:
                    raise ErrBadRequest
                await self.import_generated_api_cases(user_id, run, collection_id)
                run.imported_collection_id = collection_id
            else:
                suite_ids = await self.import_generated_function_cases(user_id, run)
                run.imported_collection_id = compact_imported_suite_ids(suite_ids)
            run.review_status = "approved"
        elif action == "reject":
            run.review_status = "rejected"
            run.imported_collection_id = ""
        else:
            raise ErrBadRequest
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def save_stage_output(self, run_id: str, body: dict[str, Any], user_id: str) -> dict:
        run = await self.owned_run(user_id, run_id, "function")
        current_stage = str(body.get("currentStage") or body.get("stage") or run.current_stage)
        if (
            run.checkpoint_enabled
            and run.status == "waiting_review"
            and current_stage != run.current_stage
        ):
            raise ErrBadRequest
        run.current_stage = current_stage
        if run.checkpoint_enabled and run.status == "waiting_review":
            run.stage_status = "waiting_review"
        else:
            run.stage_status = str(body.get("stageStatus") or "saved")
        run.snapshot_json = body.get("snapshotJson") or run.snapshot_json
        if "configJson" in body:
            run.config_json = {
                **normalize_config_json(run.config_json),
                **normalize_function_stage_config(current_stage, body.get("configJson")),
            }
        run.result_yaml = str(body.get("resultYaml") or run.result_yaml)
        run.result_summary_json = body.get("resultSummaryJson") or run.result_summary_json
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def save_requirement_analysis_stage_output(
        self, run_id: str, body: dict[str, Any], user_id: str
    ) -> dict:
        run = await self.owned_run(user_id, run_id, "requirement_analysis")
        current_stage = str(body.get("currentStage") or body.get("stage") or run.current_stage)
        is_review_stage = (
            run.checkpoint_enabled
            and current_stage == run.current_stage
            and current_stage in REQUIREMENT_ANALYSIS_REVIEWABLE_STAGES
            and run.status == "waiting_review"
            and run.stage_status in REQUIREMENT_ANALYSIS_REVIEW_READY_STATUSES
        )
        is_final_stage = (
            run.status == "success"
            and current_stage == REQUIREMENT_ANALYSIS_FINAL_STAGE
            and run.current_stage in REQUIREMENT_ANALYSIS_FINAL_RUN_STAGES
        )
        if not (is_review_stage or is_final_stage):
            raise ErrBadRequest
        if is_review_stage:
            run.stage_status = "waiting_review"
        if "configJson" in body:
            run.config_json = normalize_config_json(body.get("configJson"))
        run.snapshot_json = body.get("snapshotJson") or run.snapshot_json
        if "resultYaml" in body:
            run.result_yaml = str(body.get("resultYaml") or "")
        run.result_summary_json = body.get("resultSummaryJson") or run.result_summary_json
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def review_requirement_analysis_stage(
        self, run_id: str, body: dict[str, Any], user_id: str
    ) -> dict:
        run = await self.owned_run(user_id, run_id, "requirement_analysis")
        if (
            not run.checkpoint_enabled
            or run.status != "waiting_review"
            or run.stage_status not in REQUIREMENT_ANALYSIS_REVIEW_READY_STATUSES
        ):
            raise ErrBadRequest

        current_stage = str(body.get("currentStage") or body.get("stage") or "")
        if (
            current_stage != run.current_stage
            or current_stage not in REQUIREMENT_ANALYSIS_REVIEWABLE_STAGES
        ):
            raise ErrBadRequest

        action = str(
            body.get("action")
            or body.get("reviewStatus")
            or body.get("status")
            or body.get("stageStatus")
            or "approve"
        )
        if action == "approved":
            action = "approve"
        if action == "rejected":
            action = "reject"

        run.review_comment = str(body.get("reviewComment") or body.get("comment") or "")
        run.reviewer_user_id = user_id
        run.reviewed_at = datetime.now(UTC)
        if action == "approve":
            latest_task = await self.repository.get_latest_worker_task_by_run_id(run.run_id)
            next_stage = next_requirement_analysis_stage(run.current_stage)
            if latest_task is None or next_stage is None:
                raise ErrBadRequest
            if "configJson" in body:
                run.config_json = normalize_config_json(body.get("configJson"))
            run.status = "pending"
            run.current_stage = next_stage
            run.stage_status = "pending"
            run.error_message = ""
            self.repository.add(
                WorkerTask(
                    domain="ai",
                    task_id=new_id(),
                    task_type=task_type_for("requirement_analysis"),
                    run_id=run.run_id,
                    generate_task_id=run.task_id,
                    llm_connection_id=latest_task.llm_connection_id,
                    status="pending",
                )
            )
        elif action == "reject":
            run.status = "canceled"
            run.stage_status = "failed"
        else:
            raise ErrBadRequest
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def revise_requirement_analysis_stage(
        self, run_id: str, body: dict[str, Any], user_id: str
    ) -> dict:
        run = await self.owned_run(user_id, run_id, "requirement_analysis")

        current_stage = str(body.get("currentStage") or body.get("stage") or "")
        is_review_stage = (
            run.checkpoint_enabled
            and run.status == "waiting_review"
            and run.stage_status in REQUIREMENT_ANALYSIS_REVIEW_READY_STATUSES
            and current_stage == run.current_stage
            and current_stage in REQUIREMENT_ANALYSIS_REVIEWABLE_STAGES
        )
        is_final_stage = (
            run.status == "success"
            and current_stage == REQUIREMENT_ANALYSIS_FINAL_STAGE
            and run.current_stage in REQUIREMENT_ANALYSIS_FINAL_RUN_STAGES
        )
        if not is_review_stage and not is_final_stage:
            raise ErrBadRequest

        revision_instruction = str(
            body.get(REVISION_INSTRUCTION_FIELD) or body.get("revision_instruction") or ""
        ).strip()
        if not revision_instruction:
            raise ErrBadRequest

        latest_task = await self.repository.get_latest_worker_task_by_run_id(run.run_id)
        if latest_task is None:
            raise ErrBadRequest

        if "configJson" in body:
            run.config_json = normalize_config_json(body.get("configJson"))
        elif not isinstance(run.config_json, dict):
            run.config_json = normalize_config_json(run.config_json)
        if is_final_stage:
            result_yaml = str(body.get("resultYaml") or run.result_yaml or "").strip()
            if not result_yaml:
                raise ErrBadRequest
            run.config_json["resultYaml"] = str(body.get("resultYaml") or run.result_yaml or "")
        run.config_json[REVISION_INSTRUCTION_FIELD] = revision_instruction
        run.status = "pending"
        if is_final_stage:
            run.current_stage = REQUIREMENT_ANALYSIS_FINAL_STAGE
        run.stage_status = "pending"
        run.error_message = ""
        self.repository.add(
            WorkerTask(
                domain="ai",
                task_id=new_id(),
                task_type=task_type_for("requirement_analysis"),
                run_id=run.run_id,
                generate_task_id=run.task_id,
                llm_connection_id=latest_task.llm_connection_id,
                status="pending",
            )
        )
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def review_stage(self, run_id: str, body: dict[str, Any], user_id: str) -> dict:
        run = await self.owned_run(user_id, run_id, "function")
        if (
            not run.checkpoint_enabled
            or run.status != "waiting_review"
            or run.stage_status not in FUNCTION_CASE_REVIEW_READY_STATUSES
        ):
            raise ErrBadRequest

        current_stage = str(body.get("currentStage") or body.get("stage") or "")
        if (
            current_stage != run.current_stage
            or current_stage not in FUNCTION_CASE_REVIEWABLE_STAGES
        ):
            raise ErrBadRequest

        action = str(
            body.get("action")
            or body.get("reviewStatus")
            or body.get("status")
            or body.get("stageStatus")
            or "approve"
        )
        if action == "approved":
            action = "approve"
        if action == "rejected":
            action = "reject"

        if action == "approve":
            latest_task = await self.repository.get_latest_worker_task_by_run_id(run.run_id)
            next_stage = next_function_case_stage(run.current_stage)
            if latest_task is None or next_stage is None:
                raise ErrBadRequest
            run.status = "pending"
            run.current_stage = next_stage
            run.stage_status = "pending"
            run.error_message = ""
            self.repository.add(
                WorkerTask(
                    domain="ai",
                    task_id=new_id(),
                    task_type=task_type_for("function"),
                    run_id=run.run_id,
                    generate_task_id=run.task_id,
                    llm_connection_id=latest_task.llm_connection_id,
                    status="pending",
                )
            )
        elif action == "reject":
            run.status = "canceled"
            run.stage_status = "failed"
        else:
            raise ErrBadRequest
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)

    async def retry_stage(self, run_id: str, body: dict[str, Any] | None, user_id: str) -> dict:
        run = await self.owned_run(user_id, run_id, "function")
        run.stage_status = "retrying"
        if body and body.get("currentStage"):
            run.current_stage = str(body["currentStage"])
        await self.repository.commit()
        await self.repository.refresh(run)
        return dump_run(run)



