import sys
from pathlib import Path

from sqlalchemy.sql.elements import TextClause

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.import_defense_eligibility import apply_import, load_reference


class _Result:
    def __init__(self, scalar=None, *, mapping=None, rows=None):
        self.scalar = scalar
        self.mapping = mapping
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def mappings(self):
        return self

    def one_or_none(self):
        return self.mapping

    def all(self):
        return self.rows


class _RecordingSession:
    def __init__(self):
        self.statements: list[str] = []

    def execute(self, statement: TextClause, _params=None):
        sql = str(statement)
        self.statements.append(sql)
        if sql.startswith("UPDATE groups SET status"):
            return _Result(42)
        return _Result()


def test_apply_import_updates_eligibility_without_creating_or_linking_round_by_default():
    session = _RecordingSession()
    reference = {
        "semester": {"id": 1, "start_date": "2026-05-11", "end_date": "2026-08-23"},
        "usable_groups": [{"group_id": 42}],
    }

    result = apply_import(
        session,
        reference,
        "SU26",
        "eligibility.xlsx",
        1,
        "Sheet1",
    )

    executed = "\n".join(session.statements)
    assert "INSERT INTO rounds" not in executed
    assert "INSERT INTO round_groups" not in executed
    assert "UPDATE groups SET status = 'ELIGIBLE_D12'" in executed
    assert result["round_id"] is None
    assert result["groups_linked"] == 0
    assert result["group_status_updated"] == 1


class _ReferenceSession:
    def __init__(self):
        self.statements: list[str] = []

    def execute(self, statement: TextClause, _params=None):
        sql = str(statement)
        self.statements.append(sql)
        if sql.startswith("SELECT id, start_date"):
            return _Result(
                mapping={
                    "id": 1,
                    "start_date": "2026-05-11",
                    "end_date": "2026-08-23",
                    "status": "ACTIVE",
                }
            )
        return _Result(
            rows=[
                {
                    "project_code": "P3",
                    "group_id": 3,
                    "group_code": "G3",
                    "member_count": 3,
                    "leader_count": 1,
                },
                {
                    "project_code": "P6",
                    "group_id": 6,
                    "group_code": "G6",
                    "member_count": 6,
                    "leader_count": 1,
                },
            ]
        )


def test_load_reference_allows_small_active_groups_but_rejects_oversized_groups():
    session = _ReferenceSession()

    reference = load_reference(session, "SU26", ["P3", "P6"])

    membership_sql = session.statements[1]
    assert "gm.status = 'ACTIVE'" in membership_sql
    assert [row["project_code"] for row in reference["usable_groups"]] == ["P3"]
    assert reference["invalid_group_codes"] == ["P6"]
