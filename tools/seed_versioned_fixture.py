"""Load the versioned demo fixture during Docker database bootstrap.

This is intentionally a CLI bootstrap step, not an HTTP endpoint.  The Excel
import runs first; this fixture then adds the deterministic demo records.  The
lecturer emails are namespaced to avoid colliding with Excel lecturers because
the lecturers.account_id column is unique.
"""

from __future__ import annotations

import copy
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.domain.seed import seed_fixture_v1
from app.services.seed_loader import load_seed_fixture


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    fixture = copy.deepcopy(seed_fixture_v1())
    for lecturer in fixture["lecturers"]:
        lecturer["email"] = f"fixture-{lecturer['email']}"

    engine = create_engine(database_url)
    with Session(engine) as session:
        counts = load_seed_fixture(session, fixture)
    print(json.dumps({"source": "seed-v1", "status": "loaded", "counts": counts}))


if __name__ == "__main__":
    main()
