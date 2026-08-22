import pytest
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine
from app.services.committee_service import ROUND_COMMITTEE_FK, _is_round_committee_fk_violation

HEADERS = {"X-Test-Session": "active-manager"}
CODES = ("RCMT-A", "RCMT-B", "RCMT-SMALL")


class _Diag:
    def __init__(self, constraint_name: str | None) -> None:
        self.constraint_name = constraint_name


class _NamedForeignKeyViolation(ForeignKeyViolation):
    """psycopg's real ``diag`` is read-only, so name the constraint via a subclass."""

    def __init__(self, constraint_name: str | None) -> None:
        super().__init__("foreign key violation")
        self._constraint_name = constraint_name

    @property
    def diag(self) -> _Diag:
        return _Diag(self._constraint_name)


def _integrity_error(cause: Exception | None) -> IntegrityError:
    return IntegrityError("DELETE FROM committees", {}, cause)


def test_only_the_round_assignment_fk_counts_as_in_use():
    violation = _NamedForeignKeyViolation(ROUND_COMMITTEE_FK)
    assert _is_round_committee_fk_violation(_integrity_error(violation)) is True


@pytest.mark.parametrize(
    "cause",
    [
        UniqueViolation("duplicate key"),
        ValueError("not a database failure"),
        None,
    ],
)
def test_unrelated_integrity_failures_are_not_classified_as_in_use(cause):
    assert _is_round_committee_fk_violation(_integrity_error(cause)) is False


@pytest.mark.parametrize("constraint_name", ["fk_some_other_table", None])
def test_a_foreign_key_from_another_table_is_not_classified_as_in_use(constraint_name):
    violation = _NamedForeignKeyViolation(constraint_name)
    assert _is_round_committee_fk_violation(_integrity_error(violation)) is False


@pytest.fixture()
def lecturer_ids():
    engine = get_engine(get_settings().database_url)
    ids: list[int] = []
    with Session(engine) as db, db.begin():
        for index in range(5):
            account_id = db.execute(
                text(
                    "INSERT INTO accounts (email, display_name, password_hash) "
                    "VALUES (:email, :name, 'x') RETURNING id"
                ),
                {"email": f"round-cmt-lecturer-{index}@example.com", "name": f"Round Cmt Lecturer {index}"},
            ).scalar_one()
            db.execute(
                text("INSERT INTO account_roles (account_id, role) VALUES (:account_id, 'LECTURER')"),
                {"account_id": account_id},
            )
            lecturer_id = db.execute(
                text("INSERT INTO lecturers (account_id, lecturer_code) VALUES (:account_id, :code) RETURNING id"),
                {"account_id": account_id, "code": f"RCMTTEST{index}"},
            ).scalar_one()
            ids.append(int(lecturer_id))
    yield ids
    with Session(engine) as db, db.begin():
        account_ids = db.execute(
            text("SELECT account_id FROM lecturers WHERE id = ANY(:ids)"), {"ids": ids}
        ).scalars().all()
        db.execute(text("DELETE FROM lecturers WHERE id = ANY(:ids)"), {"ids": ids})
        db.execute(text("DELETE FROM account_roles WHERE account_id = ANY(:ids)"), {"ids": list(account_ids)})
        db.execute(text("DELETE FROM accounts WHERE id = ANY(:ids)"), {"ids": list(account_ids)})


@pytest.fixture()
def round_id():
    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        semester_id = db.execute(text("SELECT MIN(id) FROM semesters")).scalar_one()
        new_id = db.execute(
            text(
                "INSERT INTO rounds "
                "(semester_id, name, type, status, session_duration_minutes, reviewer_count) "
                "VALUES (:semester_id, 'Round Committee Test', CAST('REVIEW_1' AS round_type), "
                "CAST('DRAFT' AS round_status), 60, 2) RETURNING id"
            ),
            {"semester_id": semester_id},
        ).scalar_one()
    yield int(new_id)
    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM rounds WHERE id = :id"), {"id": new_id})


@pytest.fixture()
def committee_ids(client, lecturer_ids):
    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM committees WHERE code = ANY(:codes)"), {"codes": list(CODES)})
    created = client.post(
        "/api/v1/committees",
        headers=HEADERS,
        json={
            "groups": [
                {"code": "RCMT-A", "memberIds": lecturer_ids[:2]},
                {"code": "RCMT-B", "memberIds": lecturer_ids[2:4]},
                {"code": "RCMT-SMALL", "memberIds": lecturer_ids[4:5]},
            ]
        },
    )
    assert created.status_code == 201, created.text
    by_code = {item["code"]: int(item["id"]) for item in created.json()["data"]["committees"]}
    yield by_code
    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM round_committees WHERE committee_id = ANY(:ids)"), {"ids": list(by_code.values())})
        db.execute(text("DELETE FROM committees WHERE id = ANY(:ids)"), {"ids": list(by_code.values())})


@pytest.mark.integration
def test_replace_and_list_round_committees(client, round_id, committee_ids):
    response = client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-A']}", f"cmt_{committee_ids['RCMT-B']}"]},
    )
    assert response.status_code == 200, response.text
    assert {item["code"] for item in response.json()["data"]} == {"RCMT-A", "RCMT-B"}

    listed = client.get(f"/api/v1/rounds/{round_id}/committees", headers=HEADERS)
    assert listed.status_code == 200, listed.text
    assert {item["code"] for item in listed.json()["data"]} == {"RCMT-A", "RCMT-B"}

    detail = client.get(f"/api/v1/rounds/{round_id}", headers=HEADERS)
    assert detail.status_code == 200, detail.text
    assert detail.json()["data"]["committeeCount"] == 2


@pytest.mark.integration
def test_replace_with_empty_list_clears_assignments(client, round_id, committee_ids):
    client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-A']}"]},
    )
    cleared = client.put(f"/api/v1/rounds/{round_id}/committees", headers=HEADERS, json={"committeeIds": []})
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["data"] == []

    detail = client.get(f"/api/v1/rounds/{round_id}", headers=HEADERS)
    assert detail.json()["data"]["committeeCount"] == 0


@pytest.mark.integration
def test_size_mismatch_is_rejected(client, round_id, committee_ids):
    response = client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-SMALL']}"]},
    )
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "ROUND_COMMITTEE_SIZE_MISMATCH"


@pytest.mark.integration
def test_duplicate_committee_ids_are_rejected(client, round_id, committee_ids):
    duplicate = f"cmt_{committee_ids['RCMT-A']}"
    response = client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [duplicate, duplicate]},
    )
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "ROUND_COMMITTEE_DUPLICATE_ID"


@pytest.mark.integration
def test_unknown_committee_is_rejected(client, round_id):
    response = client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": ["cmt_99999999"]},
    )
    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "COMMITTEE_NOT_FOUND"


@pytest.mark.integration
def test_locked_round_rejects_assignment(client, round_id, committee_ids):
    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        db.execute(
            text("UPDATE rounds SET status = CAST('SCHEDULED' AS round_status) WHERE id = :id"),
            {"id": round_id},
        )
    response = client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-A']}"]},
    )
    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "ROUND_CONFIG_LOCKED"


@pytest.mark.integration
def test_student_cannot_assign_committees(client, round_id, committee_ids):
    response = client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers={"X-Test-Session": "active-student"},
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-A']}"]},
    )
    assert response.status_code == 403, response.text


@pytest.mark.integration
def test_round_input_only_keeps_committees_whose_members_are_all_eligible(
    client, round_id, committee_ids, lecturer_ids
):
    from app.routes.schedule_operations import _round_input

    client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-A']}"]},
    )
    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        day_id = db.execute(
            text("INSERT INTO round_days (round_id, day_date) VALUES (:id, DATE '2030-03-01') RETURNING id"),
            {"id": round_id},
        ).scalar_one()
        slot_id = db.execute(
            text(
                "INSERT INTO timeslots (round_day_id, start_at, end_at, active) "
                "VALUES (:day_id, CAST('2030-03-01T01:00:00Z' AS timestamptz), "
                "CAST('2030-03-01T02:00:00Z' AS timestamptz), TRUE) RETURNING id"
            ),
            {"day_id": day_id},
        ).scalar_one()

    members = tuple(sorted(lecturer_ids[:2]))

    with Session(engine) as db:
        context, _, _, reviewers = _round_input(db, round_id)
    assert context.has_assigned_committees is True
    assert context.committee_reviewer_sets == ()
    assert reviewers == []

    # One member eligible is still not enough: the Committee is all-or-nothing.
    with Session(engine) as db, db.begin():
        db.execute(
            text(
                "INSERT INTO lecturer_availabilities (round_id, lecturer_id, timeslot_id, state) "
                "VALUES (:round_id, :lecturer_id, :timeslot_id, 'AVAILABLE')"
            ),
            {"round_id": round_id, "lecturer_id": members[0], "timeslot_id": slot_id},
        )
    with Session(engine) as db:
        context, _, _, _ = _round_input(db, round_id)
    assert context.has_assigned_committees is True
    assert context.committee_reviewer_sets == ()

    with Session(engine) as db, db.begin():
        db.execute(
            text(
                "INSERT INTO lecturer_availabilities (round_id, lecturer_id, timeslot_id, state) "
                "VALUES (:round_id, :lecturer_id, :timeslot_id, 'AVAILABLE')"
            ),
            {"round_id": round_id, "lecturer_id": members[1], "timeslot_id": slot_id},
        )
    with Session(engine) as db:
        context, _, _, _ = _round_input(db, round_id)
    assert context.committee_reviewer_sets == (members,)

    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM lecturer_availabilities WHERE round_id = :id"), {"id": round_id})
        db.execute(text("DELETE FROM round_days WHERE round_id = :id"), {"id": round_id})


@pytest.mark.integration
def test_scheduling_readiness_names_committees_the_scheduler_would_drop(
    client, round_id, committee_ids, lecturer_ids
):
    before = client.get(f"/api/v1/rounds/{round_id}/scheduling-readiness", headers=HEADERS)
    assert before.status_code == 200
    assert before.json()["data"]["unusableCommittees"] == []
    assert "COMMITTEE_MEMBERS_NOT_ELIGIBLE" not in before.json()["data"]["blockers"]

    client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{committee_ids['RCMT-A']}"]},
    )

    after = client.get(f"/api/v1/rounds/{round_id}/scheduling-readiness", headers=HEADERS)
    data = after.json()["data"]
    assert "COMMITTEE_MEMBERS_NOT_ELIGIBLE" in data["blockers"]
    assert data["ready"] is False
    assert [item["code"] for item in data["unusableCommittees"]] == ["RCMT-A"]
    assert data["unusableCommittees"][0]["missingLecturerIds"] == sorted(lecturer_ids[:2])

    engine = get_engine(get_settings().database_url)
    with Session(engine) as db, db.begin():
        for lecturer_id in lecturer_ids[:2]:
            db.execute(
                text(
                    "INSERT INTO round_invitations (round_id, lecturer_id, status) "
                    "VALUES (:round_id, :lecturer_id, 'ACCEPTED')"
                ),
                {"round_id": round_id, "lecturer_id": lecturer_id},
            )

    cleared = client.get(f"/api/v1/rounds/{round_id}/scheduling-readiness", headers=HEADERS)
    assert cleared.json()["data"]["unusableCommittees"] == []
    assert "COMMITTEE_MEMBERS_NOT_ELIGIBLE" not in cleared.json()["data"]["blockers"]

    with Session(engine) as db, db.begin():
        db.execute(text("DELETE FROM round_invitations WHERE round_id = :id"), {"id": round_id})


@pytest.mark.integration
def test_deleting_an_assigned_committee_is_rejected(client, round_id, committee_ids):
    assigned = committee_ids["RCMT-A"]
    client.put(
        f"/api/v1/rounds/{round_id}/committees",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{assigned}"]},
    )

    single = client.request("DELETE", f"/api/v1/committees/cmt_{assigned}", headers=HEADERS)
    assert single.status_code == 409, single.text
    assert single.json()["error"]["code"] == "COMMITTEE_IN_USE"

    free = committee_ids["RCMT-B"]
    bulk = client.post(
        "/api/v1/committees/bulk-delete",
        headers=HEADERS,
        json={"committeeIds": [f"cmt_{assigned}", f"cmt_{free}"]},
    )
    assert bulk.status_code == 200, bulk.text
    body = bulk.json()["data"]
    assert body["deletedIds"] == [free]
    assert body["inUseIds"] == [assigned]
    assert body["deleted"] == 1
