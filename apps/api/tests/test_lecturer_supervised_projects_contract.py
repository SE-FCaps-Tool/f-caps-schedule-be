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


class _ProjectsDb:
    def __init__(self, rows):
        self.rows = rows
        self.statement = ""
        self.params = None

    def execute(self, statement, params):
        self.statement = str(statement)
        self.params = params
        return _MappingsResult(self.rows)


def test_lecturer_supervised_projects_includes_group_leader_and_members(monkeypatch):
    db = _ProjectsDb(
        [
            {
                "id": 5,
                "code": "DEMO-P05",
                "title": "Demo project",
                "status": "ACTIVE",
                "semester_id": 1,
                "semester_code": "SE-2026-2027",
                "supervisor_type": "MAIN",
                "group_id": 2,
                "group_code": "DEMO-G02",
                "member_count": 2,
                "leader": {"id": 11, "code": "SV001", "name": "Student One", "role": "LEADER", "status": "ACTIVE"},
                "members": [
                    {"id": 11, "code": "SV001", "name": "Student One", "role": "LEADER", "status": "ACTIVE"},
                    {"id": 12, "code": "SV002", "name": "Student Two", "role": "MEMBER", "status": "ACTIVE"},
                ],
            }
        ]
    )
    monkeypatch.setattr(target_portals, "_lecturer_id", lambda _db, _user: 7)

    response = jsonable_encoder(
        target_portals.lecturer_supervised_projects(db, SimpleNamespace(role="LECTURER"))
    )

    assert response["data"][0]["group"] == {
        "id": 2,
        "code": "DEMO-G02",
        "memberCount": 2,
        "leader": {"id": 11, "code": "SV001", "name": "Student One"},
        "members": [
            {"id": 11, "code": "SV001", "name": "Student One", "role": "LEADER", "status": "ACTIVE"},
            {"id": 12, "code": "SV002", "name": "Student Two", "role": "MEMBER", "status": "ACTIVE"},
        ],
    }
    assert db.params == {"lecturer_id": 7, "semester_id": None}
    assert "group_memberships" in db.statement
    assert "jsonb_agg" in db.statement
