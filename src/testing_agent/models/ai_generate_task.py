from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class AiGenerateTask(Base, SoftDeleteMixin):
    __tablename__ = "ai_generate_tasks"
    id: Mapped[IdPk]
    task_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    task_type: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False, default="api_case_generate"
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    sprint_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    creator_user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

class ApiCaseGenerateTaskRun(Base):
    __tablename__ = "api_case_generate_task_runs"
    id: Mapped[IdPk]
    run_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    sprint_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    trigger_user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="pending")
    checkpoint_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    current_stage: Mapped[str] = mapped_column(String(40), index=True, nullable=False, default="")
    stage_status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="")
    snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    config_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_yaml: Mapped[str] = mapped_column(LONGTEXT, nullable=False, default="")
    result_summary_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, default="pending"
    )
    imported_collection_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, default=""
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, default=""
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
