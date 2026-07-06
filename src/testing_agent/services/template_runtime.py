from __future__ import annotations

import secrets
import shlex
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from string import ascii_letters, digits
from typing import Any

_TEMPLATE_START = "{{"
_TEMPLATE_END = "}}"
_RANDOM_ALPHABET = ascii_letters + digits


@dataclass(slots=True)
class TemplateRenderContext:
    now: datetime
    dynamic_values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def fixed_now(cls, value: str) -> TemplateRenderContext:
        return cls(datetime.fromisoformat(value))

    @classmethod
    def current(cls) -> TemplateRenderContext:
        return cls(datetime.now().astimezone())

    def resolve_dynamic_expression(self, expr: str) -> Any:
        normalized = expr.strip()
        if normalized in self.dynamic_values:
            return self.dynamic_values[normalized]
        tokens = shlex.split(normalized)
        if not tokens:
            raise ValueError("动态函数不能为空")
        func_name = tokens[0].removeprefix("$")
        args = tokens[1:]

        if func_name == "timestamp":
            _ensure_arg_count(func_name, args, 0)
            value: Any = int(self.now.timestamp())
        elif func_name == "timestamp_ms":
            _ensure_arg_count(func_name, args, 0)
            value = int(self.now.timestamp() * 1000)
        elif func_name == "now":
            _ensure_arg_count(func_name, args, 0)
            value = self.now.isoformat()
        elif func_name == "date":
            _ensure_arg_count(func_name, args, 1)
            value = self.now.strftime(args[0])
        elif func_name == "uuid":
            _ensure_arg_count(func_name, args, 0)
            value = str(uuid.uuid4())
        elif func_name == "randomInt":
            _ensure_arg_count(func_name, args, 2)
            min_value = int(args[0])
            max_value = int(args[1])
            if min_value > max_value:
                raise ValueError("动态函数 $randomInt 最小值不能大于最大值")
            value = min_value + secrets.randbelow(max_value - min_value + 1)
        elif func_name == "randomString":
            _ensure_arg_count(func_name, args, 1)
            length = int(args[0])
            if length <= 0:
                raise ValueError("动态函数 $randomString 长度必须大于 0")
            value = "".join(secrets.choice(_RANDOM_ALPHABET) for _ in range(length))
        else:
            raise ValueError(f"不支持的动态函数: {tokens[0]}")

        self.dynamic_values[normalized] = value
        return value


def render_template_string(
    input_value: str, variables: dict[str, str], ctx: TemplateRenderContext
) -> str:
    output: list[str] = []
    cursor = 0
    while cursor < len(input_value):
        start = input_value.find(_TEMPLATE_START, cursor)
        if start < 0:
            output.append(input_value[cursor:])
            break
        end = input_value.find(_TEMPLATE_END, start + len(_TEMPLATE_START))
        if end < 0:
            output.append(input_value[cursor:])
            break
        output.append(input_value[cursor:start])
        raw_expr = input_value[start + len(_TEMPLATE_START) : end]
        expr = raw_expr.strip()
        resolved, value = resolve_template_expression(expr, variables, ctx)
        if resolved:
            output.append(stringify_value(value))
        else:
            output.append(input_value[start : end + len(_TEMPLATE_END)])
        cursor = end + len(_TEMPLATE_END)
    return "".join(output)


def render_template_value(
    input_value: str, variables: dict[str, str], ctx: TemplateRenderContext
) -> Any:
    stripped = input_value.strip()
    if stripped.startswith(_TEMPLATE_START) and stripped.endswith(_TEMPLATE_END):
        inner = stripped[len(_TEMPLATE_START) : -len(_TEMPLATE_END)].strip()
        resolved, value = resolve_template_expression(inner, variables, ctx)
        if resolved:
            return value
    return render_template_string(input_value, variables, ctx)


def resolve_template_expression(
    expr: str, variables: dict[str, str], ctx: TemplateRenderContext
) -> tuple[bool, Any]:
    if not expr:
        return False, None
    if expr.startswith("$"):
        return True, ctx.resolve_dynamic_expression(expr)
    if expr in variables:
        return True, variables[expr]
    return False, None


def stringify_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _ensure_arg_count(func_name: str, args: list[str], expected: int) -> None:
    if len(args) != expected:
        raise ValueError(f"动态函数 ${func_name} 参数数量错误")
