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
                        ON CONFLICT (account_id) DO NOTHING
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
                        ON CONFLICT (account_id) DO NOTHING
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

        demo_groups = fixture.get("demo_groups", [])
        demo_group_ids: list[int] = []
        if demo_groups:
            semester_id = _id(
                session,
                "SELECT id FROM semesters WHERE code = :code",
                {"code": semester_data["code"]},
            )
            major_id = _id(
                session,
                "SELECT id FROM majors WHERE code = :code",
                {"code": fixture["major"]["code"]},
            )
            lecturer_ids = {
                row[0]: row[1]
                for row in session.execute(
                    text(
                        "SELECT l.lecturer_code, l.id FROM lecturers l "
                        "WHERE l.lecturer_code = ANY(:codes)"
                    ),
                    {
                        "codes": [
                            group["supervisor_code"] for group in demo_groups
                        ]
                    },
                ).all()
            }
            student_ids = {
                row[0]: row[1]
                for row in session.execute(
                    text(
                        "SELECT s.student_code, s.id FROM students s "
                        "WHERE s.student_code = ANY(:codes)"
                    ),
                    {
                        "codes": sorted(
                            {
                                code
                                for group in demo_groups
                                for code in group["student_codes"]
                            }
                        )
                    },
                ).all()
            }
            for demo_group in demo_groups:
                project_id = _id(
                    session,
                    """
                    INSERT INTO projects (semester_id, major_id, code, title)
                    VALUES (:semester_id, :major_id, :code, :title)
                    ON CONFLICT (semester_id, code) DO UPDATE SET
                        major_id = EXCLUDED.major_id,
                        title = EXCLUDED.title,
                        status = 'ACTIVE'
                    RETURNING id
                    """,
                    {
                        "semester_id": semester_id,
                        "major_id": major_id,
                        "code": demo_group["project_code"],
                        "title": demo_group["project_title"],
                    },
                )
                session.execute(
                    text(
                        "INSERT INTO project_supervisors "
                        "(project_id, lecturer_id, supervisor_type) "
                        "VALUES (:project_id, :lecturer_id, 'MAIN') "
                        "ON CONFLICT (project_id, lecturer_id) DO UPDATE SET "
                        "supervisor_type = EXCLUDED.supervisor_type"
                    ),
                    {
                        "project_id": project_id,
                        "lecturer_id": lecturer_ids[demo_group["supervisor_code"]],
                    },
                )
                group_id = _id(
                    session,
                    """
                    INSERT INTO groups (project_id, code, status)
                    VALUES (:project_id, :code, 'PENDING_D11')
                    ON CONFLICT (project_id) DO UPDATE SET
                        code = EXCLUDED.code,
                        status = EXCLUDED.status
                    RETURNING id
                    """,
                    {
                        "project_id": project_id,
                        "code": demo_group["group_code"],
                    },
                )
                demo_group_ids.append(group_id)
                leader_code = demo_group["student_codes"][0]
                desired_student_ids = [student_ids[code] for code in demo_group["student_codes"]]
                session.execute(
                    text(
                        "UPDATE group_memberships SET membership_role = 'MEMBER' "
                        "WHERE group_id = :group_id AND status = 'ACTIVE' "
                        "AND membership_role = 'LEADER' AND student_id <> :leader_id"
                    ),
                    {"group_id": group_id, "leader_id": student_ids[leader_code]},
                )
                session.execute(
                    text(
                        """
                        UPDATE group_memberships
                        SET status = 'DROPPED',
                            left_at = GREATEST(now() + INTERVAL '1 second', joined_at + INTERVAL '1 second'),
                            reason = 'Seed fixture reconciled'
                        WHERE status = 'ACTIVE'
                          AND group_id <> :group_id
                          AND student_id = ANY(:student_ids)
                          AND group_id IN (
                              SELECT g2.id FROM groups g2 WHERE g2.code LIKE 'DEMO-G%'
                          )
                        """
                    ),
                    {"group_id": group_id, "student_ids": desired_student_ids},
                )
                session.execute(
                    text(
                        """
                        UPDATE group_memberships
                        SET status = 'DROPPED',
                            left_at = GREATEST(now() + INTERVAL '1 second', joined_at + INTERVAL '1 second'),
                            reason = 'Seed fixture reconciled'
                        WHERE status = 'ACTIVE'
                          AND group_id = :group_id
                          AND NOT (student_id = ANY(:student_ids))
                        """
                    ),
                    {"group_id": group_id, "student_ids": desired_student_ids},
                )
                for student_code in demo_group["student_codes"]:
                    student_id = student_ids[student_code]
                    membership = session.execute(
                        text(
                            "SELECT id FROM group_memberships "
                            "WHERE group_id = :group_id AND student_id = :student_id "
                            "AND status = 'ACTIVE'"
                        ),
                        {"group_id": group_id, "student_id": student_id},
                    ).scalar_one_or_none()
                    role = "LEADER" if student_code == leader_code else "MEMBER"
                    if membership is None:
                        session.execute(
                            text(
                                "INSERT INTO group_memberships "
                                "(group_id, student_id, membership_role) "
                                "VALUES (:group_id, :student_id, :role)"
                            ),
                            {
                                "group_id": group_id,
                                "student_id": student_id,
                                "role": role,
                            },
                        )
                    else:
                        session.execute(
                            text(
                                "UPDATE group_memberships SET membership_role = :role "
                                "WHERE id = :membership_id"
                            ),
                            {"membership_id": membership, "role": role},
                        )

        demo_round = fixture.get("demo_round")
        round_id: int | None = None
        timeslot_id: int | None = None
        group_preference_count = 0
        if demo_round and demo_group_ids:
            manager_id = actor_id or session.execute(
                text("SELECT id FROM accounts WHERE email = 'manager@gmail.com'")
            ).scalar_one_or_none()
            existing_round = session.execute(
                text(
                    "SELECT id FROM rounds WHERE semester_id = :semester_id AND name = :name"
                ),
                {"semester_id": semester_id, "name": demo_round["name"]},
            ).scalar_one_or_none()
            if existing_round is None:
                round_id = _id(
                    session,
                    """
                    INSERT INTO rounds (
                        semester_id, name, description, type, status, reviewer_count,
                        session_duration_minutes, start_date, end_date,
                        registration_deadline, group_preference_deadline,
                        group_selection_mode, h12_sessions_per_part, h12_sessions_per_day,
                        created_by
                    ) VALUES (
                        :semester_id, :name, :description, CAST(:type AS round_type),
                        CAST(:status AS round_status), :reviewer_count,
                        :session_duration_minutes, :start_date, :end_date,
                        :registration_deadline, :group_preference_deadline,
                        :group_selection_mode, :h12_sessions_per_part, :h12_sessions_per_day,
                        :created_by
                    ) RETURNING id
                    """,
                    {**demo_round, "semester_id": semester_id, "created_by": manager_id},
                )
            else:
                round_id = int(existing_round)

            for room_type in demo_round["room_types"]:
                session.execute(
                    text(
                        "INSERT INTO round_room_types (round_id, room_type) "
                        "VALUES (:round_id, CAST(:room_type AS room_type)) ON CONFLICT DO NOTHING"
                    ),
                    {"round_id": round_id, "room_type": room_type},
                )

            configured_timeslots = demo_round.get("timeslots") or [demo_round["timeslot"]]
            timeslot_ids: list[int] = []
            for configured_timeslot in configured_timeslots:
                day_id = _id(
                    session,
                    """
                    INSERT INTO round_days (round_id, day_date)
                    VALUES (:round_id, :day_date)
                    ON CONFLICT (round_id, day_date) DO UPDATE SET day_date = EXCLUDED.day_date
                    RETURNING id
                    """,
                    {"round_id": round_id, "day_date": configured_timeslot["day_date"]},
                )
                timeslot_ids.append(
                    _id(
                        session,
                        """
                        INSERT INTO timeslots (round_day_id, start_at, end_at, part)
                        VALUES (:round_day_id, :start_at, :end_at, :part)
                        ON CONFLICT (round_day_id, start_at, end_at) DO UPDATE SET active = TRUE
                        RETURNING id
                        """,
                        {"round_day_id": day_id, **configured_timeslot},
                    )
                )
            timeslot_id = timeslot_ids[0]
            for group_id in demo_group_ids:
                session.execute(
                    text(
                        "INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {"round_id": round_id, "group_id": group_id},
                )
            if demo_round.get("group_preference_mode") == "SINGLE_SLOT":
                session.execute(
                    text("DELETE FROM group_slot_preferences WHERE round_id = :round_id"),
                    {"round_id": round_id},
                )
            for lecturer_id in lecturer_ids.values():
                session.execute(
                    text(
                        """
                        INSERT INTO round_invitations
                            (round_id, lecturer_id, status, responded_at)
                        VALUES (:round_id, :lecturer_id, 'ACCEPTED', now())
                        ON CONFLICT (round_id, lecturer_id) DO UPDATE SET
                            status = 'ACCEPTED', responded_at = COALESCE(round_invitations.responded_at, now())
                        """
                    ),
                    {"round_id": round_id, "lecturer_id": lecturer_id},
                )
                for available_timeslot_id in timeslot_ids:
                    session.execute(
                        text(
                            """
                            INSERT INTO lecturer_availabilities
                                (round_id, lecturer_id, timeslot_id, state, load_preference, source, updated_by)
                            VALUES (:round_id, :lecturer_id, :timeslot_id, 'AVAILABLE', 'MEDIUM', 'MANAGER', :updated_by)
                            ON CONFLICT (round_id, lecturer_id, timeslot_id) DO UPDATE SET
                                state = 'AVAILABLE', load_preference = 'MEDIUM', source = 'MANAGER', updated_by = EXCLUDED.updated_by
                            """
                        ),
                        {"round_id": round_id, "lecturer_id": lecturer_id, "timeslot_id": available_timeslot_id, "updated_by": manager_id},
                    )
            for group_index, group_id in enumerate(demo_group_ids):
                if demo_round.get("group_preference_mode") == "SINGLE_SLOT":
                    preferred_timeslot_ids = [
                        timeslot_ids[demo_groups[group_index].get("preferred_slot_index", group_index) % len(timeslot_ids)]
                    ]
                else:
                    preferred_timeslot_ids = timeslot_ids
                for preferred_timeslot_id in preferred_timeslot_ids:
                    session.execute(
                        text(
                            """
                            INSERT INTO group_slot_preferences
                                (round_id, group_id, timeslot_id, selected, source, updated_by)
                            VALUES (:round_id, :group_id, :timeslot_id, TRUE, 'MANAGER', :updated_by)
                            ON CONFLICT (round_id, group_id, timeslot_id) DO UPDATE SET
                                selected = TRUE, source = 'MANAGER', updated_by = EXCLUDED.updated_by
                            """
                        ),
                        {"round_id": round_id, "group_id": group_id, "timeslot_id": preferred_timeslot_id, "updated_by": manager_id},
                    )
                    group_preference_count += 1

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
        "projects": len(demo_groups),
        "groups": len(demo_groups),
        "group_members": sum(len(group["student_codes"]) for group in demo_groups),
        "rounds": 1 if round_id is not None else 0,
        "timeslots": len(timeslot_ids) if timeslot_id is not None else 0,
        "accepted_invitations": len(lecturer_ids) if round_id is not None else 0,
        "lecturer_availabilities": len(lecturer_ids) * len(timeslot_ids) if timeslot_id is not None else 0,
        "group_preferences": group_preference_count,
    }
