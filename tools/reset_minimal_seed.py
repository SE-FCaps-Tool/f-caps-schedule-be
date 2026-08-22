import json

from app.config import get_settings
from app.database import get_engine
from app.domain.seed import seed_fixture_v1
from app.services.seed_loader import load_seed_fixture
from sqlalchemy import text
from sqlalchemy.orm import Session


def clear_application_data(session: Session) -> None:
    table_names = session.execute(
        text(
            "SELECT tablename FROM pg_tables "
            "WHERE schemaname = 'public' AND tablename <> 'alembic_version'"
        )
    ).scalars().all()
    if table_names:
        quoted_tables = ", ".join('"' + name.replace('"', '""') + '"' for name in table_names)
        session.connection().exec_driver_sql(
            f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"
        )


def main() -> None:
    engine = get_engine(get_settings().database_url)
    with Session(engine) as session, session.begin():
        clear_application_data(session)
    with Session(engine) as session:
        counts = load_seed_fixture(session, seed_fixture_v1())
    print(json.dumps(counts, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
