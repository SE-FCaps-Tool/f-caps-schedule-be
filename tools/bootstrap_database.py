"""Run migrations and idempotent seed sources before an app process starts.

The Compose stack intentionally has no dedicated db-init container.  API and
worker processes call this script themselves; a PostgreSQL advisory lock makes
the bootstrap safe when both processes start at the same time.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import time

import psycopg


LOCK_KEY = 617283945
ROOT = Path("/app")
API_ROOT = ROOT / "apps" / "api"
WORKBOOK = ROOT / "SE_CapstoneProject_SP26_ReviewDefense_New.xlsx"


def _dsn(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _connect(database_url: str) -> psycopg.Connection:
    while True:
        try:
            connection = psycopg.connect(_dsn(database_url), autocommit=True)
            connection.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))
            return connection
        except psycopg.OperationalError:
            time.sleep(1)


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    connection = _connect(database_url)
    try:
        commands = [
            ["alembic", "upgrade", "head"],
            [
                "python",
                "/app/tools/import_excel_database.py",
                str(WORKBOOK),
                "--skip-if-imported",
            ],
            ["python", "/app/tools/seed_versioned_fixture.py"],
        ]
        for command in commands:
            subprocess.run(command, cwd=API_ROOT, check=True)
    finally:
        connection.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))
        connection.close()


if __name__ == "__main__":
    main()
