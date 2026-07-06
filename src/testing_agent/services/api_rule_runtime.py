from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

try:
    from jsonpath_ng import parse as parse_jsonpath
except Exception:  # pragma: no cover - dependency may be absent before install
    parse_jsonpath = None


@dataclass(slots=True)
class ExecuteResponse:
    status_code: int
    headers: dict[str, list[str]]
    body: str
    duration_ms: int = 0


class RunResponseResolver:
    def __init__(self, response: ExecuteResponse) -> None:
        self.response = response
        self._body_json_loaded = False
        self._body_json: Any = None

    def resolve_extract_value(self, source: str, expr: str) -> str:
        value, exists = self.resolve_value(source, expr)
        if not exists:
            raise ValueError("未提取到值")
        return comparable_value_string(value)

    def resolve_assert_value(self, source: str, expr: str) -> tuple[str, bool]:
        value, exists = self.resolve_value(source, expr)
        return comparable_value_string(value), exists

    def resolve_value(self, source: str, expr: str) -> tuple[Any, bool]:
        if source == "status_code":
            return self.response.status_code, True
        if source == "header":
            return self._find_header(expr)
        if source == "body_jsonpath":
            if not expr.strip():
                raise ValueError("JSONPath 表达式不能为空")
            if parse_jsonpath is None:
                raise ValueError("jsonpath-ng 依赖未安装")
            body = self._load_json_body()
            matches = [match.value for match in parse_jsonpath(expr).find(body)]
            if not matches:
                return "", False
            return matches[0], True
        if source == "body_text":
            if not expr.strip():
                return self.response.body, True
            match = re.search(expr, self.response.body)
            if match is None:
                return "", False
            if match.groups():
                return match.group(1), True
            return match.group(0), True
        raise ValueError(f"不支持的规则来源: {source}")

    def _find_header(self, key: str) -> tuple[str, bool]:
        for header_key, values in self.response.headers.items():
            if header_key.lower() == key.lower():
                return ",".join(values), True
        return "", False

    def _load_json_body(self) -> Any:
        if not self._body_json_loaded:
            self._body_json_loaded = True
            if not self.response.body.strip():
                raise ValueError("响应体为空，无法解析 JSON")
            self._body_json = json.loads(self.response.body)
        return self._body_json


def comparable_value_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def compare_assertion(
    comparator: str, expected_value: str, actual_value: str, exists: bool
) -> bool:
    if comparator == "exists":
        return exists
    if not exists:
        raise ValueError("断言目标不存在")
    if comparator == "eq":
        return actual_value == expected_value
    if comparator == "neq":
        return actual_value != expected_value
    if comparator == "contains":
        return expected_value in actual_value
    if comparator == "not_contains":
        return expected_value not in actual_value
    if comparator == "regex":
        return re.search(expected_value, actual_value) is not None
    if comparator in {"gt", "gte", "lt", "lte"}:
        actual_number = float(actual_value)
        expected_number = float(expected_value)
        if comparator == "gt":
            return actual_number > expected_number
        if comparator == "gte":
            return actual_number >= expected_number
        if comparator == "lt":
            return actual_number < expected_number
        return actual_number <= expected_number
    raise ValueError(f"不支持的比较器: {comparator}")
