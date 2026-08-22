import pytest
from fastapi import HTTPException

from app.auth import CurrentUser
from app.routes import results


def test_group_absent_is_not_a_result_writable_session(monkeypatch):
    """A terminal GROUP_ABSENT session must be rejected before any result write."""

    monkeypatch.setattr(
        results,
        "_session_context",
        lambda db, session_id: {
            "id": session_id,
            "group_id": 10,
            "session_status": "GROUP_ABSENT",
            "group_status": "PENDING_D11",
            "version_id": 20,
            "round_id": 30,
            "type": "REVIEW_3",
            "result_owner_mode": False,
            "reviewer_ids": set(),
            "owner_ids": set(),
            "result": None,
        },
    )
    monkeypatch.setattr(results, "_can_write", lambda db, user, context: True)

    with pytest.raises(HTTPException) as exc_info:
        results.record_result(
            99,
            results.ResultPayload(outcome="COMPLETED"),
            object(),
            CurrentUser(role="MANAGER"),
        )

    assert exc_info.value.status_code in {409, 422}


def test_group_absent_requires_authentication(client):
    response = client.post(
        "/api/v1/sessions/1/group-absent",
        json={"reason": "Group did not attend"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("role", ["active-lecturer", "active-student"])
def test_group_absent_is_manager_or_admin_only(client, role):
    response = client.post(
        "/api/v1/sessions/1/group-absent",
        json={"reason": "Group did not attend"},
        headers={"X-Test-Session": role},
    )

    assert response.status_code == 403


def test_group_absent_reason_is_required(client):
    response = client.post(
        "/api/v1/sessions/1/group-absent",
        json={"reason": ""},
        headers={"X-Test-Session": "active-manager"},
    )

    assert response.status_code == 422
