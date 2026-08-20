import pytest


@pytest.mark.integration
def test_manager_can_run_activate_and_publish_a_schedule_version(client):
    headers = {"X-Test-Session": "active-manager"}
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    semester_id = next(
        item["id"]
        for item in client.get("/api/v1/semesters", headers=headers).json()["data"]
        if item["code"] == "SE-2026-2027"
    )
    round_response = client.post(
        "/api/v1/rounds",
        json={
            "semester_id": semester_id,
            "type": "DEFENSE_1_1",
            "reviewer_count": 3,
            "room_types": ["NORMAL"],
            "session_duration_minutes": 30,
        },
        headers=headers,
    )
    assert round_response.status_code == 201
    round_id = round_response.json()["id"]
    day_response = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={
            "day_date": "2031-03-01",
            "slots": [{"start_at": "2031-03-01T09:00:00+07:00", "end_at": "2031-03-01T09:30:00+07:00"}],
        },
        headers=headers,
    )
    assert day_response.status_code == 201
    timeslot_id = day_response.json()["timeslot_ids"][0]
    groups = client.get("/api/v1/groups", headers=headers).json()
    selected_group = next(item for item in groups if item["status"] == "PENDING_D11" and item["leader_count"] == 1)
    rooms = client.get("/api/v1/rooms", headers=headers).json()["data"]
    client.post(
        f"/api/v1/rounds/{round_id}/resources",
        json={"group_ids": [selected_group["id"]], "timeslot_ids": [timeslot_id], "room_ids": [rooms[0]["id"]]},
        headers=headers,
    )
    for lecturer in client.get("/api/v1/lecturers", headers=headers).json()["data"][:6]:
        response = client.post(
            f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
            json={"selected_timeslot_ids": [timeslot_id]},
            headers=headers,
        )
        assert response.status_code == 200
    run = client.post(
        f"/api/v1/rounds/{round_id}/schedule/run",
        json={"random_seed": 11, "time_limit_seconds": 2},
        headers=headers,
    )
    assert run.status_code == 201, run.text
    version_id = run.json()["version_id"]
    detail = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers)
    assert detail.status_code == 200
    session = detail.json()["sessions"][0]
    edit = client.post(
        f"/api/v1/schedule/versions/{version_id}/sessions/{session['id']}/edit",
        json={"timeslot_id": timeslot_id, "room_id": rooms[0]["id"], "reviewer_ids": session["reviewer_ids"], "reason": "Room confirmation"},
        headers=headers,
    )
    assert edit.status_code == 200, edit.text
    assert client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=headers).status_code == 200
    published = client.post(f"/api/v1/rounds/{round_id}/schedule/publish/{version_id}", headers=headers)
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "PUBLISHED"


@pytest.mark.integration
def test_controlled_change_creates_a_new_version_without_rewriting_source(client):
    headers = {"X-Test-Session": "active-manager"}
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    semester_id = next(item["id"] for item in client.get("/api/v1/semesters", headers=headers).json()["data"] if item["code"] == "SE-2026-2027")
    round_id = client.post("/api/v1/rounds", json={"semester_id": semester_id, "type": "DEFENSE_1_1", "reviewer_count": 3, "room_types": ["NORMAL"], "session_duration_minutes": 30}, headers=headers).json()["id"]
    day = client.post(f"/api/v1/rounds/{round_id}/days", json={"day_date": "2033-03-01", "slots": [{"start_at": "2033-03-01T09:00:00+07:00", "end_at": "2033-03-01T09:30:00+07:00"}]}, headers=headers).json()
    group = next(item for item in client.get("/api/v1/groups", headers=headers).json() if item["status"] == "PENDING_D11" and item["leader_count"] == 1)
    room = client.get("/api/v1/rooms", headers=headers).json()["data"][0]
    client.post(f"/api/v1/rounds/{round_id}/resources", json={"group_ids": [group["id"]], "timeslot_ids": [day["timeslot_ids"][0]], "room_ids": [room["id"]]}, headers=headers)
    for lecturer in client.get("/api/v1/lecturers", headers=headers).json()["data"][:6]:
        client.post(f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability", json={"selected_timeslot_ids": day["timeslot_ids"]}, headers=headers)
    original = client.post(f"/api/v1/rounds/{round_id}/schedule/run", json={"time_limit_seconds": 2}, headers=headers).json()
    version_id = original["version_id"]
    session = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers).json()["sessions"][0]
    assert client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=headers).status_code == 200
    assert client.post(f"/api/v1/rounds/{round_id}/schedule/publish/{version_id}", headers=headers).status_code == 200
    changed = client.post(f"/api/v1/schedule/versions/{version_id}/sessions/{session['id']}/controlled-change", json={"timeslot_id": session["timeslot_id"], "room_id": session["room_id"], "reviewer_ids": session["reviewer_ids"], "reason": "Operational confirmation"}, headers=headers)
    assert changed.status_code == 200, changed.text
    assert changed.json()["version_id"] != version_id
    source = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers).json()
    assert source["status"] == "PUBLISHED"
    assert source["sessions"][0]["reviewer_ids"] == session["reviewer_ids"]
