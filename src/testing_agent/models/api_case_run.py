from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class ApiCaseRun(Base):
    __tablename__ = "api_case_runs"
    id: Mapped[IdPk]
    run_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    collection_run_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    collection_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    sprint_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    environment_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    trigger_user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="pending")
    request_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    response_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    runtime_vars_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    extract_results_json: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    assert_results_json: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
