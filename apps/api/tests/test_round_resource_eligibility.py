from contextlib import nullcontext

import pytest
from fastapi import HTTPException

from app.auth import CurrentUser
from app.routes.master_data import RoundResources, attach_round_resources


class _Result:
    def __init__(self, *, scalar=None, mapping=None):
        self._scalar = scalar
        self._mapping = mapping

    def scalar_one_or_none(self):
        return self._scalar

    def scalar_one(self):
        return self._scalar

    def mappings(self):
        return self

    def one_or_none(self):
        return self._mapping


class _RoundResourceSession:
    def __init__(self, group: dict[str, object]):
        self.group = group
        self.inserted = False

    def begin(self):
        return nullcontext()

    def execute(self, statement, _params=None):
        sql = str(statement)
        if sql.startswith("SELECT semester_id FROM rounds"):
            return _Result(scalar=1)
        if sql.startswith("SELECT status FROM semesters"):
            return _Result(scalar="ACTIVE")
        if sql.startswith("SELECT type::text AS type, semester_id FROM rounds"):
            return _Result(mapping={"type": "DEFENSE_1_2", "semester_id": 1})
        if sql.startswith("SELECT g.status::text AS status"):
            return _Result(mapping=self.group)
        if sql.startswith("INSERT INTO round_groups"):
            self.inserted = True
            return _Result()
        if sql.startswith("SELECT COUNT(*) FROM rooms"):
            return _Result(scalar=0)
        return _Result()


def _group(**overrides):
    return {
        "status": "ELIGIBLE_D12",
        "semester_id": 1,
        "project_status": "ACTIVE",
        "has_active_leader": True,
        "has_main_supervisor": True,
        "has_prior_review_1": False,
        **overrides,
    }


@pytest.mark.parametrize(
    ("group", "code"),
    [
        (_group(semester_id=2), "GROUP_SEMESTER_MISMATCH"),
        (_group(status="PENDING_D11"), "GROUP_NOT_ELIGIBLE"),
        (_group(has_active_leader=False), "GROUP_NOT_ELIGIBLE"),
        (_group(has_main_supervisor=False), "GROUP_NOT_ELIGIBLE"),
    ],
)
def test_attach_round_resources_rejects_groups_filtered_out_by_eligibility(group, code):
    session = _RoundResourceSession(group)

    with pytest.raises(HTTPException) as caught:
        attach_round_resources(
            10,
            RoundResources(group_ids=[42]),
            session,
            CurrentUser(role="MANAGER"),
        )

    assert caught.value.status_code == 409
    assert caught.value.detail["code"] == code
    assert session.inserted is False


def test_attach_round_resources_accepts_an_eligible_same_semester_group():
    session = _RoundResourceSession(_group())

    result = attach_round_resources(
        10,
        RoundResources(group_ids=[42]),
        session,
        CurrentUser(role="MANAGER"),
    )

    assert result["groups"] == 1
    assert session.inserted is True
