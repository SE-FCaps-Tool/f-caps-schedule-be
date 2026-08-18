"""Seed one demo account per role: ADMIN, MANAGER, LECTURER, STUDENT.

Run inside the api container:
    docker compose exec api python scripts/seed_accounts.py
"""

from argon2 import PasswordHasher
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine

PASSWORD = "12345@Abc"

ACCOUNTS = [
    ("admin@gmail.com", "Admin", "ADMIN", None),
    ("manager@gmail.com", "Manager", "MANAGER", None),
    ("lecturer@gmail.com", "Lecturer", "LECTURER", "GV_DEMO"),
    ("student@gmail.com", "Student", "STUDENT", "SV_DEMO"),
]


def _id(session: Session, query: str, params: dict[str, object]) -> int:
    return int(session.execute(text(query), params).scalar_one())


def main() -> None:
    password_hash = PasswordHasher().hash(PASSWORD)
    engine = get_engine(get_settings().database_url)
    with Session(engine) as session, session.begin():
        for email, display_name, role, code in ACCOUNTS:
            account_id = _id(
                session,
                """
                INSERT INTO accounts (email, display_name, password_hash)
                VALUES (:email, :display_name, :password_hash)
                ON CONFLICT (email) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    password_hash = EXCLUDED.password_hash,
                    status = 'ACTIVE'
                RETURNING id
                """,
                {"email": email, "display_name": display_name, "password_hash": password_hash},
            )
            session.execute(
                text(
                    "INSERT INTO account_roles (account_id, role) VALUES (:account_id, :role) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"account_id": account_id, "role": role},
            )
            if role == "LECTURER":
                session.execute(
                    text(
                        """
                        INSERT INTO lecturers (account_id, lecturer_code) VALUES (:account_id, :code)
                        ON CONFLICT (lecturer_code) DO UPDATE SET account_id = EXCLUDED.account_id
                        """
                    ),
                    {"account_id": account_id, "code": code},
                )
            elif role == "STUDENT":
                session.execute(
                    text(
                        """
                        INSERT INTO students (account_id, student_code) VALUES (:account_id, :code)
                        ON CONFLICT (student_code) DO UPDATE SET account_id = EXCLUDED.account_id
                        """
                    ),
                    {"account_id": account_id, "code": code},
                )
            print(f"seeded {role} -> {email}")


if __name__ == "__main__":
    main()
