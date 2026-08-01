from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "20260801_0006_expand_generic_import_state.py"
)


def _load_migration():
    spec = importlib.util.spec_from_file_location("expand_generic_import_state", MIGRATION_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _upgrade_historical_rows() -> list[dict]:
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    tasks = sa.Table(
        "ai_generate_tasks",
        metadata,
        sa.Column("task_id", sa.String(64), primary_key=True),
        sa.Column("task_type", sa.String(50), nullable=False),
    )
    runs = sa.Table(
        "api_case_generate_task_runs",
        metadata,
        sa.Column("run_id", sa.String(64), primary_key=True),
        sa.Column("task_id", sa.String(64), nullable=False),
        sa.Column("imported_collection_id", sa.String(255), nullable=False, default=""),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    metadata.create_all(engine)
    imported_at = datetime(2026, 7, 31, 10, 0)
    with engine.begin() as connection:
        connection.execute(
            tasks.insert(),
            [
                {"task_id": "api-task", "task_type": "api_case_generate"},
                {"task_id": "function-task", "task_type": "functional_case_generate"},
            ],
        )
        connection.execute(
            runs.insert(),
            [
                {
                    "run_id": "pending",
                    "task_id": "api-task",
                    "imported_collection_id": "",
                    "reviewed_at": None,
                    "updated_at": imported_at,
                },
                {
                    "run_id": "api",
                    "task_id": "api-task",
                    "imported_collection_id": "collection-1",
                    "reviewed_at": imported_at,
                    "updated_at": imported_at,
                },
                {
                    "run_id": "function-single",
                    "task_id": "function-task",
                    "imported_collection_id": "suite-1",
                    "reviewed_at": imported_at,
                    "updated_at": imported_at,
                },
                {
                    "run_id": "function-multiple",
                    "task_id": "function-task",
                    "imported_collection_id": "suite-1,suite-2,suite-3",
                    "reviewed_at": imported_at,
                    "updated_at": imported_at,
                },
                {
                    "run_id": "function-lossy",
                    "task_id": "function-task",
                    "imported_collection_id": "suite-1,+2",
                    "reviewed_at": imported_at,
                    "updated_at": imported_at,
                },
            ],
        )

        migration = _load_migration()
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        reflected = sa.Table("api_case_generate_task_runs", sa.MetaData(), autoload_with=connection)
        rows = connection.execute(sa.select(reflected).order_by(reflected.c.run_id)).mappings()
        return [dict(row) for row in rows]


def test_upgrade_marks_unimported_history_as_pending():
    row = next(row for row in _upgrade_historical_rows() if row["run_id"] == "pending")

    assert row["import_status"] == "pending"
    assert row["imported_targets"] == []
    assert row["imported_at"] is None
    assert row["import_migration_complete"] is True


def test_upgrade_converts_historical_api_collection_exactly():
    row = next(row for row in _upgrade_historical_rows() if row["run_id"] == "api")

    assert row["import_status"] == "imported"
    assert row["imported_targets"] == [
        {"targetType": "api_collection", "targetId": "collection-1"}
    ]
    assert row["imported_at"] == datetime(2026, 7, 31, 10, 0)
    assert row["import_migration_complete"] is True


def test_upgrade_recovers_historical_single_function_suite():
    row = next(
        row for row in _upgrade_historical_rows() if row["run_id"] == "function-single"
    )

    assert row["imported_targets"] == [
        {"targetType": "function_suite", "targetId": "suite-1"}
    ]
    assert row["import_migration_complete"] is True


def test_upgrade_recovers_every_historical_function_suite():
    row = next(
        row for row in _upgrade_historical_rows() if row["run_id"] == "function-multiple"
    )

    assert row["imported_targets"] == [
        {"targetType": "function_suite", "targetId": "suite-1"},
        {"targetType": "function_suite", "targetId": "suite-2"},
        {"targetType": "function_suite", "targetId": "suite-3"},
    ]
    assert row["import_migration_complete"] is True


def test_upgrade_preserves_recognizable_lossy_summary_and_marks_it_incomplete():
    row = next(
        row for row in _upgrade_historical_rows() if row["run_id"] == "function-lossy"
    )

    assert row["import_status"] == "imported"
    assert row["imported_targets"] == [
        {"targetType": "function_suite", "targetId": "suite-1"}
    ]
    assert row["imported_at"] == datetime(2026, 7, 31, 10, 0)
    assert row["import_migration_complete"] is False
