from collections.abc import Mapping

from argon2 import PasswordHasher
from sqlalchemy import text
from sqlalchemy.orm import Session

_password_hasher = PasswordHasher()


def _id(session: Session, query: str, params: Mapping[str, object]) -> int:
    value = session.execute(text(query), params).scalar_one()
    return int(value)


def load_seed_fixture(
    session: Session, fixture: Mapping[str, object], *, actor_id: int | None = None
) -> dict[str, int | str]:
    with session.begin():
        password_hash = _password_hasher.hash(str(fixture["password"]))

        semester_data = fixture["semester"]
        session.execute(
            text(
                """
                INSERT INTO semesters
                    (code, name, note, start_date, end_date, academic_year, updated_at)
                VALUES
                    (:code, :name, :note, :start_date, :end_date,
                     CONCAT(EXTRACT(YEAR FROM CAST(:start_date AS DATE))::int, '-',
                            (EXTRACT(YEAR FROM CAST(:start_date AS DATE))::int + 1)),
                     now())
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    note = EXCLUDED.note,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    academic_year = EXCLUDED.academic_year,
                    updated_at = now()
                """
            ),
            {**semester_data, "note": semester_data.get("note")},
        )
        major_data = fixture["major"]
        session.execute(
            text(
                """
                INSERT INTO majors (code, name) VALUES (:code, :name)
                ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
                """
            ),
            major_data,
        )

        account_count = 0
        for account in fixture["accounts"]:
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
                {
                    "email": account["email"],
                    "display_name": account["display_name"],
                    "password_hash": password_hash,
                },
            )
            session.execute(
                text(
                    "INSERT INTO account_roles (account_id, role) VALUES (:account_id, :role) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"account_id": account_id, "role": account["role"]},
            )
            if account["role"] == "LECTURER":
                session.execute(
                    text(
                        """
                        INSERT INTO lecturers (account_id, lecturer_code)
                        VALUES (:account_id, :lecturer_code)
                        ON CONFLICT (lecturer_code) DO UPDATE SET account_id = EXCLUDED.account_id
                        """
                    ),
                    {"account_id": account_id, "lecturer_code": account["lecturer_code"]},
                )
            elif account["role"] == "STUDENT":
                session.execute(
                    text(
                        """
                        INSERT INTO students (account_id, student_code)
                        VALUES (:account_id, :student_code)
                        ON CONFLICT (student_code) DO UPDATE SET account_id = EXCLUDED.account_id
                        """
                    ),
                    {"account_id": account_id, "student_code": account["student_code"]},
                )
            account_count += 1

        for room in fixture["rooms"]:
            session.execute(
                text(
                    """
                    INSERT INTO rooms (code, name, capacity, room_type)
                    VALUES (:code, :name, :capacity, :room_type)
                    ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        capacity = EXCLUDED.capacity,
                        room_type = EXCLUDED.room_type
                    """
                ),
                room,
            )

        session.execute(
            text(
                """
                INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json)
                VALUES (:actor_id, 'SEED_FIXTURE_LOADED', 'seed_fixture', :entity_id, CAST(:after_json AS JSONB))
                """
            ),
            {
                "actor_id": actor_id,
                "entity_id": str(fixture["version"]),
                "after_json": '{"source": "VERSIONED_SEED"}',
            },
        )

    return {
        "version": str(fixture["version"]),
        "accounts": account_count,
        "rooms": len(fixture["rooms"]),
    }
