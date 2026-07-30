from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class UiTestSuite(Base, SoftDeleteMixin):
    __tablename__ = "ui_test_suites"
    __table_args__ = (
        UniqueConstraint("requirement_id", "name", name="uk_ui_suite_requirement_name"),
    )
    id: Mapped[IdPk]
    suite_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    headless: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    slow_mo_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    viewport_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    viewport_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    default_step_timeout_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    screenshot_policy: Mapped[str] = mapped_column(
        String(32), nullable=False, default="on_failure"
    )
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
