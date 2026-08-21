import pytest
from sqlalchemy import text

from app.config import get_settings
from app.database import get_engine
from app.domain.seed import FIXTURE_VERSION, seed_fixture_v1


def test_seed_fixture_is_deterministic_and_has_target_shape():
    first = seed_fixture_v1()
    second = seed_fixture_v1()

    assert first == second
    assert first["version"] == FIXTURE_VERSION
    assert first["password"] == "12345@Abc"
    assert first["semester"]["code"] == "SE-2026-2027"
    assert first["major"]["code"] == "SE"

    accounts = first["accounts"]
    assert len(accounts) == 132
    assert [a["email"] for a in accounts if a["role"] == "ADMIN"] == ["admin@gmail.com"]
    assert [a["email"] for a in accounts if a["role"] == "MANAGER"] == ["manager@gmail.com"]
    assert [a["email"] for a in accounts if a["role"] == "LECTURER"] == [
        "lecturer@gmail.com",
        *[f"lecturer{i}@gmail.com" for i in range(2, 11)],
    ]
    assert [a["email"] for a in accounts if a["role"] == "STUDENT"] == [
        f"student{i}@gmail.com" for i in range(1, 121)
    ]

    demo_groups = first["demo_groups"]
    assert len(demo_groups) == 30
    assert [len(group["student_codes"]) for group in demo_groups] == [4] * 30
    assert [group["supervisor_code"] for group in demo_groups] == [
        f"GV{((i - 1) % 10) + 1:02d}" for i in range(1, 31)
    ]
    assert first["demo_round"]["type"] == "REVIEW_1"
    assert first["demo_round"]["group_selection_mode"] is True
    assert first["demo_round"]["timeslot"]["start_at"] == "2026-08-22T09:00:00+07:00"

    rooms = first["rooms"]
    assert len(rooms) == 6
    for room_type in ("NORMAL", "SEMINAR", "LAB"):
        matching = [r for r in rooms if r["room_type"] == room_type]
        assert len(matching) == 2
        assert all(r["capacity"] == 12 for r in matching)


@pytest.mark.integration
def test_seed_fixture_loads_ten_lecturers_thirty_groups_and_shared_round(client):
    response = client.post(
        "/api/v1/admin/seed-fixture",
        headers={"X-Test-Session": "active-admin"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["counts"] == {
        "version": FIXTURE_VERSION,
        "accounts": 132,
        "rooms": 6,
        "projects": 30,
        "groups": 30,
        "group_members": 120,
        "rounds": 1,
        "timeslots": 1,
        "accepted_invitations": 10,
        "lecturer_availabilities": 10,
        "group_preferences": 30,
    }

    engine = get_engine(get_settings().database_url)
    with engine.begin() as db:
        lecturer_count = db.execute(
            text(
                "SELECT COUNT(*) FROM lecturers "
                "WHERE lecturer_code = ANY(:codes)"
            ),
            {"codes": [f"GV{i:02d}" for i in range(1, 11)]},
        ).scalar_one()
        group_sizes = db.execute(
            text(
                "SELECT g.code, COUNT(gm.id) "
                "FROM groups g JOIN group_memberships gm ON gm.group_id = g.id "
                "AND gm.status = 'ACTIVE' "
                "WHERE g.code = ANY(:codes) "
                "GROUP BY g.code ORDER BY g.code"
            ),
            {"codes": [f"DEMO-G{i:02d}" for i in range(1, 31)]},
        ).all()
        round_counts = db.execute(
            text(
                "SELECT COUNT(*), "
                "(SELECT COUNT(*) FROM round_invitations WHERE round_id = r.id AND status = 'ACCEPTED'), "
                "(SELECT COUNT(*) FROM lecturer_availabilities WHERE round_id = r.id AND state = 'AVAILABLE'), "
                "(SELECT COUNT(*) FROM group_slot_preferences WHERE round_id = r.id AND selected), "
                "(SELECT COUNT(*) FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE rd.round_id = r.id) "
                "FROM rounds r WHERE r.name = 'DEMO-ROUND-SHARED-SLOT' GROUP BY r.id"
            )
        ).one()

    assert lecturer_count == 10
    assert group_sizes == [(f"DEMO-G{i:02d}", 4) for i in range(1, 31)]
    assert tuple(round_counts) == (1, 10, 10, 30, 1)
