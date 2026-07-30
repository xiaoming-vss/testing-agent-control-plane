from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from testing_agent.core.errors import (
    ErrBadRequest,
    ErrForbidden,
    ErrFunctionTestCaseImportInvalid,
    ErrNotFound,
    ErrResourceBindingInvalid,
    ErrResourceBindingNotFound,
    ErrZentaoRemoteResourceUnavailable,
    dynamic_error,
)
from testing_agent.core.sid import new_id
from testing_agent.models.function_test_case import FunctionTestCase
from testing_agent.models.function_test_suite import FunctionTestSuite
from testing_agent.models.resource_binding import ResourceBinding
from testing_agent.repositories.function_test_case import FunctionTestCaseRepository
from testing_agent.schemas.function_test_case import (
    FunctionCaseRequest,
    FunctionCaseResponse,
    ImportFunctionCasesToZentaoRequest,
)
from testing_agent.services.api_collection import (
    import_items,
    parse_import_payload,
    read_import_payload,
)
from testing_agent.services.common import apply_patch, dump, list_payload
from testing_agent.services.zentao_resource import parse_zentao_remote_id, truncate_error


class FunctionTestCaseService:
    def __init__(
        self,
        repository: FunctionTestCaseRepository,
        integration_connection_service: Any | None = None,
        zentao_resource_client: Any | None = None,
    ):
        self.repository = repository
        self.integration_connection_service = integration_connection_service
        self.zentao_resource_client = zentao_resource_client

    async def get_owned_suite(self, user_id: str, suite_id: str) -> FunctionTestSuite:
        suite = await self.repository.get_suite(suite_id)
        if suite is None:
            raise ErrNotFound
        requirement = await self.repository.get_requirement(suite.requirement_id)
        if requirement is None:
            raise ErrNotFound
        sprint = await self.repository.get_sprint(requirement.sprint_id)
        if sprint is None:
            raise ErrNotFound
        project = await self.repository.get_project(sprint.project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden
        return suite

    async def get_owned_entity(self, user_id: str, case_id: str) -> FunctionTestCase:
        case = await self.repository.get_case(case_id)
        if case is None:
            raise ErrNotFound
        await self.get_owned_suite(user_id, case.suite_id)
        return case

    async def create(self, user_id: str, suite_id: str, body: FunctionCaseRequest) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        case = FunctionTestCase(
            case_id=new_id(),
            suite_id=suite_id,
            **body.model_dump(by_alias=False),
        )
        self.repository.add(case)
        await self.repository.commit()
        await self.repository.refresh(case)
        return dump(FunctionCaseResponse, case)

    async def import_cases(self, user_id: str, suite_id: str, payload: Any, file: Any) -> dict:
        await self.get_owned_suite(user_id, suite_id)
        parsed = await read_import_payload(payload, file)
        created = 0
        for index, item in enumerate(import_items(parsed, "cases", "functionCases", "testcases")):
            if not isinstance(item, dict):
                continue
            self.repository.add(
                FunctionTestCase(
                    case_id=new_id(),
                    suite_id=suite_id,
                    module=str(item.get("module") or ""),
                    title=str(
                        item.get("title") or item.get("name") or f"Function Case {index + 1}"
                    ),
                    preconditions=str(
                        item.get("preconditions") or item.get("precondition") or ""
                    ),
                    steps=str(item.get("steps") or ""),
                    expected_results=str(
                        item.get("expectedResults") or item.get("expected_results") or ""
                    ),
                    priority=str(item.get("priority") or ""),
                    case_type=str(item.get("caseType") or item.get("case_type") or ""),
                    order_no=int(item.get("orderNo", item.get("order_no", index))),
                )
            )
            created += 1
        await self.repository.commit()
        return {"imported": created}

    async def import_to_zentao(self, user_id: str, suite_id: str, payload: Any) -> dict:
        if isinstance(payload, ImportFunctionCasesToZentaoRequest):
            request = payload
        else:
            try:
                request = ImportFunctionCasesToZentaoRequest.model_validate(
                    parse_import_payload(payload)
                )
            except ValidationError as exc:
                raise ErrBadRequest from exc

        suite, requirement, sprint, project = await self.get_owned_suite_context(user_id, suite_id)
        cases = await self.resolve_cases_for_zentao_import(suite.suite_id, request.case_ids)
        if not cases:
            raise dynamic_error(ErrFunctionTestCaseImportInvalid, "测试集下没有可导入用例")

        project_binding = await self.get_required_binding(
            "project",
            project.project_id,
            "请先绑定所属项目",
        )
        sprint_binding = await self.get_required_binding(
            "sprint",
            sprint.sprint_id,
            "请先绑定所属迭代",
        )
        requirement_binding = await self.get_required_binding(
            "requirement",
            requirement.requirement_id,
            "请先绑定所属需求",
        )
        self.validate_zentao_binding(project_binding, "project")
        self.validate_zentao_binding(sprint_binding, "execution")
        self.validate_zentao_binding(requirement_binding, "story")
        if (
            project_binding.connection_id != sprint_binding.connection_id
            or project_binding.connection_id != requirement_binding.connection_id
        ):
            raise dynamic_error(
                ErrResourceBindingInvalid,
                "项目、迭代和需求必须绑定到同一个禅道连接",
            )
        if (
            requirement_binding.remote_parent_id
            and requirement_binding.remote_parent_id != sprint_binding.remote_resource_id
        ):
            raise dynamic_error(
                ErrResourceBindingInvalid,
                "需求绑定的禅道需求不属于所属迭代绑定的禅道执行",
            )

        try:
            remote_project_id = parse_zentao_remote_id(project_binding.remote_resource_id)
            remote_execution_id = parse_zentao_remote_id(sprint_binding.remote_resource_id)
            remote_story_id = parse_zentao_remote_id(requirement_binding.remote_resource_id)
        except ValueError as exc:
            raise dynamic_error(ErrResourceBindingInvalid, str(exc)) from exc

        create_body = {
            "productID": request.product_id,
            "project": remote_project_id,
            "execution": remote_execution_id,
            "cases": [],
        }
        for case in cases:
            steps = split_zentao_lines(case.steps)
            expects = split_zentao_lines(case.expected_results)
            if not steps:
                raise dynamic_error(
                    ErrFunctionTestCaseImportInvalid,
                    f"用例[{case.case_id}]测试步骤不能为空",
                )
            if not expects:
                raise dynamic_error(
                    ErrFunctionTestCaseImportInvalid,
                    f"用例[{case.case_id}]预期结果不能为空",
                )
            steps, expects = normalize_zentao_steps_and_expects(steps, expects)
            create_body["cases"].append(
                {
                    "title": case.title.strip(),
                    "module": request.module_id,
                    "story": remote_story_id,
                    "pri": zentao_priority(case.priority),
                    "precondition": case.preconditions.strip(),
                    "steps": steps,
                    "expects": expects,
                }
            )

        if self.integration_connection_service is None or self.zentao_resource_client is None:
            raise ErrZentaoRemoteResourceUnavailable
        connection = await self.integration_connection_service.resolve_zentao_access(
            user_id,
            project_binding.connection_id,
            project.project_id,
        )
        try:
            result = await self.zentao_resource_client.create_test_cases(connection, create_body)
        except Exception as exc:
            raise dynamic_error(
                ErrZentaoRemoteResourceUnavailable,
                truncate_error(str(exc)),
            ) from exc
        remote_items = result.get("items") or []
        if len(remote_items) < len(cases):
            raise dynamic_error(ErrZentaoRemoteResourceUnavailable, "禅道测试用例创建结果数量不足")

        items = []
        for index, case in enumerate(cases):
            remote = remote_items[index]
            items.append(
                {
                    "caseId": case.case_id,
                    "remoteCaseId": int(item_value(remote, "id", default=0)),
                    "status": str(item_value(remote, "status", default="success") or "success"),
                }
            )
        return {
            "suiteId": suite.suite_id,
            "productId": request.product_id,
            "remoteProjectId": remote_project_id,
            "remoteExecutionId": remote_execution_id,
            "importedCaseCount": len(items),
            "items": items,
        }

    async def get_owned_suite_context(
        self,
        user_id: str,
        suite_id: str,
    ) -> tuple[Any, Any, Any, Any]:
        suite = await self.repository.get_suite(suite_id)
        if suite is None:
            raise ErrNotFound
        requirement = await self.repository.get_requirement(suite.requirement_id)
        if requirement is None:
            raise ErrNotFound
        sprint = await self.repository.get_sprint(requirement.sprint_id)
        if sprint is None:
            raise ErrNotFound
        project = await self.repository.get_project(sprint.project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden
        return suite, requirement, sprint, project

    async def resolve_cases_for_zentao_import(
        self,
        suite_id: str,
        case_ids: list[str],
    ) -> list[FunctionTestCase]:
        if not case_ids:
            return await self.repository.list_by_suite(suite_id)
        result = []
        seen = set()
        for index, case_id in enumerate(case_ids):
            normalized = str(case_id or "").strip()
            if not normalized:
                raise dynamic_error(ErrFunctionTestCaseImportInvalid, f"caseIds[{index}] 不能为空")
            if normalized in seen:
                raise dynamic_error(
                    ErrFunctionTestCaseImportInvalid,
                    f"caseIds[{index}] 重复: {normalized}",
                )
            seen.add(normalized)
            case = await self.repository.get_case(normalized)
            if case is None:
                raise ErrNotFound
            if case.suite_id != suite_id:
                raise dynamic_error(
                    ErrFunctionTestCaseImportInvalid,
                    f"用例不属于当前测试集: {normalized}",
                )
            result.append(case)
        return result

    async def get_required_binding(
        self,
        resource_type: str,
        resource_id: str,
        message: str,
    ) -> ResourceBinding:
        binding = await self.repository.get_active_binding(resource_type, resource_id)
        if binding is None:
            raise dynamic_error(ErrResourceBindingNotFound, message)
        return binding

    @staticmethod
    def validate_zentao_binding(binding: ResourceBinding, remote_resource_type: str) -> None:
        aliases = {
            "execution": {"execution", "sprint"},
            "story": {"story", "requirement"},
        }
        allowed_types = aliases.get(remote_resource_type, {remote_resource_type})
        if binding.provider != "zentao" or binding.remote_resource_type not in allowed_types:
            raise dynamic_error(ErrResourceBindingInvalid, "资源绑定不是有效的禅道绑定")

    async def list(self, user_id: str, suite_id: str) -> dict[str, Any]:
        await self.get_owned_suite(user_id, suite_id)
        rows = await self.repository.list_by_suite(suite_id)
        return list_payload([dump(FunctionCaseResponse, row) for row in rows])

    async def get(self, user_id: str, case_id: str) -> dict:
        return dump(FunctionCaseResponse, await self.get_owned_entity(user_id, case_id))

    async def update(self, user_id: str, case_id: str, body: dict[str, Any]) -> dict:
        case = await self.get_owned_entity(user_id, case_id)
        apply_patch(
            case,
            body,
            {
                "module",
                "title",
                "preconditions",
                "steps",
                "expected_results",
                "priority",
                "case_type",
                "order_no",
            },
        )
        await self.repository.commit()
        await self.repository.refresh(case)
        return dump(FunctionCaseResponse, case)

    async def delete(self, user_id: str, case_id: str) -> dict:
        case = await self.get_owned_entity(user_id, case_id)
        self.repository.soft_delete(case, datetime.now(UTC))
        await self.repository.commit()
        return {}


def split_zentao_lines(value: str) -> list[str]:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    return [part.strip() for part in text.split("\n") if part.strip()]


def normalize_zentao_steps_and_expects(
    steps: list[str],
    expects: list[str],
) -> tuple[list[str], list[str]]:
    if len(steps) == len(expects):
        return steps, expects
    target = max(len(steps), len(expects))
    return (
        steps + [" "] * (target - len(steps)),
        expects + [" "] * (target - len(expects)),
    )


def zentao_priority(value: str) -> int:
    text = str(value or "").strip().upper().removeprefix("P")
    try:
        priority = int(text)
    except ValueError:
        return 3
    return priority if 1 <= priority <= 4 else 3


def item_value(item: Any, key: str, *, default: Any = "") -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)
