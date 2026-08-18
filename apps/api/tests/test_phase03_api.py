from uuid import uuid4

import pytest


@pytest.mark.integration
def test_manager_can_create_semester_and_duplicate_code_is_rejected(client):
    code = f"API-{uuid4().hex[:8]}"
    payload = {
        "code": code,
        "name": "API Test Semester",
        "start_date": "2030-01-01",
        "end_date": "2030-04-15",
    }
    created = client.post("/api/v1/semesters", json=payload, headers={"X-Test-Session": "active-manager"})
    assert created.status_code == 201
    assert created.json()["code"] == code.upper()
    assert created.json()["status"] == "UPCOMING"
    assert created.json()["start_date"] == "2030-01-01"
    assert created.json()["end_date"] == "2030-04-15"

    duplicate = client.post(
        "/api/v1/semesters", json=payload, headers={"X-Test-Session": "active-manager"}
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "DATA_DUPLICATE"


@pytest.mark.integration
def test_seed_fixture_is_idempotent_and_returns_target_counts(client):
    first = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    second = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})

    assert first.status_code == 201
    assert second.status_code in {200, 201}
    assert first.json()["counts"] == second.json()["counts"]
    assert first.json()["counts"]["lecturers"] == 26
    assert first.json()["counts"]["groups"] == 74


def test_invalid_semester_payload_is_rejected_before_database_access(client):
    response = client.post(
        "/api/v1/semesters",
        json={"code": "   ", "name": "Missing code"},
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_semester_duration_and_status_transitions(client):
    headers = {"X-Test-Session": "active-manager"}
    created = client.post(
        "/api/v1/semesters",
        json={
            "code": f"DURATION-{uuid4().hex[:8]}",
            "name": "Duration Test Semester",
            "start_date": "2030-01-01",
            "end_date": "2030-04-15",
        },
        headers=headers,
    )
    assert created.status_code == 201
    semester_id = created.json()["id"]

    activated = client.post(
        f"/api/v1/semesters/{semester_id}/transition",
        json={"target_status": "ACTIVE", "reason": "Open semester"},
        headers=headers,
    )
    assert activated.status_code == 200
    assert activated.json() == {"id": semester_id, "status": "ACTIVE"}

    closed = client.post(
        f"/api/v1/semesters/{semester_id}/transition",
        json={"target_status": "CLOSED", "reason": "Semester completed"},
        headers=headers,
    )
    assert closed.status_code == 200
    assert closed.json() == {"id": semester_id, "status": "CLOSED"}


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        ("2030-01-01", "2030-04-14"),
        ("2030-01-01", "2030-05-01"),
        ("2030-04-15", "2030-01-01"),
    ],
)
def test_invalid_semester_duration_is_rejected(client, start_date, end_date):
    response = client.post(
        "/api/v1/semesters",
        json={
            "code": f"INVALID-{uuid4().hex[:8]}",
            "name": "Invalid Duration",
            "start_date": start_date,
            "end_date": end_date,
        },
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "SEMESTER_DURATION_INVALID"


def test_manager_only_endpoint_rejects_lecturer(client):
    response = client.post(
        "/api/v1/admin/seed-fixture",
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_manager_can_create_round_day_and_manager_entered_availability(client):
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    semesters = client.get("/api/v1/semesters", headers={"X-Test-Session": "active-manager"}).json()
    semester_id = next(item["id"] for item in semesters if item["code"] == "SE-2026-2027")
    created_round = client.post(
        "/api/v1/rounds",
        json={
            "semester_id": semester_id,
            "type": "DEFENSE_1_1",
            "reviewer_count": 3,
            "result_owner_mode": True,
            "session_duration_minutes": 30,
        },
        headers={"X-Test-Session": "active-manager"},
    )
    assert created_round.status_code == 201
    round_id = created_round.json()["id"]
    day = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={
            "day_date": "2030-02-01",
            "slots": [
                {"start_at": "2030-02-01T09:00:00+07:00", "end_at": "2030-02-01T09:30:00+07:00"},
                {"start_at": "2030-02-01T09:30:00+07:00", "end_at": "2030-02-01T10:00:00+07:00"},
            ],
        },
        headers={"X-Test-Session": "active-manager"},
    )
    assert day.status_code == 201
    lecturer_id = client.get("/api/v1/lecturers", headers={"X-Test-Session": "active-manager"}).json()[0]["id"]
    availability = client.post(
        f"/api/v1/rounds/{round_id}/lecturers/{lecturer_id}/availability",
        json={"selected_timeslot_ids": day.json()["timeslot_ids"][:1], "load_preference": "HIGH"},
        headers={"X-Test-Session": "active-manager"},
    )
    assert availability.status_code == 200
    assert availability.json()["source"] == "MANAGER"


@pytest.mark.integration
def test_group_mutation_validates_leader_and_rolls_back_atomically(client):
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    headers = {"X-Test-Session": "active-manager"}
    semesters = client.get("/api/v1/semesters", headers=headers).json()
    semester_id = next(item["id"] for item in semesters if item["code"] == "SE-2026-2027")
    majors = client.get("/api/v1/majors", headers=headers).json()
    before = len(client.get("/api/v1/groups", headers=headers).json())
    project = client.post(
        "/api/v1/projects",
        json={
            "semester_id": semester_id,
            "major_id": majors[0]["id"],
            "code": f"P-API-{uuid4().hex[:6]}",
            "title": "API Project",
            "supervisors": ["GV01:MAIN"],
        },
        headers=headers,
    )
    assert project.status_code == 201
    students = client.get("/api/v1/students", headers=headers).json()[:4]
    invalid = client.post(
        "/api/v1/groups",
        json={
            "project_id": project.json()["id"],
            "code": "G-INVALID",
            "members": [{"student_code": student["student_code"], "role": "MEMBER"} for student in students],
        },
        headers=headers,
    )
    assert invalid.status_code == 422
    assert invalid.json()["detail"]["code"] == "LEADER_REQUIRED"
    assert len(client.get("/api/v1/groups", headers=headers).json()) == before
