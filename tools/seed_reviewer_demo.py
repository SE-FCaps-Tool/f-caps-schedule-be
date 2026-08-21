import json

from app.config import get_settings
from app.database import get_engine
from app.domain.reviewer_demo_seed import reviewer_demo_fixture
from app.services.seed_loader import load_seed_fixture
from sqlalchemy.orm import Session


def main() -> None:
    with Session(get_engine(get_settings().database_url)) as session:
        counts = load_seed_fixture(session, reviewer_demo_fixture())
    print(json.dumps(counts, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
