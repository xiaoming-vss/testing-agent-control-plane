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
    / "20260801_0008_drop_legacy_import_field.py"
)


def _load_migration():
    spec = importlib.util.spec_from_file_location("drop_legacy_import_field", MIGRATION_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_upgrade_drops_legacy_field_without_losing_generic_import_state():
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    runs = sa.Table(
        "api_case_generate_task_runs",
        metadata,
        sa.Column("run_id", sa.String(64), primary_key=True),
        sa.Column("imported_collection_id", sa.String(64), nullable=False, default=""),
        sa.Column("import_status", sa.String(20), nullable=False),
        sa.Column("imported_targets", sa.JSON(), nullable=True),
        sa.Column("imported_at", sa.DateTime(), nullable=True),
        sa.Column("import_migration_complete", sa.Boolean(), nullable=False),
        sa.Index(
            "ix_api_case_generate_task_runs_imported_collection_id",
            "imported_collection_id",
        ),
    )
    metadata.create_all(engine)
    imported_at = datetime(2026, 8, 1, 10, 0)

    with engine.begin() as connection:
        connection.execute(
            runs.insert().values(
                run_id="historical-api",
                imported_collection_id="collection-1",
                import_status="imported",
                imported_targets=[
                    {"targetType": "api_collection", "targetId": "collection-1"}
                ],
                imported_at=imported_at,
                import_migration_complete=True,
            )
        )
        migration = _load_migration()
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        reflected = sa.Table(
            "api_case_generate_task_runs", sa.MetaData(), autoload_with=connection
        )
        row = connection.execute(sa.select(reflected)).mappings().one()

    assert "imported_collection_id" not in reflected.c
    assert row["import_status"] == "imported"
    assert row["imported_targets"] == [
        {"targetType": "api_collection", "targetId": "collection-1"}
    ]
    assert row["imported_at"] == imported_at
    assert row["import_migration_complete"] is True
