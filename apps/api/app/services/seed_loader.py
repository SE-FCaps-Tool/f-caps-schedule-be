from collections.abc import Mapping

from sqlalchemy import text
from sqlalchemy.orm import Session

DEMO_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$V6pAiT9HmR/z0IItWjtNuA$skwmr/puZ9G53gYN9UBRlHgGHXIVk2nNuIh9OunS00Y"


def _id(session: Session, query: str, params: Mapping[str, object]) -> int:
    value = session.execute(text(query), params).scalar_one()
    return int(value)


def load_seed_fixture(
    session: Session, fixture: Mapping[str, object], *, actor_id: int | None = None
) -> dict[str, int | str]:
    with session.begin():
        semester_data = fixture["semester"]
        major_data = fixture["major"]
        semester_id = _id(
            session,
            """
            INSERT INTO semesters (code, name, start_date, end_date)
            VALUES (:code, :name, :start_date, :end_date)
            ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date
            RETURNING id
            """,
            semester_data,
        )
        major_id = _id(
            session,
            """
            INSERT INTO majors (code, name) VALUES (:code, :name)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            major_data,
        )

        for email, display_name, role in (
            ("admin1@gmail.com", "Scheduler Admin 1", "ADMIN"),
            ("admin2@gmail.com", "Scheduler Admin 2", "ADMIN"),
            ("manager1@gmail.com", "Scheduler Manager 1", "MANAGER"),
            ("manager2@gmail.com", "Scheduler Manager 2", "MANAGER"),
        ):
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
                {"email": email, "display_name": display_name, "password_hash": DEMO_PASSWORD_HASH},
            )
            session.execute(
                text(
                    "INSERT INTO account_roles (account_id, role) VALUES (:account_id, :role) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"account_id": account_id, "role": role},
            )

        lecturer_ids: dict[str, int] = {}
        for lecturer in fixture["lecturers"]:
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
                {**lecturer, "password_hash": DEMO_PASSWORD_HASH},
            )
            session.execute(
                text(
                    "INSERT INTO account_roles (account_id, role) VALUES (:account_id, 'LECTURER') "
                    "ON CONFLICT DO NOTHING"
                ),
                {"account_id": account_id},
            )
            lecturer_id = _id(
                session,
                """
                INSERT INTO lecturers (account_id, lecturer_code) VALUES (:account_id, :lecturer_code)
                ON CONFLICT (lecturer_code) DO UPDATE SET account_id = EXCLUDED.account_id
                RETURNING id
                """,
                {"account_id": account_id, "lecturer_code": lecturer["lecturer_code"]},
            )
            lecturer_ids[lecturer["lecturer_code"]] = lecturer_id

        for room in fixture["rooms"]:
            session.execute(
                text(
                    """
                    INSERT INTO rooms (code, name, capacity) VALUES (:code, :name, :capacity)
                    ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, capacity = EXCLUDED.capacity
                    """
                ),
                room,
            )

        student_ids: dict[str, int] = {}
        for student in fixture["students"]:
            student_account_id = _id(
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
                    "email": student["email"],
                    "display_name": student.get("display_name", student["student_code"]),
                    "password_hash": DEMO_PASSWORD_HASH,
                },
            )
            session.execute(
                text(
                    "INSERT INTO account_roles (account_id, role) VALUES (:account_id, 'STUDENT') "
                    "ON CONFLICT DO NOTHING"
                ),
                {"account_id": student_account_id},
            )
            student_id = _id(
                session,
                """
                INSERT INTO students (account_id, student_code) VALUES (:account_id, :student_code)
                ON CONFLICT (student_code) DO UPDATE SET account_id = EXCLUDED.account_id
                RETURNING id
                """,
                {"account_id": student_account_id, "student_code": student["student_code"]},
            )
            student_ids[student["student_code"]] = student_id

        group_count = 0
        for group in fixture["groups"]:
            project_id = _id(
                session,
                """
                INSERT INTO projects (semester_id, major_id, code, title)
                VALUES (:semester_id, :major_id, :code, :title)
                ON CONFLICT (semester_id, code) DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """,
                {
                    "semester_id": semester_id,
                    "major_id": major_id,
                    "code": group["project_code"],
                    "title": group["title"],
                },
            )
            group_id = _id(
                session,
                """
                INSERT INTO groups (project_id, code) VALUES (:project_id, :code)
                ON CONFLICT (project_id) DO UPDATE SET code = EXCLUDED.code
                RETURNING id
                """,
                {"project_id": project_id, "code": group["code"]},
            )
            for member in group["members"]:
                session.execute(
                    text(
                        """
                        INSERT INTO group_memberships (group_id, student_id, membership_role)
                        VALUES (:group_id, :student_id, :membership_role)
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    {
                        "group_id": group_id,
                        "student_id": student_ids[member["student_code"]],
                        "membership_role": member["role"],
                    },
                )
            for supervisor in group["supervisors"]:
                code, supervisor_type = supervisor.split(":", maxsplit=1)
                session.execute(
                    text(
                        """
                        INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type)
                        VALUES (:project_id, :lecturer_id, :supervisor_type)
                        ON CONFLICT (project_id, lecturer_id) DO UPDATE
                        SET supervisor_type = EXCLUDED.supervisor_type
                        """
                    ),
                    {
                        "project_id": project_id,
                        "lecturer_id": lecturer_ids[code],
                        "supervisor_type": supervisor_type,
                    },
                )
            group_count += 1

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
        "lecturers": len(fixture["lecturers"]),
        "groups": group_count,
        "students": len(fixture["students"]),
        "rooms": len(fixture["rooms"]),
    }
