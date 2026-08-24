import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import CHECKLIST_OPERATIONS
from app.config import get_settings
from app.database import get_engine


def test_committee_create_contract_declares_created_status():
    operation = next(
        item
        for item in CHECKLIST_OPERATIONS
        if item.method == "POST" and item.path == "/api/v1/committees"
    )
    assert operation.success_status == 201


@pytest.fixture()
def lecturer_ids():
    engine = get_engine(get_settings().database_url)
    ids: list[int] = []
    with Session(engine) as db, db.begin():
        for index in range(6):
            account_id = db.execute(
                text(
                    "INSERT INTO accounts (email, display_name, password_hash) "
                    "VALUES (:email, :name, 'x') RETURNING id"
                ),
                {"email": f"committee-test-lecturer-{index}@example.com", "name": f"Committee Test Lecturer {index}"},
            ).scalar_one()
            db.execute(
                text("INSERT INTO account_roles (account_id, role) VALUES (:account_id, 'LECTURER')"),
                {"account_id": account_id},
            )
            lecturer_id = db.execute(
                text(
                    "INSERT INTO lecturers (account_id, lecturer_code) VALUES (:account_id, :code) RETURNING id"
                ),
                {"account_id": account_id, "code": f"CMTTEST{index}"},
            ).scalar_one()
            ids.append(int(lecturer_id))
    yield ids
    with Session(engine) as db, db.begin():
        account_ids = db.execute(
            text("SELECT account_id FROM lecturers WHERE id = ANY(:ids)"), {"ids": ids}
        ).scalars().all()
        db.execute(text("DELETE FROM committee_members WHERE lecturer_id = ANY(:ids)"), {"ids": ids})
        db.execute(text("DELETE FROM lecturers WHERE id = ANY(:ids)"), {"ids": ids})
        db.execute(text("DELETE FROM account_roles WHERE account_id = ANY(:ids)"), {"ids": account_ids})
        db.execute(text("DELETE FROM accounts WHERE id = ANY(:ids)"), {"ids": account_ids})


@pytest.mark.integration
def test_committee_preview_requires_manager(client, lecturer_ids):
    payload = {"groups": [{"code": "CMT-TEST-01", "memberIds": lecturer_ids[:3]}]}
    forbidden = client.post(
        "/api/v1/committees/preview",
        headers={"X-Test-Session": "active-lecturer"},
        json=payload,
    )
    assert forbidden.status_code == 403


@pytest.mark.integration
def test_committee_preview_labels_reviewer_only_group(client, lecturer_ids):
    payload = {"groups": [{"code": "CMT-TEST-REVIEWER", "memberIds": lecturer_ids[:3]}]}
    response = client.post(
        "/api/v1/committees/preview",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )
    assert response.status_code == 200, response.text
    group = response.json()["data"]["groups"][0]
    assert group["ok"] is True
    assert [member["role"] for member in group["members"]] == ["REVIEWER", "REVIEWER", "REVIEWER"]
    assert [member["roleLabel"] for member in group["members"]] == ["Reviewer 1", "Reviewer 2", "Reviewer 3"]


@pytest.mark.integration
def test_committee_preview_labels_chair_secretary_member_group(client, lecturer_ids):
    payload = {"groups": [{"code": "CMT-TEST-DEFENSE", "memberIds": lecturer_ids[:5]}]}
    response = client.post(
        "/api/v1/committees/preview",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )
    assert response.status_code == 200, response.text
    group = response.json()["data"]["groups"][0]
    assert group["ok"] is True
    assert [member["role"] for member in group["members"]] == ["CHAIR", "SECRETARY", "MEMBER", "MEMBER", "MEMBER"]
    assert [member["roleLabel"] for member in group["members"]] == [
        "Chủ tịch",
        "Thư ký",
        "Thành viên 1",
        "Thành viên 2",
        "Thành viên 3",
    ]


@pytest.mark.integration
def test_committee_preview_reports_duplicate_member_error(client, lecturer_ids):
    payload = {"groups": [{"code": "CMT-TEST-DUP", "memberIds": [lecturer_ids[0], lecturer_ids[0]]}]}
    response = client.post(
        "/api/v1/committees/preview",
        headers={"X-Test-Session": "active-manager"},
        json=payload,
    )
    assert response.status_code == 200, response.text
    group = response.json()["data"]["groups"][0]
    assert group["ok"] is False
    assert group["errors"][0]["code"] == "COMMITTEE_MEMBER_DUPLICATE"


@pytest.mark.integration
def test_committee_bulk_create_partial_success_then_list_get_delete(client, lecturer_ids):
    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM committees WHERE code IN ('CMT-TEST-OK', 'CMT-TEST-BAD')"))

    payload = {
        "groups": [
            {"code": "CMT-TEST-OK", "memberIds": lecturer_ids[:3]},
            {"code": "CMT-TEST-BAD", "memberIds": [lecturer_ids[0], lecturer_ids[0]]},
        ]
    }
    headers = {"X-Test-Session": "active-manager"}
    created = client.post("/api/v1/committees", headers=headers, json=payload)
    assert created.status_code == 201, created.text
    body = created.json()["data"]
    assert body["created"] == 1
    assert body["skipped"] == 1
    assert body["errors"][0]["code"] == "COMMITTEE_MEMBER_DUPLICATE"
    committee_id = body["committees"][0]["id"]

    try:
        listed = client.get(
            f"/api/v1/committees?lecturerId=lec_{lecturer_ids[0]}",
            headers=headers,
        )
        assert listed.status_code == 200, listed.text
        assert any(item["id"] == committee_id for item in listed.json()["data"])

        detail = client.get(f"/api/v1/committees/cmt_{committee_id}", headers=headers)
        assert detail.status_code == 200, detail.text
        assert detail.json()["data"]["code"] == "CMT-TEST-OK"
        assert len(detail.json()["data"]["members"]) == 3
    finally:
        removed = client.request("DELETE", f"/api/v1/committees/cmt_{committee_id}", headers=headers)
        assert removed.status_code == 200, removed.text

    missing = client.get(f"/api/v1/committees/cmt_{committee_id}", headers=headers)
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "COMMITTEE_NOT_FOUND"


@pytest.mark.integration
def test_committee_bulk_delete(client, lecturer_ids):
    headers = {"X-Test-Session": "active-manager"}
    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM committees WHERE code IN ('CMT-TEST-BULK-1', 'CMT-TEST-BULK-2')"))

    payload = {
        "groups": [
            {"code": "CMT-TEST-BULK-1", "memberIds": lecturer_ids[:3]},
            {"code": "CMT-TEST-BULK-2", "memberIds": lecturer_ids[3:6]},
        ]
    }
    created = client.post("/api/v1/committees", headers=headers, json=payload)
    assert created.status_code == 201, created.text
    ids = [item["id"] for item in created.json()["data"]["committees"]]

    response = client.post(
        "/api/v1/committees/bulk-delete",
        headers=headers,
        json={"committeeIds": [f"cmt_{value}" for value in ids]},
    )
    assert response.status_code == 200, response.text
    assert response.json()["data"]["deleted"] == 2
