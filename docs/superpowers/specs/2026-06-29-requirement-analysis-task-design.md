# Requirement Analysis Task Design

## Context

The control plane already supports requirement records and AI generation tasks for API case generation and function case generation. Requirement records store user-entered or uploaded requirement content through `document_type` and `document_content`. AI generation tasks use a shared flow: create a task, run it with an LLM connection, enqueue a worker task, expose a run snapshot to the AI worker, and persist progress and final results.

The new capability adds a requirement analysis task. Users choose an existing requirement and publish an AI task. The AI worker performs the analysis and emits the agreed output format. The backend does not parse or normalize the analysis result in this phase.

## Goals

- Add a requirement analysis task type beside API case generation and function case generation.
- Let users create the analysis task by selecting an existing requirement.
- Use the selected requirement as the source of truth for document type and content at run time.
- Reuse the existing AI worker task queue, run lifecycle, progress reporting, and result persistence.
- Keep analysis output opaque to the backend. Store it as `result_yaml` and `result_summary_json` just like existing AI runs.

## Non-Goals

- Do not create structured requirement analysis tables.
- Do not import analysis output into test suites, API collections, or other business assets.
- Do not implement Word parsing in this task. Word or rich-text requirement ingestion remains part of requirement management.
- Do not change the AI worker authentication or claim/progress/completion contract beyond adding a new `taskType` value.

## API Design

Add a new public route group:

```text
POST /v1/projects/{projectId}/requirement-analysis-tasks
GET  /v1/projects/{projectId}/requirement-analysis-tasks
GET  /v1/requirement-analysis-tasks/{taskId}
PATCH /v1/requirement-analysis-tasks/{taskId}
DELETE /v1/requirement-analysis-tasks/{taskId}
POST /v1/requirement-analysis-tasks/{taskId}/run
GET  /v1/requirement-analysis-tasks/{taskId}/runs
GET  /v1/requirement-analysis-task-runs/{runId}
```

Create request shape:

```json
{
  "name": "Login requirement analysis",
  "sprintId": "sprint-1",
  "requirementId": "requirement-1",
  "instruction": "Focus on ambiguous rules and edge cases."
}
```

Run request shape matches existing AI generation tasks:

```json
{
  "connectionId": "llm-connection-1",
  "triggerType": "manual",
  "configJson": {}
}
```

The task response and run response should reuse the existing `dump_task` and `dump_run` shapes, with `taskType` set to `requirement_analysis`.

## Task Lifecycle

Creation validates project ownership, sprint ownership when `sprintId` is provided, and requirement ownership when `requirementId` is provided. For this task type, `requirementId` is required because the task should be created by selecting an existing requirement.

Running the task creates:

- one `ApiCaseGenerateTaskRun` row reused as the generic AI run record,
- one `WorkerTask` row with `domain = "ai"`,
- `WorkerTask.task_type = "requirement_analysis"`,
- a run snapshot containing the selected requirement document content.

The run snapshot should include:

```json
{
  "taskId": "task-1",
  "runId": "run-1",
  "taskType": "requirement_analysis",
  "name": "Login requirement analysis",
  "projectId": "project-1",
  "sprintId": "sprint-1",
  "requirementId": "requirement-1",
  "sourceType": "text",
  "sourceContent": "requirement document content",
  "instruction": "Focus on ambiguous rules and edge cases."
}
```

`sourceType` and `sourceContent` should be read from the selected requirement at run time. This keeps analysis aligned with the latest saved requirement content.

## Worker Contract

The AI worker claim response remains unchanged except that `taskType` may be `requirement_analysis`.

The AI worker snapshot endpoint continues to return:

```json
{
  "taskType": "requirement_analysis",
  "checkpointEnabled": false,
  "currentStage": "",
  "configJson": "{}",
  "run": {
    "...": "snapshot fields"
  }
}
```

The AI worker may report progress and completion through the existing internal endpoints. The backend stores `resultYaml`, `resultSummaryJson`, `errorMessage`, status, stage fields, and duration without interpreting the analysis content.

## Review Behavior

Requirement analysis runs do not need an import-on-approve flow in this phase. If a review endpoint is exposed later, approval should only mark the run as approved and keep the output attached to the run. The initial API surface does not need a review route.

## Implementation Notes

- Extend the task type mapping so `kind = "requirement_analysis"` maps to `task_type = "requirement_analysis"`.
- Allow the shared AI task service to create, list, get, update, delete, run, and list runs for this kind.
- Require `requirementId` when creating requirement analysis tasks.
- Build snapshots for requirement analysis using the requirement's `document_type` and `document_content`, matching the current function-case behavior.
- Add `handlers/requirement_analysis_task.py` and `routers/requirement_analysis_tasks.py` following the style of existing API/function AI task handlers.
- Include the new router in the FastAPI app.
- Add route compatibility tests and worker snapshot/claim tests for the new task type.

## Error Handling

- Missing or unauthorized project, sprint, or requirement returns the same errors as existing AI task creation.
- Creating a requirement analysis task without `requirementId` returns bad request.
- Running without an LLM connection continues to return bad request.
- If the selected requirement is deleted before run creation, run creation returns not found.
- If the selected requirement content is empty, the backend still publishes the task; the AI worker decides how to handle empty input.

## Testing

Add or update tests for:

- route registration for all requirement analysis task endpoints,
- create requires `requirementId`,
- create/list/get use `taskType = requirement_analysis`,
- run enqueues an AI worker task with `task_type = requirement_analysis`,
- snapshot includes the selected requirement's `documentType` and `documentContent`,
- AI worker claim still returns the existing Go-style payload with the new task type.

## Open Decisions

No open decisions remain for this phase. The analysis result is intentionally opaque to the backend, and structured output handling stays in the AI worker.
