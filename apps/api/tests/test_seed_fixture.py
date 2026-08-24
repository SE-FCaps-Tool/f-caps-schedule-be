import pytest
from sqlalchemy import text

from app.config import get_settings
from app.database import get_engine
from app.domain.seed import FIXTURE_VERSION


@pytest.mark.integration
def test_seed_fixture_loads_ten_lecturers_thirty_groups_and_shared_round(client):
    response = client.post(
        "/api/v1/admin/seed-fixture",
        headers={"X-Test-Session": "active-admin"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["counts"] == {
        "version": FIXTURE_VERSION,
        "accounts": 140,
        "rooms": 6,
        "projects": 30,
        "groups": 30,
        "groupMembers": 120,
        "rounds": 1,
        "timeslots": 1,
        "acceptedInvitations": 10,
        "lecturerAvailabilities": 10,
        "groupPreferences": 30,
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
                    "(SELECT COUNT(DISTINCT g.code) FROM group_slot_preferences p "
                    "JOIN groups g ON g.id = p.group_id "
                    "WHERE p.round_id = r.id AND p.selected AND g.code LIKE 'DEMO-G%'), "
                "(SELECT COUNT(*) FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE rd.round_id = r.id) "
                "FROM rounds r WHERE r.name = 'DEMO-ROUND-SHARED-SLOT' GROUP BY r.id"
            )
        ).one()

    assert lecturer_count == 10
    assert group_sizes == [(f"DEMO-G{i:02d}", 4) for i in range(1, 31)]
    assert tuple(round_counts) == (1, 10, 10, 30, 1)
