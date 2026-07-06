from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class WorkerTask(Base):
    __tablename__ = "worker_tasks"
    __table_args__ = (
        UniqueConstraint("domain", "task_id", name="uk_worker_domain_task"),
        Index("idx_worker_domain_status_created", "domain", "status", "created_at"),
    )
    id: Mapped[IdPk]
    domain: Mapped[str] = mapped_column(String(10), nullable=False)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    run_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    suite_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="")
    case_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="")
    collection_run_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, default=""
    )
    collection_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="")
    generate_task_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, default=""
    )
    llm_connection_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="pending")
    worker_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False, default="")
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
