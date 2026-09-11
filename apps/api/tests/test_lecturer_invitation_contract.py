from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.encoders import jsonable_encoder

from app.routes import target_portals


class _MappingsResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _InvitationDb:
    def __init__(self, rows):
        self._rows = rows
        self.statement = ""
        self.params = None

    def execute(self, statement, params):
        self.statement = str(statement)
        self.params = params
        return _MappingsResult(self._rows)


def test_lecturer_invitations_matches_frontend_nested_contract(monkeypatch):
    deadline = datetime(2026, 8, 20, 16, 59, tzinfo=UTC)
    responded_at = datetime(2026, 8, 19, 8, 30, tzinfo=UTC)
    db = _InvitationDb(
        [
            {
                "round_id": 85,
                "lecturer_id": 7,
                "status": "ACCEPTED",
                "responded_at": responded_at,
                "round_name": "Review 3",
                "round_type": "REVIEW_3",
                "registration_deadline": deadline,
                "group_preference_deadline": None,
                "semester_id": 2,
                "semester_code": "SU26",
                "semester_name": "Summer 2026",
                "semester_status": "ACTIVE",
                "semester_start_date": "2026-05-04",
                "semester_end_date": "2026-08-16",
            }
        ]
    )
    monkeypatch.setattr(target_portals, "_lecturer_id", lambda _db, _user: 7)

    response = jsonable_encoder(
        target_portals.lecturer_invitations(db, SimpleNamespace(role="LECTURER"))
    )

    assert response == {
        "data": [
            {
                "id": "inv_85_7",
                "round": {
                    "id": "85",
                    "name": "Review 3",
                    "type": "REVIEW_3",
                    "registrationDeadline": "2026-08-20T16:59:00+00:00",
                    "semester": {
                        "id": 2,
                        "code": "SU26",
                        "name": "Summer 2026",
                        "status": "ACTIVE",
                        "startDate": "2026-05-04",
                        "endDate": "2026-08-16",
                    },
                },
                "status": "ACCEPTED",
                "respondedAt": "2026-08-19T08:30:00+00:00",
            }
        ]
    }
    assert db.params == {"lecturer_id": 7, "semester_id": None}
    assert "r.name AS round_name" in db.statement
    assert "r.registration_deadline" in db.statement


def test_lecturer_invitations_uses_round_type_when_legacy_round_name_is_null(monkeypatch):
    db = _InvitationDb(
        [
            {
                "round_id": 3,
                "lecturer_id": 7,
                "status": "PENDING",
                "responded_at": None,
                "round_name": None,
                "round_type": "REVIEW_1",
                "registration_deadline": datetime(2026, 8, 20, tzinfo=UTC),
                "group_preference_deadline": None,
                "semester_id": 2,
                "semester_code": "SU26",
                "semester_name": "Summer 2026",
                "semester_status": "ACTIVE",
                "semester_start_date": "2026-05-04",
                "semester_end_date": "2026-08-16",
            }
        ]
    )
    monkeypatch.setattr(target_portals, "_lecturer_id", lambda _db, _user: 7)

    invitation = target_portals.lecturer_invitations(db, SimpleNamespace(role="LECTURER"))["data"][0]

    assert invitation["round"]["name"] == "REVIEW_1"
    assert invitation["respondedAt"] is None


def test_lecturer_invitations_marks_overdue_pending_invitation_as_expired(monkeypatch):
    db = _InvitationDb(
        [
            {
                "round_id": 3,
                "lecturer_id": 7,
                "status": "PENDING",
                "responded_at": None,
                "round_name": "Review 1",
                "round_type": "REVIEW_1",
                "registration_deadline": datetime(2020, 1, 1, tzinfo=UTC),
                "group_preference_deadline": None,
                "semester_id": 2,
                "semester_code": "SU26",
                "semester_name": "Summer 2026",
                "semester_status": "ACTIVE",
                "semester_start_date": "2026-05-04",
                "semester_end_date": "2026-08-16",
            }
        ]
    )
    monkeypatch.setattr(target_portals, "_lecturer_id", lambda _db, _user: 7)

    invitation = target_portals.lecturer_invitations(db, SimpleNamespace(role="LECTURER"))["data"][0]

    assert invitation["status"] == "EXPIRED"
