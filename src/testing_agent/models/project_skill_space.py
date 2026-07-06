from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class ProjectSkillSpace(Base, SoftDeleteMixin):
    __tablename__ = "project_skill_spaces"
    __table_args__ = (UniqueConstraint("project_id", "filename", name="uk_project_skill_filename"),)
    id: Mapped[IdPk]
    skill_space_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    download_url: Mapped[str] = mapped_column(String(512), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
