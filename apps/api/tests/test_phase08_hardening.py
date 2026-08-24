from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.config import get_settings
from app.database import get_engine
from app.main import create_app


@pytest.mark.integration
def test_concurrent_activation_keeps_one_active_version(client):
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text
    engine = get_engine(get_settings().database_url)
    with engine.begin() as db:
        semester_id = db.execute(text("SELECT id FROM semesters WHERE code = 'SE-2026-2027'")).scalar_one()
        round_id = db.execute(
            text(
                "INSERT INTO rounds (semester_id, type, status, reviewer_count, session_duration_minutes) "
                "VALUES (:semester_id, 'REVIEW_1', CAST('SCHEDULED' AS round_status), 2, 30) RETURNING id"
            ),
            {"semester_id": semester_id},
        ).scalar_one()
        version_ids = []
        for version_no in (1, 2):
            version_ids.append(
                db.execute(
                    text(
                        "INSERT INTO schedule_versions (round_id, version_no, status, input_snapshot, algorithm_parameters) "
                        "VALUES (:round_id, :version_no, CAST('DRAFT' AS schedule_version_status), '{}'::jsonb, '{}'::jsonb) RETURNING id"
                    ),
                    {"round_id": round_id, "version_no": version_no},
                ).scalar_one()
            )

    def activate(version_id: int) -> int:
        with TestClient(create_app()) as isolated_client:
            return isolated_client.post(
                f"/api/v1/schedule/versions/{version_id}/activate",
                headers={"X-Test-Session": "active-manager"},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(activate, version_ids))

    assert statuses.count(200) == 1
    assert statuses.count(422) == 1
    with engine.begin() as db:
        active_count = db.execute(
            text(
                "SELECT COUNT(*) FROM schedule_versions "
                "WHERE round_id = :round_id AND status = 'ACTIVE' AND activated_at IS NOT NULL"
            ),
            {"round_id": round_id},
        ).scalar_one()
        db.execute(text("DELETE FROM rounds WHERE id = :round_id"), {"round_id": round_id})
    assert active_count == 1


@pytest.mark.integration
def test_h11_waiver_is_manager_only_at_the_route_boundary(client):
    payload = {"reason": "Approved continuity exception"}
    admin = client.post("/api/v1/rounds/1/groups/1/h11-waiver", json=payload, headers={"X-Test-Session": "active-admin"})
    lecturer = client.post("/api/v1/rounds/1/groups/1/h11-waiver", json=payload, headers={"X-Test-Session": "active-lecturer:2"})
    assert admin.status_code == 403
    assert lecturer.status_code == 403


@pytest.mark.integration
def test_round_operation_and_locked_round_unlock_are_authorized_and_audited(client):
    manager_headers = {"X-Test-Session": "active-manager"}
    admin_headers = {"X-Test-Session": "active-admin"}
    assert client.post("/api/v1/admin/seed-fixture", headers=admin_headers).status_code == 201
    semester_id = next(item["id"] for item in client.get("/api/v1/semesters", headers=manager_headers).json()["data"] if item["code"] == "SE-2026-2027")
    round_response = client.post(
        "/api/v1/rounds",
        json={"semester_id": semester_id, "type": "REVIEW_1", "reviewer_count": 2, "room_types": ["NORMAL"], "session_duration_minutes": 30, "startDate": "2030-03-01", "endDate": "2030-03-01"},
        headers=manager_headers,
    )
    assert round_response.status_code == 201, round_response.text
    round_id = round_response.json()["id"]
    cancelled = client.post(f"/api/v1/rounds/{round_id}/operation", json={"action": "CANCELLED", "reason": "Local acceptance cleanup"}, headers=manager_headers)
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "CANCELLED"

    engine = get_engine(get_settings().database_url)
    with engine.begin() as db:
        locked_id = db.execute(
            text(
                "INSERT INTO rounds (semester_id, type, status, reviewer_count, session_duration_minutes) "
                "VALUES (:semester_id, 'REVIEW_1', CAST('LOCKED' AS round_status), 2, 30) RETURNING id"
            ),
            {"semester_id": semester_id},
        ).scalar_one()
    unlocked = client.post(f"/api/v1/rounds/{locked_id}/unlock", json={"reason": "Admin unlock acceptance"}, headers=admin_headers)
    assert unlocked.status_code == 200, unlocked.text
    assert unlocked.json()["status"] == "COMPLETED"
    manager_unlock = client.post(f"/api/v1/rounds/{locked_id}/unlock", json={"reason": "Must be denied"}, headers=manager_headers)
    assert manager_unlock.status_code == 403
    with engine.begin() as db:
        db.execute(text("DELETE FROM rounds WHERE id IN (:round_id, :locked_id)"), {"round_id": round_id, "locked_id": locked_id})
