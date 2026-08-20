from uuid import uuid4

import pytest


@pytest.mark.integration
def test_manager_can_assign_supervisors_to_existing_target_project(client):
    client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    headers = {"X-Test-Session": "active-manager"}
    semester = next(
        item for item in client.get("/api/v1/semesters", headers=headers).json()["data"]
        if item["code"] == "SE-2026-2027"
    )
    lecturers = client.get("/api/v1/lecturers", headers=headers).json()["data"]
    assert lecturers
    main_id = lecturers[0]["id"]
    co_id = lecturers[1]["id"] if len(lecturers) > 1 else main_id

    created = client.post(
        f"/api/v1/semesters/{semester['id']}/projects",
        json={
            "code": f"P-SUP-{uuid4().hex[:8]}",
            "nameVi": "Supervisor assignment contract",
            "mainSupervisorId": f"lec_{main_id}",
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    project_id = created.json()["data"]["id"]

    updated = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"mainSupervisorId": f"lec_{co_id}"},
        headers=headers,
    )
    assert updated.status_code == 200, updated.text

    listed = client.get(f"/api/v1/semesters/{semester['id']}/projects", headers=headers)
    assert listed.status_code == 200, listed.text
    project = next(item for item in listed.json()["data"] if item["id"] == project_id)
    assert project["nameVi"] == "Supervisor assignment contract"
    assert project["mainSupervisor"]["id"] == f"lec_{co_id}"
    assert project["coSupervisor"] is None
