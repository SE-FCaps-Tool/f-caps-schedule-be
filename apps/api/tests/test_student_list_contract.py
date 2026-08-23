from app.auth import CurrentUser
from app.main import create_app
from app.routes.master_data import list_students


class _Rows:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _RecordingSession:
    def __init__(self):
        self.sql = ""
        self.params = {}

    def execute(self, statement, params=None):
        self.sql = str(statement)
        self.params = params or {}
        return _Rows(
            [
                {
                    "id": 7,
                    "student_code": "SE007",
                    "full_name": "Nguyen Van An",
                    "email": "an@example.test",
                    "total_count": 3,
                }
            ]
        )


def test_students_openapi_exposes_search_pagination_and_group_filters():
    operation = create_app().openapi()["paths"]["/api/v1/students"]["get"]
    parameters = {parameter["name"] for parameter in operation["parameters"]}

    assert {"search", "page", "pageSize", "hasGroup", "semesterId"} <= parameters


def test_list_students_returns_names_email_meta_and_scoped_availability_filter():
    session = _RecordingSession()

    result = list_students(
        db=session,
        user=CurrentUser(role="MANAGER"),
        search="an",
        semester_id=1,
        has_group=False,
        page=2,
        page_size=25,
    )

    assert result == {
        "data": [
            {
                "id": 7,
                "studentCode": "SE007",
                "fullName": "Nguyen Van An",
                "email": "an@example.test",
            }
        ],
        "meta": {"page": 2, "pageSize": 25, "total": 3},
    }
    assert "a.display_name ILIKE" in session.sql
    assert "gm.status = 'ACTIVE'" in session.sql
    assert "p.semester_id" in session.sql
    assert session.params == {
        "search": "an",
        "semester_id": 1,
        "has_group": False,
        "limit": 25,
        "offset": 25,
    }
