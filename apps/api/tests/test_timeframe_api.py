import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import CHECKLIST_OPERATIONS
from app.config import get_settings
from app.database import get_engine


def _payload(*, start: str = "07:00:00", end: str = "17:30:00") -> dict[str, object]:
    return {
        "name": "Global Timeframe API Test",
        "type": "COUNCIL",
        "startTime": start,
        "endTime": end,
        "blockDurationMinutes": 135,
        "groupDurationMinutes": 45,
        "breakBetweenBlocksMinutes": 15,
        "breakWindows": [
            {
                "name": "Nghi trua",
                "startTime": "12:00:00",
                "endTime": "13:00:00",
            }
        ],
        "reason": "Test reusable system configuration",
    }


def _manual_payload() -> dict[str, object]:
    return {
        "name": "Global Manual Timeframe API Test",
        "type": "COUNCIL",
        "groupDurationMinutes": 45,
        "timelines": [
            {"startTime": "07:30:00", "endTime": "09:00:00", "groupsPerSlot": 2},
            {"startTime": "09:15:00", "endTime": "11:30:00", "groupsPerSlot": 3},
            {"startTime": "13:00:00", "endTime": "14:30:00", "groupsPerSlot": 2},
        ],
        "reason": "Save timelines edited from quick preview",
    }


def test_timeframe_create_contract_declares_created_status():
    operation = next(
        item
        for item in CHECKLIST_OPERATIONS
        if item.method == "POST" and item.path == "/api/v1/timeframes"
    )

    assert operation.success_status == 201

    manual_operation = next(
        item
        for item in CHECKLIST_OPERATIONS
        if item.method == "POST" and item.path == "/api/v1/timeframes/manual"
    )
    assert manual_operation.success_status == 201


def test_timeframe_preview_is_global_and_read_only(client):
    forbidden = client.post(
        "/api/v1/timeframes/preview",
        headers={"X-Test-Session": "active-lecturer"},
        json=_payload(),
    )
    assert forbidden.status_code == 403

    preview = client.post(
        "/api/v1/timeframes/preview",
        headers={"X-Test-Session": "active-manager"},
        json=_payload(),
    )
    assert preview.status_code == 200, preview.text
    data = preview.json()["data"]
    assert data["blocksPerDay"] == 3
    assert data["groupsPerBlock"] == 3
    assert data["capacityPerDay"] == 9
    assert data["breakBetweenBlocksMinutes"] == 15
    assert data["breakWindows"][0]["name"] == "Nghi trua"


def test_timeframe_preview_rejects_timezone_offsets(client):
    payload = _payload()
    payload["startTime"] = "07:00:00+07:00"
    payload["endTime"] = "17:30:00+07:00"

    response = client.post(
        "/api/v1/timeframes/preview",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "TIMEFRAME_TIMEZONE_NOT_ALLOWED"


def test_manual_timeframe_rejects_mismatched_timeline_duration(client):
    payload = _manual_payload()
    payload["timelines"][0]["endTime"] = "08:30:00"

    response = client.post(
        "/api/v1/timeframes/manual",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "MANUAL_TIMELINE_DURATION_MISMATCH"


def test_manual_timeframe_returns_stable_domain_errors_for_empty_or_invalid_counts(client):
    payload = _manual_payload()
    payload["timelines"] = []
    empty = client.post(
        "/api/v1/timeframes/manual/preview",
        headers={"X-Test-Session": "active-manager"},
        json={
            "groupDurationMinutes": payload["groupDurationMinutes"],
            "timelines": payload["timelines"],
        },
    )
    assert empty.status_code == 422
    assert empty.json()["error"]["code"] == "MANUAL_TIMELINE_REQUIRED"

    payload = _manual_payload()
    payload["timelines"][0]["groupsPerSlot"] = 0
    invalid_count = client.post(
        "/api/v1/timeframes/manual",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )
    assert invalid_count.status_code == 422
    assert invalid_count.json()["error"]["code"] == "MANUAL_TIMELINE_GROUP_COUNT_INVALID"


def test_manual_preview_recalculates_metrics_after_timeline_edits(client):
    payload = _manual_payload()
    payload.pop("name")
    payload.pop("type")
    payload.pop("reason")

    response = client.post(
        "/api/v1/timeframes/manual/preview",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )

    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["startTime"] == "07:30:00"
    assert data["endTime"] == "14:30:00"
    assert data["blocksPerDay"] == 3
    assert data["capacityPerDay"] == 7
    assert data["totalBreakMinutes"] == 105
    assert data["manualTimelines"] == payload["timelines"]


@pytest.mark.integration
def test_manual_timeframe_create_and_update_preserve_edited_timeline_revisions(client):
    headers = {"X-Test-Session": "active-manager"}
    engine = get_engine(get_settings().database_url)
    timeframe_id: int | None = None

    with Session(engine) as db, db.begin():
        db.execute(
            text("DELETE FROM timeframes WHERE name = :name"),
            {"name": _manual_payload()["name"]},
        )

    try:
        created = client.post(
            "/api/v1/timeframes/manual",
            headers=headers,
            json=_manual_payload(),
        )
        assert created.status_code == 201, created.text
        data = created.json()["data"]
        timeframe_id = int(data["id"])
        assert data["startTime"] == "07:30:00"
        assert data["endTime"] == "14:30:00"
        assert data["blocksPerDay"] == 3
        assert data["capacityPerDay"] == 7
        assert data["blockDurationMinutes"] is None
        assert data["groupsPerBlock"] is None
        assert data["breakBetweenBlocksMinutes"] is None
        assert data["totalBreakMinutes"] == 105
        assert [len(block["groupSlots"]) for block in data["blocks"]] == [2, 3, 2]
        assert len(data["revisions"][0]["manualTimelines"]) == 3

        update_payload = _manual_payload()
        update_payload["timelines"] = [
            {"startTime": "08:00:00", "endTime": "10:15:00", "groupsPerSlot": 3},
            {"startTime": "13:00:00", "endTime": "14:30:00", "groupsPerSlot": 2},
        ]
        update_payload["reason"] = "Replace all edited timelines"
        updated = client.patch(
            f"/api/v1/timeframes/{timeframe_id}/manual",
            headers=headers,
            json=update_payload,
        )
        assert updated.status_code == 200, updated.text
        updated_data = updated.json()["data"]
        assert updated_data["version"]["number"] == 2
        assert updated_data["capacityPerDay"] == 5
        assert len(updated_data["blocks"]) == 2
        assert len(updated_data["revisions"][0]["manualTimelines"]) == 2
        assert len(updated_data["revisions"][1]["manualTimelines"]) == 3
    finally:
        if timeframe_id is not None:
            with Session(engine) as db, db.begin():
                db.execute(text("DELETE FROM timeframes WHERE id = :id"), {"id": timeframe_id})


@pytest.mark.integration
def test_global_timeframe_crud_creates_revisions_without_touching_round_slots(client):
    headers = {"X-Test-Session": "active-manager"}
    engine = get_engine(get_settings().database_url)
    timeframe_id: int | None = None

    with Session(engine) as db, db.begin():
        db.execute(
            text("DELETE FROM timeframes WHERE name = :name"),
            {"name": _payload()["name"]},
        )
        protected_counts_before = {
            table: int(db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())
            for table in ("rounds", "timeslots", "scheduler_jobs")
        }

    try:
        created = client.post("/api/v1/timeframes", headers=headers, json=_payload())
        assert created.status_code == 201, created.text
        created_data = created.json()["data"]
        timeframe_id = int(created_data["id"])
        assert created_data["version"]["number"] == 1
        assert created_data["blocksPerDay"] == 3
        assert created_data["capacityPerDay"] == 9
        assert created_data["breakBetweenBlocksMinutes"] == 15
        assert created_data["breakWindows"][0]["name"] == "Nghi trua"
        assert "roundId" not in created_data

        listed = client.get("/api/v1/timeframes", headers=headers)
        assert listed.status_code == 200, listed.text
        assert any(item["id"] == timeframe_id for item in listed.json()["data"])

        updated_payload = _payload(start="08:00:00", end="17:00:00")
        updated_payload["breakBetweenBlocksMinutes"] = 0
        updated_payload["breakWindows"] = [
            {
                "name": "Nghi trua moi",
                "startTime": "12:30:00",
                "endTime": "13:15:00",
            }
        ]
        updated_payload["reason"] = "Move the shared template to 08:00"
        updated = client.patch(
            f"/api/v1/timeframes/{timeframe_id}",
            headers=headers,
            json=updated_payload,
        )
        assert updated.status_code == 200, updated.text
        updated_data = updated.json()["data"]
        assert updated_data["version"]["number"] == 2
        assert updated_data["breakBetweenBlocksMinutes"] == 0
        assert updated_data["breakWindows"][0]["name"] == "Nghi trua moi"
        assert [revision["status"] for revision in updated_data["revisions"]] == [
            "ACTIVE",
            "SUPERSEDED",
        ]
        active_revision, superseded_revision = updated_data["revisions"]
        assert active_revision["breakBetweenBlocksMinutes"] == 0
        assert active_revision["breakWindows"][0]["name"] == "Nghi trua moi"
        assert superseded_revision["breakBetweenBlocksMinutes"] == 15
        assert superseded_revision["breakWindows"][0]["name"] == "Nghi trua"

        archived = client.request(
            "DELETE",
            f"/api/v1/timeframes/{timeframe_id}",
            headers=headers,
            json={"reason": "Archive test template"},
        )
        assert archived.status_code == 200, archived.text
        assert archived.json()["data"]["archivedAt"] is not None

        active_list = client.get("/api/v1/timeframes", headers=headers).json()["data"]
        assert all(item["id"] != timeframe_id for item in active_list)
        full_list = client.get(
            "/api/v1/timeframes?includeArchived=true",
            headers=headers,
        ).json()["data"]
        assert any(item["id"] == timeframe_id for item in full_list)

        with Session(engine) as db:
            protected_counts_after = {
                table: int(db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())
                for table in ("rounds", "timeslots", "scheduler_jobs")
            }
        assert protected_counts_after == protected_counts_before
    finally:
        if timeframe_id is not None:
            with Session(engine) as db, db.begin():
                db.execute(text("DELETE FROM timeframes WHERE id = :id"), {"id": timeframe_id})


@pytest.mark.integration
def test_round_creation_materializes_and_pins_quick_timeframe_revision(client):
    headers = {"X-Test-Session": "active-manager"}
    engine = get_engine(get_settings().database_url)
    timeframe_id: int | None = None
    round_id: int | None = None

    with Session(engine) as db:
        semester_id = db.execute(
            text("SELECT id FROM semesters WHERE status = 'ACTIVE' ORDER BY id LIMIT 1")
        ).scalar_one()

    try:
        created_timeframe = client.post(
            "/api/v1/timeframes",
            headers=headers,
            json={**_payload(), "name": "Round Binding Quick Timeframe"},
        )
        assert created_timeframe.status_code == 201, created_timeframe.text
        timeframe_id = int(created_timeframe.json()["data"]["id"])
        active_version_id = int(created_timeframe.json()["data"]["version"]["id"])

        created_round = client.post(
            "/api/v1/rounds",
            headers=headers,
            json={
                "semester_id": semester_id,
                "name": "Round From Quick Timeframe",
                "type": "REVIEW_1",
                "reviewer_count": 2,
                "start_date": "2026-09-01",
                "end_date": "2026-09-01",
                "session_duration_minutes": 45,
                "max_groups_per_timeslot": 1,
                "room_types": ["NORMAL"],
                "timeframeId": timeframe_id,
            },
        )
        assert created_round.status_code == 201, created_round.text
        round_data = created_round.json()
        round_id = int(round_data["id"])
        assert round_data["timeframe_id"] == timeframe_id
        assert round_data["timeframe_version_id"] == active_version_id

        with Session(engine) as db:
            slots_before = db.execute(
                text(
                    "SELECT ts.start_at, ts.end_at FROM timeslots ts "
                    "JOIN round_days rd ON rd.id = ts.round_day_id "
                    "WHERE rd.round_id = :round_id ORDER BY ts.start_at"
                ),
                {"round_id": round_id},
            ).all()
        assert len(slots_before) == 9

        changed_round = client.patch(
            f"/api/v1/rounds/{round_id}",
            headers=headers,
            json={"startDate": "2026-09-03", "endDate": "2026-09-03"},
        )
        assert changed_round.status_code == 200, changed_round.text
        assert changed_round.json()["data"]["timeframeId"] == str(timeframe_id)
        assert changed_round.json()["data"]["timeframeVersionId"] == str(active_version_id)

        with Session(engine) as db:
            slots_before = db.execute(
                text(
                    "SELECT ts.start_at, ts.end_at FROM timeslots ts "
                    "JOIN round_days rd ON rd.id = ts.round_day_id "
                    "WHERE rd.round_id = :round_id ORDER BY ts.start_at"
                ),
                {"round_id": round_id},
            ).all()
        assert len(slots_before) == 9

        changed_payload = _payload(start="08:00:00", end="17:00:00")
        changed_payload["name"] = "Round Binding Quick Timeframe"
        changed_payload["breakBetweenBlocksMinutes"] = 0
        changed_payload["breakWindows"] = []
        changed = client.patch(
            f"/api/v1/timeframes/{timeframe_id}",
            headers=headers,
            json=changed_payload,
        )
        assert changed.status_code == 200, changed.text
        assert int(changed.json()["data"]["version"]["id"]) != active_version_id

        with Session(engine) as db:
            slots_after = db.execute(
                text(
                    "SELECT ts.start_at, ts.end_at FROM timeslots ts "
                    "JOIN round_days rd ON rd.id = ts.round_day_id "
                    "WHERE rd.round_id = :round_id ORDER BY ts.start_at"
                ),
                {"round_id": round_id},
            ).all()
        assert slots_after == slots_before
    finally:
        with Session(engine) as db, db.begin():
            if round_id is not None:
                db.execute(text("DELETE FROM rounds WHERE id = :id"), {"id": round_id})
            if timeframe_id is not None:
                db.execute(text("DELETE FROM timeframes WHERE id = :id"), {"id": timeframe_id})


@pytest.mark.integration
def test_round_creation_materializes_manual_timeframe_group_slots(client):
    headers = {"X-Test-Session": "active-manager"}
    engine = get_engine(get_settings().database_url)
    timeframe_id: int | None = None
    round_id: int | None = None

    with Session(engine) as db:
        semester_id = db.execute(
            text("SELECT id FROM semesters WHERE status = 'ACTIVE' ORDER BY id LIMIT 1")
        ).scalar_one()

    try:
        created_timeframe = client.post(
            "/api/v1/timeframes/manual",
            headers=headers,
            json={**_manual_payload(), "name": "Round Binding Manual Timeframe"},
        )
        assert created_timeframe.status_code == 201, created_timeframe.text
        timeframe_data = created_timeframe.json()["data"]
        timeframe_id = int(timeframe_data["id"])

        created_round = client.post(
            "/api/v1/rounds",
            headers=headers,
            json={
                "semester_id": semester_id,
                "name": "Round From Manual Timeframe",
                "type": "REVIEW_1",
                "reviewer_count": 2,
                "start_date": "2026-09-02",
                "end_date": "2026-09-02",
                "session_duration_minutes": 45,
                "max_groups_per_timeslot": 1,
                "room_types": ["NORMAL"],
                "timeframeId": timeframe_id,
            },
        )
        assert created_round.status_code == 201, created_round.text
        round_id = int(created_round.json()["id"])

        with Session(engine) as db:
            count = db.execute(
                text(
                    "SELECT COUNT(*) FROM timeslots ts "
                    "JOIN round_days rd ON rd.id = ts.round_day_id "
                    "WHERE rd.round_id = :round_id"
                ),
                {"round_id": round_id},
            ).scalar_one()
        assert count == 7
    finally:
        with Session(engine) as db, db.begin():
            if round_id is not None:
                db.execute(text("DELETE FROM rounds WHERE id = :id"), {"id": round_id})
            if timeframe_id is not None:
                db.execute(text("DELETE FROM timeframes WHERE id = :id"), {"id": timeframe_id})
