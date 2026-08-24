"""Phase 3 — the API accepts camelCase input without dropping the snake_case names.

Every request name has two spellings during the migration, so the frontend can
move one call site at a time.  These tests pin the whole inventory rather than a
sample: a query parameter that quietly loses one of its two spellings is exactly
the kind of break that only shows up in a half-migrated browser.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ConfigDict

from app.api_contract import RequestModel, dual_name_query
from app.main import create_app
from app.routes.master_data import GroupCreate, ProjectCreate, RoundCreate

MANAGER = {"X-Test-Session": "active-manager"}

# (path, camelName, legacyName, valueA, valueB) — the complete set of query
# parameters that were snake_case on the wire before this phase.
DUAL_QUERY_PARAMS = [
    ("/api/v1/semesters", "academicYear", "academic_year", "2026-2027", "2027-2028"),
    ("/api/v1/audit", "actorId", "actor_id", "1", "2"),
    ("/api/v1/audit", "entityType", "entity_type", "round", "session"),
    ("/api/v1/projects", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/groups", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/rounds", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/sessions", "roundId", "round_id", "1", "2"),
    ("/api/v1/sessions", "versionId", "version_id", "1", "2"),
    ("/api/v1/sessions", "statusFilter", "status_filter", "PLANNED", "DONE"),
    ("/api/v1/reschedule-requests", "statusFilter", "status_filter", "PENDING", "APPROVED"),
    ("/api/v1/reports/group-progress", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/results", "roundId", "round_id", "1", "2"),
    ("/api/v1/dashboard", "roundId", "round_id", "1", "2"),
    ("/api/v1/dashboard", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/reports/lecturer-load", "roundId", "round_id", "1", "2"),
    ("/api/v1/reports/lecturer-load", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/reports/unscheduled", "roundId", "round_id", "1", "2"),
    ("/api/v1/reports/quality", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/reports/remediation", "roundId", "round_id", "1", "2"),
    ("/api/v1/reports/remediation", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/reports/outcomes", "roundId", "round_id", "1", "2"),
    ("/api/v1/reports/outcomes", "semesterId", "semester_id", "1", "2"),
    ("/api/v1/my/schedule", "versionId", "version_id", "1", "2"),
    ("/api/v1/my/schedule", "fromAt", "from_at", "2026-01-01T00:00:00Z", "2026-02-01T00:00:00Z"),
    ("/api/v1/my/schedule", "toAt", "to_at", "2026-03-01T00:00:00Z", "2026-04-01T00:00:00Z"),
]

# The same two live on a route that never runs: `target_room_publish` registers
# `GET /rounds/{roundId}/rooms/available` first and wins, while `room_assignment`
# keeps supplying the documented signature.  They are exercised against their own
# router instead of through the shared app.
SHADOWED_QUERY_PARAMS = [
    ("/api/v1/rounds/1/rooms/available", "timeslotId", "timeslot_id", "1", "2"),
    ("/api/v1/rounds/1/rooms/available", "roomType", "room_type", "NORMAL", "LAB"),
]

PARAM_IDS = [f"{row[0]}:{row[1]}" for row in DUAL_QUERY_PARAMS]


def test_the_inventory_covers_every_parameter_that_was_snake_case():
    assert len(DUAL_QUERY_PARAMS) + len(SHADOWED_QUERY_PARAMS) == 27


@pytest.mark.parametrize(
    ("path", "camel", "legacy", "value_a", "value_b"), DUAL_QUERY_PARAMS, ids=PARAM_IDS
)
def test_both_spellings_reach_the_same_parameter(client, path, camel, legacy, value_a, value_b):
    """Disagreeing spellings are refused, which only one shared reader can do.

    A route that had dropped the legacy name would ignore it and answer normally.
    """

    response = client.get(f"{path}?{camel}={value_a}&{legacy}={value_b}", headers=MANAGER)

    assert response.status_code == 422, response.text
    body = response.json()
    assert body["error"]["code"] == "AMBIGUOUS_PARAM"
    assert body["error"]["details"] == {"param": camel, "legacyParam": legacy}


@pytest.mark.integration
@pytest.mark.parametrize(
    ("path", "camel", "legacy", "value_a", "value_b"), DUAL_QUERY_PARAMS, ids=PARAM_IDS
)
def test_agreeing_spellings_are_not_a_conflict(client, path, camel, legacy, value_a, value_b):
    response = client.get(f"{path}?{camel}={value_a}&{legacy}={value_a}", headers=MANAGER)

    assert response.status_code != 422, response.text


@pytest.mark.parametrize(
    ("path", "camel", "legacy", "value_a", "value_b"), SHADOWED_QUERY_PARAMS
)
def test_both_spellings_reach_the_same_parameter_on_the_shadowed_route(
    path, camel, legacy, value_a, value_b
):
    """`room_assignment` owns the documented signature, so test it where it runs."""

    from fastapi import FastAPI

    from app.routes.room_assignment import router

    isolated = FastAPI()
    isolated.include_router(router)
    response = TestClient(isolated).get(
        f"{path}?{camel}={value_a}&{legacy}={value_b}", headers=MANAGER
    )

    assert response.status_code == 422, response.text
    assert response.json()["detail"]["code"] == "AMBIGUOUS_PARAM"


def test_only_the_camel_spelling_is_published_in_the_schema():
    spec = create_app().openapi()

    for path, camel, legacy, _a, _b in DUAL_QUERY_PARAMS + SHADOWED_QUERY_PARAMS:
        template = path.replace("/1/", "/{roundId}/")
        published = {
            parameter["name"]
            for operation in spec["paths"][template].values()
            if isinstance(operation, dict)
            for parameter in operation.get("parameters", [])
        }
        assert camel in published, (template, camel)
        assert legacy not in published, (template, legacy)


def test_a_required_parameter_still_has_to_be_sent(client):
    response = client.get("/api/v1/reports/unscheduled", headers=MANAGER)

    assert response.status_code == 422
    assert response.json()["error"]["details"] == {"param": "roundId"}


def test_the_url_itself_is_unchanged_by_the_path_parameter_rename(client):
    """Renaming a path parameter is invisible to callers — the URL carries no names.

    A student is refused by the handler, which it can only reach if the router
    still matches the concrete URL and binds 999 to the renamed parameter; an
    unmatched URL never gets that far and answers 404 instead.
    """

    matched = client.get("/api/v1/semesters/999", headers={"X-Test-Session": "active-student"})
    unmatched = client.get("/api/v1/semesters/999/nope", headers={"X-Test-Session": "active-student"})

    assert matched.status_code == 403, matched.text
    assert unmatched.status_code == 404


@pytest.mark.parametrize(
    ("model", "camel_payload", "snake_payload"),
    [
        (
            ProjectCreate,
            {"semesterId": 1, "majorId": 2, "code": "P1", "title": "T", "supervisors": ["L1"]},
            {"semester_id": 1, "major_id": 2, "code": "P1", "title": "T", "supervisors": ["L1"]},
        ),
        (
            GroupCreate,
            {"projectId": 1, "code": "G1", "members": [{"studentCode": "S1", "role": "LEADER"}] * 4},
            {"project_id": 1, "code": "G1", "members": [{"student_code": "S1", "role": "LEADER"}] * 4},
        ),
    ],
)
def test_request_bodies_accept_either_spelling(model, camel_payload, snake_payload):
    assert model(**camel_payload) == model(**snake_payload)


def test_round_create_accepts_the_camel_spelling_of_every_snake_field():
    """POST /rounds used to mix both styles: snake fields beside timeframeId."""

    aliases = {field.alias for field in RoundCreate.model_fields.values()}

    assert "_" not in "".join(aliases)
    assert {"semesterId", "reviewerCount", "h12SessionsPerDay", "timeframeId"} <= aliases


def test_request_model_leaves_each_subclass_extra_setting_alone():
    class Strict(RequestModel):
        model_config = ConfigDict(extra="forbid")

        some_field: int = 0

    class Lenient(RequestModel):
        some_field: int = 0

    assert Lenient(someField=1, unknown="ignored").some_field == 1
    with pytest.raises(ValueError):
        Strict(someField=1, unknown="rejected")


def test_dual_name_query_resolves_values_and_falls_back_to_the_default():
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/probe")
    def probe(
        size: int = dual_name_query("pageSize", "page_size", int, default=20, ge=1, le=200),
        moment: datetime | None = dual_name_query("fromAt", "from_at", datetime),
    ) -> dict[str, object]:
        return {"size": size, "moment": moment}

    probe_client = TestClient(app)

    assert probe_client.get("/probe").json() == {"size": 20, "moment": None}
    assert probe_client.get("/probe?pageSize=50").json()["size"] == 50
    assert probe_client.get("/probe?page_size=50").json()["size"] == 50
    assert probe_client.get("/probe?fromAt=2026-01-01T00:00:00Z").json()["moment"] is not None
    assert probe_client.get("/probe?pageSize=0").status_code == 422
    assert probe_client.get("/probe?page_size=0").status_code == 422
