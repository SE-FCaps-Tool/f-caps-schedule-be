"""Regenerate committed OpenAPI artifacts and fail when they drift."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
EXPORTER = API_ROOT / "tools" / "openapi_export.py"
ARTIFACTS = ("openapi.json",)


def without_commit_stamp(raw: str) -> dict[str, Any]:
    """The stamp names the commit being built, so it always differs from the file."""

    spec = json.loads(raw)
    spec.get("info", {}).pop("x-be-commit", None)
    return spec


def main() -> int:
    committed = {name: (REPO_ROOT / "apps" / "api" / name).read_text(encoding="utf-8") for name in ARTIFACTS}
    subprocess.run([sys.executable, str(EXPORTER)], cwd=REPO_ROOT, check=True)

    drifted = []
    for name, before in committed.items():
        path = API_ROOT / name
        after = path.read_text(encoding="utf-8")
        if without_commit_stamp(before) == without_commit_stamp(after):
            path.write_text(before, encoding="utf-8")
        else:
            drifted.append(name)

    for name in drifted:
        print(f"{name} is out of date; commit the regenerated file.", file=sys.stderr)
    return 1 if drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())
