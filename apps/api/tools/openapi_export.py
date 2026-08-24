"""Export the committed OpenAPI wire contract."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

os.environ["APP_ENV"] = "test"


def current_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_spec(path: Path, spec: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    from app.main import create_app

    commit = current_commit()
    spec = create_app().openapi()
    spec.setdefault("info", {})["x-be-commit"] = commit
    write_spec(API_ROOT / "openapi.json", spec)


if __name__ == "__main__":
    main()
