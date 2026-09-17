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
def test_import_projects_finds_header_row_below_a_banner_row(client):
    """Real user file (DanhSachDeTai_FA26.xlsx) has a title banner in row 1 and the real
    header in row 2 — the naive "row 0 is always the header" assumption silently misparsed
    every single row. Regression test for that exact shape."""
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    project_code = f"PRJ{suffix}"
    group_code = f"GRP{suffix}"

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["PROJECTS INFORMATION"])  # banner row, not the header
    sheet.append(HEADER_ROW)
    sheet.append([1, project_code, group_code, "Title EN", "Title VI", lecturer_code, None])
    buffer = BytesIO()
    workbook.save(buffer)

    response = _upload(client, semester_id, buffer.getvalue())

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 0


HEADER_ROW_WITH_DEPARTMENT = ["STT", "Ma de tai", "Ma nhom", "Ten de tai Tieng Anh/ Tieng Nhat", "Ten de tai Tieng Viet", "Department", "GVHD", "GVHD2"]
# Fixed, reused across runs — the major upsert (ON CONFLICT DO UPDATE) makes this idempotent,
# so this never leaks a new majors row per test run the way a per-run uuid code would.
_TEST_MAJOR_CODE = "ZZTEST"


def _project_row(code: str, group: str, dept, lecturer_code: str) -> list[object]:
    return [1, code, group, "Title EN", "Title VI", dept, lecturer_code, None]


def _get_major_code(client, semester_id: int, project_code: str) -> str | None:
    projects = client.get("/api/v1/projects", headers=ADMIN_HEADERS, params={"semesterId": semester_id}).json()
    return next((p.get("majorCode") for p in projects if p["code"] == project_code.upper()), None)


@pytest.mark.integration
def test_import_projects_maps_department_to_major_and_creates_new_ones(client):
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(HEADER_ROW_WITH_DEPARTMENT)
    sheet.append(_project_row(f"PRJ{suffix}A", f"GRP{suffix}A", "SE", lecturer_code))
    sheet.append(_project_row(f"PRJ{suffix}B", f"GRP{suffix}B", _TEST_MAJOR_CODE, lecturer_code))
    buffer = BytesIO()
    workbook.save(buffer)

    response = _upload(client, semester_id, buffer.getvalue())

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 2
    assert body["skipped"] == 0
    assert _get_major_code(client, semester_id, f"PRJ{suffix}A") == "SE"
    assert _get_major_code(client, semester_id, f"PRJ{suffix}B") == _TEST_MAJOR_CODE


@pytest.mark.integration
def test_import_projects_rerun_with_changed_department_updates_major(client):
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    code, group = f"PRJ{suffix}", f"GRP{suffix}"

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(HEADER_ROW_WITH_DEPARTMENT)
    sheet.append(_project_row(code, group, "SE", lecturer_code))
    buffer = BytesIO()
    workbook.save(buffer)
    first = _upload(client, semester_id, buffer.getvalue())
    assert first.json()["created"] == 1
    assert _get_major_code(client, semester_id, code) == "SE"

    workbook2 = Workbook()
    sheet2 = workbook2.active
    sheet2.append(HEADER_ROW_WITH_DEPARTMENT)
    sheet2.append(_project_row(code, group, _TEST_MAJOR_CODE, lecturer_code))
    buffer2 = BytesIO()
    workbook2.save(buffer2)
    second = _upload(client, semester_id, buffer2.getvalue())

    assert second.status_code == 201, second.text
    assert second.json()["updated"] == 1
    assert _get_major_code(client, semester_id, code) == _TEST_MAJOR_CODE


@pytest.mark.integration
def test_import_projects_rerun_with_blank_department_keeps_existing_major(client):
    """The FE's own documented template has no Department column at all — a sheet built from
    it must NOT reset an existing project's (possibly non-SE) major back to the SE default."""
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    code, group = f"PRJ{suffix}", f"GRP{suffix}"

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(HEADER_ROW_WITH_DEPARTMENT)
    sheet.append(_project_row(code, group, _TEST_MAJOR_CODE, lecturer_code))
    buffer = BytesIO()
    workbook.save(buffer)
    first = _upload(client, semester_id, buffer.getvalue())
    assert first.json()["created"] == 1
    assert _get_major_code(client, semester_id, code) == _TEST_MAJOR_CODE

    # Re-import using the plain template (no Department column at all).
    content = _workbook([[1, code, group, "Title EN", "Title VI 2", lecturer_code, None]])
    second = _upload(client, semester_id, content)

    assert second.status_code == 201, second.text
    assert second.json()["updated"] == 1
    assert _get_major_code(client, semester_id, code) == _TEST_MAJOR_CODE


@pytest.mark.integration
def test_import_projects_no_header_row_returns_422(client):
    semester_id, _ = _seed_semester_and_lecturer(client)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Not", "A", "Header", "Row"])
    sheet.append(["just", "some", "data", "here"])
    buffer = BytesIO()
    workbook.save(buffer)

    response = _upload(client, semester_id, buffer.getvalue())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "IMPORT_INVALID_FILE"


@pytest.mark.integration
def test_import_projects_requires_admin_or_manager_role(client):
    content = _workbook([[1, "PRJX001", "GRPX001", "Title EN", "Title VI", "SOMEONE", None]])
    response = client.post(
        "/api/v1/projects/import?semesterId=1",
        headers={"X-Test-Session": "active-student"},
        files={"file": ("projects.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 403


STUDENT_HEADER_ROW = [
    "STT", "MSSV", "Ho va ten", "Ma nhom", "Ma de tai",
    "Ten de tai Tieng Anh/ Tieng Nhat", "Ten de tai Tieng Viet", "GVHD 1", "GVHD 2", "Nganh",
]


def _student_workbook(rows: list[list[object]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(STUDENT_HEADER_ROW)
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _seed_semester_and_named_lecturer(client, display_name: str) -> tuple[int, str]:
    client.post("/api/v1/admin/seed-fixture", headers=ADMIN_HEADERS)
    semester_id = client.get("/api/v1/semesters", headers=ADMIN_HEADERS).json()["data"][0]["id"]
    suffix = uuid4().hex[:8]
    lecturer_code = f"GVIMP{suffix}"
    create = client.post(
        "/api/v1/accounts",
        headers=ADMIN_HEADERS,
        json={
            "email": f"gvimp.{suffix}@example.com",
            "displayName": display_name,
            "password": "P@ssword12345",
            "role": "LECTURER",
            "lecturerCode": lecturer_code,
        },
    )
    assert create.status_code == 201, create.text
    return semester_id, lecturer_code


def _add_named_lecturer(client, display_name: str) -> str:
    suffix = uuid4().hex[:8]
    lecturer_code = f"GVIMP{suffix}"
    create = client.post(
        "/api/v1/accounts",
        headers=ADMIN_HEADERS,
        json={
            "email": f"gvimp.{suffix}@example.com",
            "displayName": display_name,
            "password": "P@ssword12345",
            "role": "LECTURER",
            "lecturerCode": lecturer_code,
        },
    )
    assert create.status_code == 201, create.text
    return lecturer_code


@pytest.mark.integration
def test_import_projects_student_format_creates_group_with_leader_and_members(client):
    """1 dòng/sinh viên, GVHD khớp theo tên — dòng đầu (có Mã nhóm) là Leader."""
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    code, group = f"PRJ{suffix}", f"GRP{suffix}"
    mssv_leader, mssv_member = f"SE{suffix}A", f"SE{suffix}B"
    content = _student_workbook([
        [1, mssv_leader, "Leader Name", group, code, "Title EN", "Title VI", lecturer_name, None, "SE"],
        [2, mssv_member, "Member Name", None, None, None, None, None, None, None],
    ])

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 0
    assert body["studentsCreated"] == 2
    assert body["membersAssigned"] == 2

    project = next(p for p in client.get("/api/v1/projects", headers=ADMIN_HEADERS, params={"semesterId": semester_id}).json() if p["code"] == code.upper())
    assert project["majorCode"] == "SE"
    detail = client.get(f"/api/v1/projects/{project['id']}", headers=ADMIN_HEADERS).json()["data"]
    members = client.get(f"/api/v1/groups/{detail['group']['id']}/members", headers=ADMIN_HEADERS).json()["data"]
    roles = {m["studentCode"]: m["role"] for m in members}
    assert roles[mssv_leader.upper()] == "LEADER"
    assert roles[mssv_member.upper()] == "MEMBER"


@pytest.mark.integration
def test_import_projects_student_format_creates_student_without_account(client):
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    code, group, mssv = f"PRJ{suffix}", f"GRP{suffix}", f"SE{suffix}"
    content = _student_workbook([[1, mssv, "Some Student", group, code, "Title EN", "Title VI", lecturer_name, None, None]])

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    assert response.json()["studentsCreated"] == 1
    students = client.get("/api/v1/students", headers=ADMIN_HEADERS, params={"search": mssv}).json()["data"]
    assert len(students) == 1
    assert students[0]["fullName"] == "Some Student"


@pytest.mark.integration
def test_import_projects_student_format_gvhd_name_ambiguous_is_not_found(client):
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Dup {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    _add_named_lecturer(client, lecturer_name)
    content = _student_workbook([[1, f"SE{suffix}", "Some Student", f"GRP{suffix}", f"PRJ{suffix}", "Title EN", "Title VI", lecturer_name, None, None]])

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 0
    assert body["errors"][0]["code"] == "GVHD_NOT_FOUND"


@pytest.mark.integration
def test_import_projects_student_format_member_already_in_another_group_errors(client):
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    mssv = f"SE{suffix}"
    first_group = _student_workbook([[1, mssv, "Shared Student", f"GRP{suffix}A", f"PRJ{suffix}A", "Title EN", "Title VI", lecturer_name, None, None]])
    first = _upload(client, semester_id, first_group)
    assert first.json()["created"] == 1

    second_group = _student_workbook([[1, mssv, "Shared Student", f"GRP{suffix}B", f"PRJ{suffix}B", "Title EN", "Title VI", lecturer_name, None, None]])
    second = _upload(client, semester_id, second_group)

    assert second.status_code == 201, second.text
    body = second.json()
    assert body["created"] == 1
    assert any(e["code"] == "MEMBER_ALREADY_IN_ANOTHER_GROUP" for e in body["errors"])


@pytest.mark.integration
def test_import_projects_student_format_rerun_reassigns_leader(client):
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    code, group = f"PRJ{suffix}", f"GRP{suffix}"
    mssv_a, mssv_b = f"SE{suffix}A", f"SE{suffix}B"
    first = _student_workbook([
        [1, mssv_a, "Student A", group, code, "Title EN", "Title VI", lecturer_name, None, None],
        [2, mssv_b, "Student B", None, None, None, None, None, None, None],
    ])
    assert _upload(client, semester_id, first).json()["created"] == 1

    # Re-run with the members swapped: mssv_b is now the header row -> new leader.
    second = _student_workbook([
        [1, mssv_b, "Student B", group, code, "Title EN", "Title VI", lecturer_name, None, None],
        [2, mssv_a, "Student A", None, None, None, None, None, None, None],
    ])
    response = _upload(client, semester_id, second)

    assert response.status_code == 201, response.text
    project = next(p for p in client.get("/api/v1/projects", headers=ADMIN_HEADERS, params={"semesterId": semester_id}).json() if p["code"] == code.upper())
    detail = client.get(f"/api/v1/projects/{project['id']}", headers=ADMIN_HEADERS).json()["data"]
    members = client.get(f"/api/v1/groups/{detail['group']['id']}/members", headers=ADMIN_HEADERS).json()["data"]
    roles = {m["studentCode"]: m["role"] for m in members}
    assert roles[mssv_b.upper()] == "LEADER"
    assert roles[mssv_a.upper()] == "MEMBER"


@pytest.mark.integration
def test_import_projects_legacy_row_missing_group_code_is_rejected_not_dropped(client):
    """Regression: block-grouping must not silently swallow a legacy (no-MSSV) row that
    has no Mã nhóm — it must still surface REQUIRED_FIELD_MISSING like every other row."""
    semester_id, lecturer_code = _seed_semester_and_lecturer(client)
    suffix = uuid4().hex[:8]
    good_code = f"PRJ{suffix}A"
    content = _workbook([
        [1, good_code, f"GRP{suffix}A", "Title EN", "Title VI", lecturer_code, None],
        [2, f"PRJ{suffix}B", None, "Title EN", "Title VI", lecturer_code, None],  # blank Ma nhom
    ])

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 1
    assert body["errors"][0]["code"] == "REQUIRED_FIELD_MISSING"


@pytest.mark.integration
def test_import_projects_student_format_duplicate_mssv_in_block_is_rejected(client):
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    code, group, mssv = f"PRJ{suffix}", f"GRP{suffix}", f"SE{suffix}"
    content = _student_workbook([
        [1, mssv, "Student", group, code, "Title EN", "Title VI", lecturer_name, None, None],
        [2, mssv, "Student", None, None, None, None, None, None, None],  # same MSSV again
    ])

    response = _upload(client, semester_id, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["membersAssigned"] == 1
    assert any(e["code"] == "MEMBERSHIP_DUPLICATE" for e in body["errors"])


@pytest.mark.integration
def test_import_projects_student_format_department_cache_survives_a_later_row_failure(client):
    """Regression: major_by_code must not be poisoned when the row that FIRST creates a new
    Department also fails inside its own savepoint (e.g. GROUP_CODE_MISMATCH, raised after
    the major INSERT but before commit) — the savepoint rollback must undo the major insert
    at the DB level too, so a later row reusing that Department creates it fresh instead of
    inheriting a cached id that no longer exists (which would 500→PROJECT_ROW_INVALID)."""
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    dept = f"DPT{suffix}"[:20].upper()
    clash_code = f"PRJ{suffix}CLASH"

    # Row 1: claims clash_code under group G1 — unrelated department, succeeds normally.
    first = _upload(client, semester_id, _student_workbook([
        [1, f"SE{suffix}A", "Student A", f"GRP{suffix}G1", clash_code, "Title EN", "Title VI", lecturer_name, None, None],
    ]))
    assert first.json()["created"] == 1

    # Row 2 introduces `dept` for the first time (fresh INSERT INTO majors inside its
    # savepoint) but reuses clash_code under a DIFFERENT group -> GROUP_CODE_MISMATCH,
    # rolling back the whole savepoint including the majors insert.
    # Row 3 reuses the same never-successfully-created `dept` on a brand new project.
    second = _upload(client, semester_id, _student_workbook([
        [1, f"SE{suffix}B", "Student B", f"GRP{suffix}G2", clash_code, "Title EN", "Title VI", lecturer_name, None, dept],
        [2, f"SE{suffix}C", "Student C", f"GRP{suffix}G3", f"PRJ{suffix}NEW", "Title EN", "Title VI", lecturer_name, None, dept],
    ]))

    assert second.status_code == 201, second.text
    body = second.json()
    assert body["created"] == 1
    assert any(e["code"] == "GROUP_CODE_MISMATCH" for e in body["errors"])
    assert _get_major_code(client, semester_id, f"PRJ{suffix}NEW") == dept


@pytest.mark.integration
def test_import_projects_student_format_account_can_be_created_after_import(client):
    """Regression: students.student_code UNIQUE must not block linking a login account to
    a student row that this import already created without one."""
    suffix = uuid4().hex[:8]
    lecturer_name = f"GVHD Test {suffix}"
    semester_id, _ = _seed_semester_and_named_lecturer(client, lecturer_name)
    mssv = f"SE{suffix}"
    content = _student_workbook([[1, mssv, "Some Student", f"GRP{suffix}", f"PRJ{suffix}", "Title EN", "Title VI", lecturer_name, None, None]])
    assert _upload(client, semester_id, content).json()["studentsCreated"] == 1

    create = client.post(
        "/api/v1/accounts",
        headers=ADMIN_HEADERS,
        json={
            "email": f"student.{suffix}@example.com",
            "displayName": "Some Student",
            "password": "P@ssword12345",
            "role": "STUDENT",
            "studentCode": mssv,
        },
    )
    assert create.status_code == 201, create.text

    students = client.get("/api/v1/students", headers=ADMIN_HEADERS, params={"search": mssv}).json()["data"]
    assert students[0]["email"] == f"student.{suffix}@example.com"
