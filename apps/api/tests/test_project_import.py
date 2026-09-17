from io import BytesIO
from uuid import uuid4

import pytest
from openpyxl import Workbook

ADMIN_HEADERS = {"X-Test-Session": "active-admin"}
HEADER_ROW = ["STT", "Ma de tai", "Ma nhom", "Ten de tai Tieng Anh/ Tieng Nhat", "Ten de tai Tieng Viet", "GVHD", "GVHD2"]


def _workbook(rows: list[list[object]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(HEADER_ROW)
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _upload(client, semester_id: int, content: bytes, headers: dict[str, str] = ADMIN_HEADERS):
    return client.post(
        f"/api/v1/projects/import?semesterId={semester_id}",
        headers=headers,
        files={"file": ("projects.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


def _seed_semester_and_lecturer(client) -> tuple[int, str]:
    """seed-fixture gives a clean ACTIVE semester + a couple of lecturers to import against."""
    client.post("/api/v1/admin/seed-fixture", headers=ADMIN_HEADERS)
    semester_id = client.get("/api/v1/semesters", headers=ADMIN_HEADERS).json()["data"][0]["id"]
    suffix = uuid4().hex[:8]
    lecturer_code = f"GVIMP{suffix}"
    create = client.post(
        "/api/v1/accounts",
        headers=ADMIN_HEADERS,
        json={
            "email": f"gvimp.{suffix}@example.com",
            "displayName": "Test GVHD",
            "password": "P@ssword12345",
            "role": "LECTURER",
            "lecturerCode": lecturer_code,
        },
    )
    assert create.status_code == 201, create.text
    return semester_id, lecturer_code


@pytest.mark.integration
def test_import_projects_creates_project_group_and_main_supervisor(client):
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    project_code = f"PRJ{suffix}"
    group_code = f"GRP{suffix}"
    content = _workbook([[1, project_code, group_code, "Title EN", "Title VI", lecturer_code.lower(), None]])

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["updated"] == 0
    assert body["skipped"] == 0
    assert body["errors"] == []


@pytest.mark.integration
def test_import_projects_upserts_on_rerun_instead_of_duplicating(client):
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    project_code = f"PRJ{suffix}"
    group_code = f"GRP{suffix}"
    content = _workbook([[1, project_code, group_code, "Title EN", "Title VI", lecturer_code, None]])

    first = _upload(client, semester_id, content)
    assert first.json()["created"] == 1

    second = _upload(client, semester_id, content)
    assert second.status_code == 201, second.text
    body = second.json()
    assert body["created"] == 0
    assert body["updated"] == 1
    assert body["skipped"] == 0


@pytest.mark.integration
def test_import_projects_row_with_unmatched_gvhd_is_skipped_not_fatal(client):
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    good_code = f"PRJ{suffix}A"
    bad_code = f"PRJ{suffix}B"
    content = _workbook(
        [
            [1, good_code, f"GRP{suffix}A", "Title EN", "Title VI", lecturer_code, None],
            [2, bad_code, f"GRP{suffix}B", "Title EN", "Title VI", "NO-SUCH-CODE", None],
        ]
    )

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 1
    assert body["errors"][0]["code"] == "GVHD_NOT_FOUND"


@pytest.mark.integration
def test_import_projects_requires_admin_or_manager_role(client):
    content = _workbook([[1, "PRJX001", "GRPX001", "Title EN", "Title VI", "SOMEONE", None]])
    response = client.post(
        "/api/v1/projects/import?semesterId=1",
        headers={"X-Test-Session": "active-student"},
        files={"file": ("projects.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 403
