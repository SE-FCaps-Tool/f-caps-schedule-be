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


class _SemesterDb:
    def __init__(self, rows):
        self.rows = rows
        self.statement = ""
        self.params = None

    def execute(self, statement, params):
        self.statement = str(statement)
        self.params = params
        return _MappingsResult(self.rows)


def test_lecturer_semesters_returns_only_related_semester_catalog(monkeypatch):
    db = _SemesterDb(
        [
            {
                "id": 2,
                "code": "SU26",
                "name": "Summer 2026",
                "status": "ACTIVE",
                "start_date": "2026-05-04",
                "end_date": "2026-08-16",
            }
        ]
    )
    monkeypatch.setattr(target_portals, "_lecturer_id", lambda _db, _user: 7)

    response = jsonable_encoder(target_portals.lecturer_semesters(db, SimpleNamespace(role="LECTURER")))

    assert response == {
        "data": [
            {
                "id": 2,
                "code": "SU26",
                "name": "Summer 2026",
                "status": "ACTIVE",
                "startDate": "2026-05-04",
                "endDate": "2026-08-16",
            }
        ]
    }
    assert db.params == {"lecturer_id": 7}
    assert "round_invitations" in db.statement
    assert "project_supervisors" in db.statement
    assert "remediation_cases" in db.statement


def test_lecturer_invitation_semester_filter_is_forwarded_to_sql(monkeypatch):
    db = _SemesterDb([])
    monkeypatch.setattr(target_portals, "_lecturer_id", lambda _db, _user: 7)

    response = target_portals.lecturer_invitations(
        db,
        SimpleNamespace(role="LECTURER"),
        semester_id=42,
    )

    assert response == {"data": []}
    assert db.params == {"lecturer_id": 7, "semester_id": 42}
    assert ":semester_id IS NULL OR r.semester_id = :semester_id" in db.statement
