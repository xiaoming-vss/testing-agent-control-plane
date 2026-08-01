"""expand generic import state

Revision ID: 20260801_0006
Revises: 20260730_0005
Create Date: 2026-08-01 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260801_0006"
down_revision = "20260730_0005"
branch_labels = None
depends_on = None

RUNS_TABLE = "api_case_generate_task_runs"


def _function_targets(summary: str) -> tuple[list[dict[str, str]], bool]:
    targets: list[dict[str, str]] = []
    migration_complete = True
    for part in summary.split(","):
        target_id = part.strip()
        if target_id.startswith("+") and target_id[1:].isdigit():
            migration_complete = False
        elif target_id:
            targets.append({"targetType": "function_suite", "targetId": target_id})
    return targets, migration_complete


def upgrade() -> None:
    op.add_column(
        RUNS_TABLE,
        sa.Column("import_status", sa.String(length=20), nullable=False, server_default="pending"),
    )
    op.create_index(
        op.f("ix_api_case_generate_task_runs_import_status"),
        RUNS_TABLE,
        ["import_status"],
        unique=False,
    )
    op.add_column(RUNS_TABLE, sa.Column("imported_targets", sa.JSON(), nullable=True))
    op.add_column(RUNS_TABLE, sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        RUNS_TABLE,
        sa.Column(
            "import_migration_complete",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    tasks = sa.table(
        "ai_generate_tasks",
        sa.column("task_id", sa.String(length=64)),
        sa.column("task_type", sa.String(length=50)),
    )
    runs = sa.table(
        RUNS_TABLE,
        sa.column("run_id", sa.String(length=64)),
        sa.column("task_id", sa.String(length=64)),
        sa.column("imported_collection_id", sa.String(length=255)),
        sa.column("reviewed_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("import_status", sa.String(length=20)),
        sa.column("imported_targets", sa.JSON()),
        sa.column("imported_at", sa.DateTime(timezone=True)),
        sa.column("import_migration_complete", sa.Boolean()),
    )
    bind = op.get_bind()
    historical_rows = bind.execute(
        sa.select(
            runs.c.run_id,
            runs.c.imported_collection_id,
            runs.c.reviewed_at,
            runs.c.updated_at,
            tasks.c.task_type,
        ).select_from(runs.join(tasks, tasks.c.task_id == runs.c.task_id))
    ).mappings()

    for row in historical_rows:
        legacy_target = str(row["imported_collection_id"] or "").strip()
        values: dict[str, object] = {
            "import_status": "pending",
            "imported_targets": [],
            "imported_at": None,
            "import_migration_complete": True,
        }
        if legacy_target:
            task_type = str(row["task_type"] or "")
            if task_type == "api_case_generate":
                targets = [{"targetType": "api_collection", "targetId": legacy_target}]
                migration_complete = True
            elif task_type == "functional_case_generate":
                targets, migration_complete = _function_targets(legacy_target)
            else:
                targets = []
                migration_complete = False
            values.update(
                import_status="imported",
                imported_targets=targets,
                imported_at=row["reviewed_at"] or row["updated_at"],
                import_migration_complete=migration_complete,
            )
        bind.execute(runs.update().where(runs.c.run_id == row["run_id"]).values(**values))


def downgrade() -> None:
    op.drop_column(RUNS_TABLE, "import_migration_complete")
    op.drop_column(RUNS_TABLE, "imported_at")
    op.drop_column(RUNS_TABLE, "imported_targets")
    op.drop_index(op.f("ix_api_case_generate_task_runs_import_status"), table_name=RUNS_TABLE)
    op.drop_column(RUNS_TABLE, "import_status")
