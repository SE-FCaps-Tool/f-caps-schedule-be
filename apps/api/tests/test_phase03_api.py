from uuid import uuid4

import pytest


def _close_current_semester(client, headers):
    rows = client.get("/api/v1/semesters", headers=headers).json()
    active = next(row for row in rows if row["status"] == "ACTIVE")
    response = client.post(
        f"/api/v1/semesters/{active['id']}/transition",
        json={"target_status": "CLOSED", "reason": "Prepare isolated API test"},
        headers=headers,
    )
    assert response.status_code == 200
    return active["id"]


def _restore_current_semester(client, semester_id, headers):
    response = client.post(
        f"/api/v1/semesters/{semester_id}/set-current",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.integration
def test_manager_can_create_semester_and_duplicate_code_is_rejected(client):
    headers = {"X-Test-Session": "active-manager"}
    original_active_id = _close_current_semester(client, headers)
    code = f"API-{uuid4().hex[:8]}"
    payload = {
        "code": code,
        "name": "API Test Semester",
        "start_date": "2030-01-01",
        "end_date": "2030-04-15",
    }
    try:
        created = client.post("/api/v1/semesters", json=payload, headers=headers)
        assert created.status_code == 201
        assert created.json()["code"] == code.upper()
        assert created.json()["status"] == "ACTIVE"
        assert created.json()["start_date"] == "2030-01-01"
        assert created.json()["end_date"] == "2030-04-15"

        duplicate = client.post("/api/v1/semesters", json=payload, headers=headers)
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"]["code"] == "DATA_DUPLICATE"
    finally:
        _restore_current_semester(client, original_active_id, headers)


@pytest.mark.integration
def test_seed_fixture_is_idempotent_and_returns_target_counts(client):
    first = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    second = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})

    assert first.status_code == 201
    assert second.status_code in {200, 201}
    assert first.json()["counts"] == second.json()["counts"]
    assert first.json()["counts"]["accounts"] == 8
    assert first.json()["counts"]["rooms"] == 6


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
    original_active_id = _close_current_semester(client, headers)
    try:
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

        closed = client.post(
            f"/api/v1/semesters/{semester_id}/transition",
            json={"target_status": "CLOSED", "reason": "Semester completed"},
            headers=headers,
        )
        assert closed.status_code == 200
        assert closed.json() == {"id": semester_id, "status": "CLOSED"}
    finally:
        _restore_current_semester(client, original_active_id, headers)


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        ("2030-01-01", "2030-04-14"),
        ("2030-01-01", "2030-05-01"),
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


def test_semester_end_before_start_is_rejected_as_date_invalid(client):
    response = client.post(
        "/api/v1/semesters",
        json={
            "code": f"INVALID-{uuid4().hex[:8]}",
            "name": "Invalid Date Order",
            "start_date": "2030-04-15",
            "end_date": "2030-01-01",
        },
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "SEMESTER_DATE_INVALID"


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
            "room_types": ["NORMAL"],
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


@pytest.mark.integration
def test_group_can_be_created_before_project_and_assigned_later(client):
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    headers = {"X-Test-Session": "active-manager"}
    semesters = client.get("/api/v1/semesters", headers=headers).json()
    semester_id = next(item["id"] for item in semesters if item["code"] == "SE-2026-2027")
    majors = client.get("/api/v1/majors", headers=headers).json()
    students = client.get("/api/v1/students", headers=headers).json()[4:8]
    group_code = f"G-NOPROJ-{uuid4().hex[:6]}"

    created = client.post(
        "/api/v1/groups",
        json={
            "code": group_code,
            "members": [
                {"student_code": student["student_code"], "role": "LEADER" if index == 0 else "MEMBER"}
                for index, student in enumerate(students)
            ],
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    group_id = created.json()["id"]

    listed = next(item for item in client.get("/api/v1/groups", headers=headers).json() if item["id"] == group_id)
    assert listed["project_id"] is None
    assert listed["project_code"] is None

    detail = client.get(f"/api/v1/groups/{group_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["project_id"] is None

    project = client.post(
        "/api/v1/projects",
        json={
            "semester_id": semester_id,
            "major_id": majors[0]["id"],
            "code": f"P-NOPROJ-{uuid4().hex[:6]}",
            "title": "Assigned Later Project",
            "supervisors": ["GV01:MAIN"],
        },
        headers=headers,
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]

    assigned = client.patch(
        f"/api/v1/groups/{group_id}",
        json={"project_id": project_id},
        headers=headers,
    )
    assert assigned.status_code == 200, assigned.text
    assert assigned.json()["project_id"] == project_id

    detail_after = client.get(f"/api/v1/groups/{group_id}", headers=headers)
    assert detail_after.json()["project_id"] == project_id
    assert detail_after.json()["project_code"] == project.json()["code"]

    duplicate_assign = client.post(
        "/api/v1/groups",
        json={
            "code": f"G-DUP-{uuid4().hex[:6]}",
            "members": [
                {"student_code": student["student_code"], "role": "LEADER" if index == 0 else "MEMBER"}
                for index, student in enumerate(client.get("/api/v1/students", headers=headers).json()[8:12])
            ],
        },
        headers=headers,
    )
    assert duplicate_assign.status_code == 201, duplicate_assign.text
    conflict = client.patch(
        f"/api/v1/groups/{duplicate_assign.json()['id']}",
        json={"project_id": project_id},
        headers=headers,
    )
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "PROJECT_ALREADY_ASSIGNED"
