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
            "type": "REVIEW_3",
            "reviewer_count": 3,
            "room_types": ["NORMAL"],
            "session_duration_minutes": 30,
            "startDate": "2031-03-01",
            "endDate": "2031-03-01",
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
    timeslot_id = day_response.json()["timeslotIds"][0]
    groups = client.get("/api/v1/groups", headers=headers).json()
    selected_group = next(item for item in groups if item["status"] == "PENDING_D11" and item["leaderCount"] == 1)
    rooms = client.get("/api/v1/rooms", headers=headers).json()["data"]
    client.post(
        f"/api/v1/rounds/{round_id}/resources",
        json={"groupIds": [selected_group["id"]], "timeslotIds": [timeslot_id], "room_ids": [rooms[0]["id"]]},
        headers=headers,
    )
    for lecturer in client.get("/api/v1/lecturers", headers=headers).json()["data"][:6]:
        response = client.post(
            f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
            json={"selectedTimeslotIds": [timeslot_id]},
            headers=headers,
        )
        assert response.status_code == 200
    for target_status in ("OPEN_REGISTRATION", "REGISTRATION_CLOSED"):
        assert client.post(
            f"/api/v1/rounds/{round_id}/transition",
            json={"targetStatus": target_status},
            headers=headers,
        ).status_code == 200
    run = client.post(
        f"/api/v1/rounds/{round_id}/schedule/run",
        json={"randomSeed": 11, "timeLimitSeconds": 2},
        headers=headers,
    )
    assert run.status_code == 201, run.text
    version_id = run.json()["versionId"]
    assert client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=headers).status_code == 200
    detail = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers)
    assert detail.status_code == 200
    session = detail.json()["sessions"][0]
    assert client.put(
        f"/api/v1/sessions/{session['id']}/room",
        json={"roomId": rooms[0]["id"]},
        headers=headers,
    ).status_code == 200
    published = client.post(f"/api/v1/rounds/{round_id}/schedule/publish/{version_id}", headers=headers)
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "PUBLISHED"


@pytest.mark.integration
def test_controlled_change_creates_a_new_version_without_rewriting_source(client):
    headers = {"X-Test-Session": "active-manager"}
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    semester_id = next(item["id"] for item in client.get("/api/v1/semesters", headers=headers).json()["data"] if item["code"] == "SE-2026-2027")
    round_id = client.post("/api/v1/rounds", json={"semester_id": semester_id, "type": "REVIEW_3", "reviewer_count": 3, "room_types": ["NORMAL"], "session_duration_minutes": 30, "startDate": "2053-03-01", "endDate": "2053-03-01"}, headers=headers).json()["id"]
    day = client.post(f"/api/v1/rounds/{round_id}/days", json={"day_date": "2053-03-01", "slots": [{"start_at": "2053-03-01T09:00:00+07:00", "end_at": "2053-03-01T09:30:00+07:00"}]}, headers=headers).json()
    group = next(item for item in client.get("/api/v1/groups", headers=headers).json() if item["status"] == "PENDING_D11" and item["leaderCount"] == 1)
    room = client.get("/api/v1/rooms", headers=headers).json()["data"][0]
    client.post(f"/api/v1/rounds/{round_id}/resources", json={"groupIds": [group["id"]], "timeslotIds": [day["timeslotIds"][0]], "room_ids": [room["id"]]}, headers=headers)
    for lecturer in client.get("/api/v1/lecturers", headers=headers).json()["data"][:6]:
        client.post(f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability", json={"selectedTimeslotIds": day["timeslotIds"]}, headers=headers)
    for target_status in ("OPEN_REGISTRATION", "REGISTRATION_CLOSED"):
        assert client.post(f"/api/v1/rounds/{round_id}/transition", json={"targetStatus": target_status}, headers=headers).status_code == 200
    original = client.post(f"/api/v1/rounds/{round_id}/schedule/run", json={"timeLimitSeconds": 2}, headers=headers).json()
    version_id = original["versionId"]
    assert client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=headers).status_code == 200
    session = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers).json()["sessions"][0]
    assert client.put(f"/api/v1/sessions/{session['id']}/room", json={"roomId": room["id"]}, headers=headers).status_code == 200
    assert client.post(f"/api/v1/rounds/{round_id}/schedule/publish/{version_id}", headers=headers).status_code == 200
    changed = client.post(f"/api/v1/schedule/versions/{version_id}/sessions/{session['id']}/controlled-change", json={"timeslotId": session["timeslotId"], "roomId": client.get("/api/v1/rooms", headers=headers).json()["data"][1]["id"], "reviewerIds": session["reviewerIds"], "reason": "Operational confirmation"}, headers=headers)
    assert changed.status_code == 200, changed.text
    assert changed.json()["versionId"] != version_id
    source = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers).json()
    assert source["status"] == "DISCARDED"
    assert source["sessions"][0]["reviewerIds"] == session["reviewerIds"]
