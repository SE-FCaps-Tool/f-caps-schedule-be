from io import BytesIO
from uuid import uuid4

import pytest
from openpyxl import Workbook

ADMIN_HEADERS = {"X-Test-Session": "active-admin"}


def _template_workbook(rows: list[tuple[str, str, str, str]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "LECTURERS INFORMATION"
    sheet.append(["LECTURERS INFORMATION", None, None, None])
    sheet.append(["STT", "Mã giảng viên", "Họ và tên", "Email"])
    for row in rows:
        sheet.append(list(row))
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _upload(client, content: bytes):
    return client.post(
        "/api/v1/lecturers/import",
        headers=ADMIN_HEADERS,
        files={"file": ("lecturers_template.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


@pytest.mark.integration
def test_import_lecturers_creates_accounts_and_returns_temp_passwords(client):
    client.post("/api/v1/admin/seed-fixture", headers=ADMIN_HEADERS)
    suffix = uuid4().hex[:8]
    code = f"GVI{suffix}"
    email = f"gvi.{suffix}@example.com"
    content = _template_workbook([("1", code, "Nguyen Van Import", email)])

    response = _upload(client, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 0
    assert body["errors"] == []
    assert len(body["accounts"]) == 1
    account = body["accounts"][0]
    assert account["lecturer_code"] == code.upper()
    assert account["email"] == email
    assert len(account["temp_password"]) >= 12

    lecturers = client.get("/api/v1/lecturers", headers=ADMIN_HEADERS, params={"search": code}).json()["data"]
    assert any(item["lecturerCode"] == code.upper() for item in lecturers)


@pytest.mark.integration
def test_import_lecturers_reports_missing_fields_and_duplicates(client):
    client.post("/api/v1/admin/seed-fixture", headers=ADMIN_HEADERS)
    suffix = uuid4().hex[:8]
    code = f"GVD{suffix}"
    email = f"gvd.{suffix}@example.com"
    content = _template_workbook(
        [
            ("1", code, "Duplicate Row One", email),
            ("2", code, "Duplicate Row Two", email),
            ("3", "", "Missing Code Row", f"missing.{suffix}@example.com"),
        ]
    )

    response = _upload(client, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 2
    codes = {error["code"] for error in body["errors"]}
    assert "LECTURER_DUPLICATE" in codes
    assert "REQUIRED_FIELD_MISSING" in codes


@pytest.mark.integration
def test_import_lecturers_rejects_file_without_template_header(client):
    client.post("/api/v1/admin/seed-fixture", headers=ADMIN_HEADERS)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["not", "a", "template"])
    buffer = BytesIO()
    workbook.save(buffer)

    response = _upload(client, buffer.getvalue())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "IMPORT_INVALID_FILE"


@pytest.mark.integration
def test_import_lecturers_requires_admin_or_manager_role(client):
    content = _template_workbook([("1", "GVX001", "Nguyen Van X", "gvx001@example.com")])
    response = client.post(
        "/api/v1/lecturers/import",
        headers={"X-Test-Session": "active-student"},
        files={"file": ("lecturers_template.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 403
