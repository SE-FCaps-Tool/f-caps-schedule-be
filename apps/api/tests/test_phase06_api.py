import pytest


@pytest.mark.integration
def test_manager_can_record_defense_result_and_advance_group(client):
    headers = {"X-Test-Session": "active-manager"}
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    semester_id = next(
        row["id"]
        for row in client.get("/api/v1/semesters", headers=headers).json()["data"]
        if row["code"] == "SE-2026-2027"
    )
    round_response = client.post(
        "/api/v1/rounds",
        json={"semester_id": semester_id, "type": "REVIEW_3", "reviewer_count": 3, "room_types": ["NORMAL"], "session_duration_minutes": 30},
        headers=headers,
    )
    assert round_response.status_code == 201
    round_id = round_response.json()["id"]
    day = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={"day_date": "2032-04-01", "slots": [{"start_at": "2032-04-01T09:00:00+07:00", "end_at": "2032-04-01T09:30:00+07:00"}]},
        headers=headers,
    )
    assert day.status_code == 201
    slot_id = day.json()["timeslot_ids"][0]
    group = next(item for item in client.get("/api/v1/groups", headers=headers).json() if item["status"] == "PENDING_D11" and item["leader_count"] == 1)
    room = client.get("/api/v1/rooms", headers=headers).json()["data"][1]
    assert client.post(f"/api/v1/rounds/{round_id}/resources", json={"group_ids": [group["id"]], "timeslot_ids": [slot_id], "room_ids": [room["id"]]}, headers=headers).status_code == 200
    for lecturer in client.get("/api/v1/lecturers", headers=headers).json()["data"][:6]:
        assert client.post(f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability", json={"selected_timeslot_ids": [slot_id]}, headers=headers).status_code == 200
    run = client.post(f"/api/v1/rounds/{round_id}/schedule/run", json={"time_limit_seconds": 2}, headers=headers)
    assert run.status_code == 201, run.text
    detail = client.get(f"/api/v1/schedule/versions/{run.json()['version_id']}", headers=headers)
    assert detail.status_code == 200
    session_id = detail.json()["sessions"][0]["id"]
    result = client.post(f"/api/v1/sessions/{session_id}/result", json={"outcome": "LEVEL_1", "note": "Pass to Defense 1"}, headers=headers)
    assert result.status_code == 201, result.text
    assert result.json()["group_status"] == "ELIGIBLE_D12"
