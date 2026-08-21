import json

from app.config import get_settings
from app.database import get_engine
from app.domain.reviewer_demo_seed import reviewer_demo_fixture
from argon2 import PasswordHasher
from sqlalchemy import text
from sqlalchemy.orm import Session

password_hasher = PasswordHasher()


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


def seed_accounts(session: Session) -> dict[str, int | str]:
    fixture = reviewer_demo_fixture()
    password_hash = password_hasher.hash(str(fixture["password"]))
    account_count = 0
    lecturer_count = 0
    student_count = 0

    for account in fixture["accounts"]:
        account_id = session.execute(
            text(
                "INSERT INTO accounts (email, display_name, password_hash) "
                "VALUES (:email, :display_name, :password_hash) RETURNING id"
            ),
            {
                "email": account["email"],
                "display_name": account["display_name"],
                "password_hash": password_hash,
            },
        ).scalar_one()
        session.execute(
            text("INSERT INTO account_roles (account_id, role) VALUES (:account_id, :role)"),
            {"account_id": account_id, "role": account["role"]},
        )
        account_count += 1
        if account["role"] == "LECTURER":
            session.execute(
                text("INSERT INTO lecturers (account_id, lecturer_code) VALUES (:account_id, :code)"),
                {"account_id": account_id, "code": account["lecturer_code"]},
            )
            lecturer_count += 1
        elif account["role"] == "STUDENT":
            session.execute(
                text("INSERT INTO students (account_id, student_code) VALUES (:account_id, :code)"),
                {"account_id": account_id, "code": account["student_code"]},
            )
            student_count += 1

    return {
        "version": "accounts-only-reviewer-demo-v1",
        "accounts": account_count,
        "lecturers": lecturer_count,
        "students": student_count,
    }


def main() -> None:
    with Session(get_engine(get_settings().database_url)) as session, session.begin():
        clear_application_data(session)
        counts = seed_accounts(session)
    print(json.dumps(counts, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
