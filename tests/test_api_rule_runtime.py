from testing_agent.services.api_rule_runtime import (
    ExecuteResponse,
    RunResponseResolver,
    comparable_value_string,
    compare_assertion,
)


def test_compare_assertion_supports_go_comparators():
    assert compare_assertion("eq", "200", "200", True)
    assert compare_assertion("neq", "201", "200", True)
    assert compare_assertion("contains", "ok", "all ok", True)
    assert compare_assertion("not_contains", "bad", "all ok", True)
    assert compare_assertion("gt", "1", "2", True)
    assert compare_assertion("gte", "2", "2", True)
    assert compare_assertion("lt", "3", "2", True)
    assert compare_assertion("lte", "2", "2", True)
    assert compare_assertion("exists", "", "", True)


def test_resolver_reads_status_header_and_text_regex():
    resolver = RunResponseResolver(ExecuteResponse(200, {"X-Token": ["abc"]}, "hello id=42"))

    assert resolver.resolve_assert_value("status_code", "") == ("200", True)
    assert resolver.resolve_assert_value("header", "x-token") == ("abc", True)
    assert resolver.resolve_extract_value("body_text", r"id=(\d+)") == "42"


def test_comparable_value_string_matches_go_style_booleans_and_json():
    assert comparable_value_string(True) == "true"
    assert comparable_value_string(False) == "false"
    assert comparable_value_string({"a": 1}) == '{"a":1}'
