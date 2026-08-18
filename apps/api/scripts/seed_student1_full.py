"""Seed student1@gmail.com with a full profile: account, student record,
semester, major, project, group (as LEADER), supervisor + reviewer
lecturers, a published defense round, and a scheduled session.

Run inside the api container:
    docker compose exec api python scripts/seed_student1_full.py
"""

from datetime import date, datetime, timedelta, timezone

from argon2 import PasswordHasher
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine

EMAIL = "student1@gmail.com"
PASSWORD = "12345@Abc"
DISPLAY_NAME = "Student One"
STUDENT_CODE = "SV_DEMO1"

SEMESTER = {"code": "SE-2026-2027", "name": "Software Engineering 2026–2027"}
MAJOR = {"code": "SE", "name": "Software Engineering"}
LECTURER = {
    "email": "lecturer1@gmail.com",
    "display_name": "Lecturer One",
    "lecturer_code": "GV_DEMO1",
}
REVIEWER = {
    "email": "lecturer2@gmail.com",
    "display_name": "Lecturer Two",
    "lecturer_code": "GV_DEMO2",
}
PROJECT = {"code": "P_DEMO1", "title": "Demo Capstone Project 1"}
GROUP_CODE = "G_DEMO1"
ROOM = {"code": "R_DEMO1", "name": "Demo Defense Room 1", "capacity": 12}

ROUND_DAY = date.today() + timedelta(days=7)
SESSION_START = datetime.combine(ROUND_DAY, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=9)
SESSION_END = SESSION_START + timedelta(minutes=45)


def _insert_lecturer(session: Session, password_hash: str, data: dict[str, str]) -> tuple[int, int]:
    account_id = _id(
        session,
        """
        INSERT INTO accounts (email, display_name, password_hash)
        VALUES (:email, :display_name, :password_hash)
        ON CONFLICT (email) DO UPDATE SET
            display_name = EXCLUDED.display_name,
            status = 'ACTIVE'
        RETURNING id
        """,
        {"email": data["email"], "display_name": data["display_name"], "password_hash": password_hash},
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
        {"account_id": account_id, "lecturer_code": data["lecturer_code"]},
    )
    return account_id, lecturer_id


def _id(session: Session, query: str, params: dict[str, object]) -> int:
    return int(session.execute(text(query), params).scalar_one())


def main() -> None:
    password_hash = PasswordHasher().hash(PASSWORD)
    engine = get_engine(get_settings().database_url)
    with Session(engine) as session, session.begin():
        semester_id = _id(
            session,
            """
            INSERT INTO semesters (code, name, start_date, end_date, status)
            VALUES (:code, :name, :start_date, :end_date, 'ACTIVE')
            ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                status = 'ACTIVE'
            RETURNING id
            """,
            {**SEMESTER, "start_date": "2026-05-11", "end_date": "2026-08-23"},
        )
        major_id = _id(
            session,
            """
            INSERT INTO majors (code, name) VALUES (:code, :name)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            MAJOR,
        )

        _, lecturer_id = _insert_lecturer(session, password_hash, LECTURER)
        _, reviewer_id = _insert_lecturer(session, password_hash, REVIEWER)

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
            {"email": EMAIL, "display_name": DISPLAY_NAME, "password_hash": password_hash},
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
            {"account_id": student_account_id, "student_code": STUDENT_CODE},
        )

        project_id = _id(
            session,
            """
            INSERT INTO projects (semester_id, major_id, code, title)
            VALUES (:semester_id, :major_id, :code, :title)
            ON CONFLICT (semester_id, code) DO UPDATE SET title = EXCLUDED.title
            RETURNING id
            """,
            {"semester_id": semester_id, "major_id": major_id, **PROJECT},
        )
        group_id = _id(
            session,
            """
            INSERT INTO groups (project_id, code) VALUES (:project_id, :code)
            ON CONFLICT (project_id) DO UPDATE SET code = EXCLUDED.code
            RETURNING id
            """,
            {"project_id": project_id, "code": GROUP_CODE},
        )
        session.execute(
            text(
                """
                INSERT INTO group_memberships (group_id, student_id, membership_role)
                VALUES (:group_id, :student_id, 'LEADER')
                ON CONFLICT DO NOTHING
                """
            ),
            {"group_id": group_id, "student_id": student_id},
        )
        session.execute(
            text(
                """
                INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type)
                VALUES (:project_id, :lecturer_id, 'MAIN')
                ON CONFLICT (project_id, lecturer_id) DO UPDATE
                SET supervisor_type = EXCLUDED.supervisor_type
                """
            ),
            {"project_id": project_id, "lecturer_id": lecturer_id},
        )

        room_id = _id(
            session,
            """
            INSERT INTO rooms (code, name, capacity) VALUES (:code, :name, :capacity)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, capacity = EXCLUDED.capacity
            RETURNING id
            """,
            ROOM,
        )

        round_id = session.execute(
            text("SELECT id FROM rounds WHERE semester_id = :semester_id AND type = 'DEFENSE_1_1'"),
            {"semester_id": semester_id},
        ).scalar_one_or_none()
        if round_id is None:
            round_id = _id(
                session,
                """
                INSERT INTO rounds
                    (semester_id, type, status, session_duration_minutes, reviewer_count, result_owner_mode)
                VALUES (:semester_id, 'DEFENSE_1_1', 'PUBLISHED', 45, 1, TRUE)
                RETURNING id
                """,
                {"semester_id": semester_id},
            )

        round_day_id = _id(
            session,
            """
            INSERT INTO round_days (round_id, day_date) VALUES (:round_id, :day_date)
            ON CONFLICT (round_id, day_date) DO UPDATE SET day_date = EXCLUDED.day_date
            RETURNING id
            """,
            {"round_id": round_id, "day_date": ROUND_DAY},
        )
        timeslot_id = _id(
            session,
            """
            INSERT INTO timeslots (round_day_id, start_at, end_at)
            VALUES (:round_day_id, :start_at, :end_at)
            ON CONFLICT (round_day_id, start_at, end_at) DO UPDATE SET end_at = EXCLUDED.end_at
            RETURNING id
            """,
            {"round_day_id": round_day_id, "start_at": SESSION_START, "end_at": SESSION_END},
        )

        session.execute(
            text(
                "INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id) "
                "ON CONFLICT DO NOTHING"
            ),
            {"round_id": round_id, "group_id": group_id},
        )
        session.execute(
            text(
                "INSERT INTO round_rooms (round_id, room_id) VALUES (:round_id, :room_id) "
                "ON CONFLICT DO NOTHING"
            ),
            {"round_id": round_id, "room_id": room_id},
        )
        for lid in (lecturer_id, reviewer_id):
            session.execute(
                text(
                    """
                    INSERT INTO round_invitations (round_id, lecturer_id, status, responded_at)
                    VALUES (:round_id, :lecturer_id, 'ACCEPTED', now())
                    ON CONFLICT (round_id, lecturer_id) DO UPDATE SET status = 'ACCEPTED'
                    """
                ),
                {"round_id": round_id, "lecturer_id": lid},
            )
            session.execute(
                text(
                    """
                    INSERT INTO lecturer_availabilities (round_id, lecturer_id, timeslot_id, state)
                    VALUES (:round_id, :lecturer_id, :timeslot_id, 'AVAILABLE')
                    ON CONFLICT (round_id, lecturer_id, timeslot_id) DO UPDATE SET state = 'AVAILABLE'
                    """
                ),
                {"round_id": round_id, "lecturer_id": lid, "timeslot_id": timeslot_id},
            )

        schedule_version_id = _id(
            session,
            """
            INSERT INTO schedule_versions (round_id, version_no, status, activated_at)
            VALUES (:round_id, 1, 'PUBLISHED', now())
            ON CONFLICT (round_id, version_no) DO UPDATE SET status = 'PUBLISHED', activated_at = now()
            RETURNING id
            """,
            {"round_id": round_id},
        )

        session_id = _id(
            session,
            """
            INSERT INTO sessions (schedule_version_id, group_id, timeslot_id, room_id, start_at, end_at, status)
            VALUES (:schedule_version_id, :group_id, :timeslot_id, :room_id, :start_at, :end_at, 'SCHEDULED')
            ON CONFLICT (schedule_version_id, group_id) DO UPDATE SET status = 'SCHEDULED'
            RETURNING id
            """,
            {
                "schedule_version_id": schedule_version_id,
                "group_id": group_id,
                "timeslot_id": timeslot_id,
                "room_id": room_id,
                "start_at": SESSION_START,
                "end_at": SESSION_END,
            },
        )
        for lid, role, is_owner, snapshot_name in (
            (lecturer_id, "SUPERVISOR", True, LECTURER["display_name"]),
            (reviewer_id, "REVIEWER", False, REVIEWER["display_name"]),
        ):
            session.execute(
                text(
                    """
                    INSERT INTO session_reviewers
                        (session_id, schedule_version_id, lecturer_id, assignment, is_result_owner,
                         snapshot_name, start_at, end_at)
                    VALUES (:session_id, :schedule_version_id, :lecturer_id, :assignment, :is_result_owner,
                            :snapshot_name, :start_at, :end_at)
                    ON CONFLICT (session_id, lecturer_id) DO UPDATE SET assignment = EXCLUDED.assignment
                    """
                ),
                {
                    "session_id": session_id,
                    "schedule_version_id": schedule_version_id,
                    "lecturer_id": lid,
                    "assignment": role,
                    "is_result_owner": is_owner,
                    "snapshot_name": snapshot_name,
                    "start_at": SESSION_START,
                    "end_at": SESSION_END,
                },
            )

        print(f"seeded STUDENT -> {EMAIL} (code={STUDENT_CODE}, group={GROUP_CODE}, leader=True)")
        print(f"seeded LECTURER -> {LECTURER['email']} (supervisor of {PROJECT['code']})")
        print(f"seeded LECTURER -> {REVIEWER['email']} (reviewer of {PROJECT['code']})")
        print(f"seeded ROUND -> DEFENSE_1_1 (round_id={round_id}, published)")
        print(f"seeded SESSION -> {SESSION_START.isoformat()} - {SESSION_END.isoformat()} in {ROOM['code']}")


if __name__ == "__main__":
    main()
