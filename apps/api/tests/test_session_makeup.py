"""Spec §73 make-up session: authorization and payload validation.

Happy-path H-constraint / room / audit behavior needs a seeded round and
schedule, so it is covered separately as an ``integration`` test against
Docker PostgreSQL; this file only exercises the checks that run before any
database write, mirroring the group-absent tests in
``test_phase01_lifecycle.py``.
"""

import pytest


def test_makeup_requires_authentication(client):
    response = client.post(
        "/api/v1/sessions/1/makeup",
        json={"timeslot_id": 1, "reason": "Lecturer unavailable."},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("role", ["active-lecturer", "active-student"])
def test_makeup_is_manager_or_admin_only(client, role):
    response = client.post(
        "/api/v1/sessions/1/makeup",
        json={"timeslot_id": 1, "reason": "Lecturer unavailable."},
        headers={"X-Test-Session": role},
    )

    assert response.status_code == 403


def test_makeup_reason_is_required(client):
    response = client.post(
        "/api/v1/sessions/1/makeup",
        json={"timeslot_id": 1, "reason": ""},
        headers={"X-Test-Session": "active-manager"},
    )

    assert response.status_code == 422


def test_makeup_requires_timeslot_id(client):
    response = client.post(
        "/api/v1/sessions/1/makeup",
        json={"reason": "Lecturer unavailable."},
        headers={"X-Test-Session": "active-manager"},
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_makeup_target_session_not_found(client):
    response = client.post(
        "/api/v1/sessions/999999/makeup",
        json={"timeslot_id": 1, "reason": "Lecturer unavailable."},
        headers={"X-Test-Session": "active-manager"},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SESSION_NOT_FOUND"
