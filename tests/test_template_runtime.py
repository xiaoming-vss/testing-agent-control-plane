import re

import pytest

from testing_agent.services.template_runtime import TemplateRenderContext, render_template_string


def test_template_keeps_unknown_variables_unchanged():
    ctx = TemplateRenderContext.fixed_now("2026-06-25T12:30:00+00:00")

    assert (
        render_template_string("/users/{{ missing }}", {"id": "42"}, ctx) == "/users/{{ missing }}"
    )


def test_template_renders_variables_and_cached_dynamic_values():
    ctx = TemplateRenderContext.fixed_now("2026-06-25T12:30:00+00:00")

    rendered = render_template_string(
        "/{{ id }}/{{ $timestamp }}/{{ $timestamp }}/{{ $date '%Y-%m-%d' }}",
        {"id": "42"},
        ctx,
    )

    assert rendered == "/42/1782390600/1782390600/2026-06-25"


def test_template_renders_uuid_and_random_string():
    ctx = TemplateRenderContext.fixed_now("2026-06-25T12:30:00+00:00")

    rendered = render_template_string("{{ $uuid }}:{{ $randomString 8 }}", {}, ctx)

    uuid_part, random_part = rendered.split(":")
    assert re.fullmatch(r"[0-9a-f\-]{36}", uuid_part)
    assert re.fullmatch(r"[A-Za-z0-9]{8}", random_part)


def test_template_rejects_invalid_dynamic_arguments():
    ctx = TemplateRenderContext.fixed_now("2026-06-25T12:30:00+00:00")

    with pytest.raises(ValueError, match="randomInt"):
        render_template_string("{{ $randomInt 9 1 }}", {}, ctx)
