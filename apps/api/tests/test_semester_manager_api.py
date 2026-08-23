from uuid import uuid4

import pytest

MANAGER_HEADERS = {"X-Test-Session": "active-manager"}


@pytest.mark.integration
def test_semester_list_detail_and_filters_expose_complete_contract(client):
    rows = client.get("/api/v1/semesters", headers=MANAGER_HEADERS)
    assert rows.status_code == 200
    body = rows.json()
    assert body["data"]
    assert body["meta"]["page"] == 1
    assert body["meta"]["total"] >= len(body["data"])
    item = body["data"][0]
    assert {
        "id",
        "code",
        "name",
        "note",
        "startDate",
        "endDate",
        "academicYear",
        "status",
        "projectCount",
        "groupCount",
        "roundCount",
        "createdAt",
        "createdBy",
        "updatedAt",
        "updatedBy",
    } <= item.keys()

    detail = client.get(f"/api/v1/semesters/{item['id']}", headers=MANAGER_HEADERS)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["id"] == item["id"]
    assert detail_body["code"] == item["code"]
    assert detail_body["status"] == item["status"]
    assert detail_body["academic_year"] == item["academicYear"]

    filtered = client.get(
        "/api/v1/semesters",
        params={"status": item["status"], "academic_year": item["academicYear"]},
        headers=MANAGER_HEADERS,
    )
    assert filtered.status_code == 200
    assert all(row["status"] == item["status"] for row in filtered.json()["data"])
    assert all(row["academicYear"] == item["academicYear"] for row in filtered.json()["data"])


@pytest.mark.integration
def test_semester_create_patch_and_set_current_are_atomic(client):
    before = client.get("/api/v1/semesters", headers=MANAGER_HEADERS).json()["data"]
    original_active = next(row for row in before if row["status"] == "ACTIVE")
    code = f"FAST-{uuid4().hex[:8]}"
    payload = {
        "code": code,
        "name": "Fast Track Semester",
        "note": "Created by API test",
        "start_date": "2036-01-01",
        "end_date": "2036-04-15",
    }

    close = client.post(
        f"/api/v1/semesters/{original_active['id']}/transition",
        json={"target_status": "CLOSED", "reason": "Prepare API test"},
        headers=MANAGER_HEADERS,
    )
    assert close.status_code == 200

    created = client.post("/api/v1/semesters", json=payload, headers=MANAGER_HEADERS)
    assert created.status_code == 201
    created_body = created.json()
    assert created_body["status"] == "ACTIVE"
    assert created_body["academic_year"] == "2036-2037"
    assert created_body["note"] == payload["note"]
    assert created_body["created_by"]["email"]

    duplicate_active = client.post(
        "/api/v1/semesters",
        json={**payload, "code": f"FAST-OTHER-{uuid4().hex[:8]}"},
        headers=MANAGER_HEADERS,
    )
    assert duplicate_active.status_code == 409
    assert duplicate_active.json()["error"]["code"] == "ACTIVE_SEMESTER_EXISTS"

    patched = client.patch(
        f"/api/v1/semesters/{created_body['id']}",
        json={"note": "Updated note"},
        headers=MANAGER_HEADERS,
    )
    assert patched.status_code == 200
    assert patched.json()["note"] == "Updated note"

    switched = client.post(
        f"/api/v1/semesters/{original_active['id']}/set-current",
        headers=MANAGER_HEADERS,
    )
    assert switched.status_code == 200
    assert switched.json()["id"] == original_active["id"]
    assert switched.json()["status"] == "ACTIVE"

    second_switch = client.post(
        f"/api/v1/semesters/{original_active['id']}/set-current",
        headers=MANAGER_HEADERS,
    )
    assert second_switch.status_code == 200
    assert second_switch.json()["status"] == "ACTIVE"
