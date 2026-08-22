"""Generate a transactional SQL cleanup/import from a defenserflowdb dump.

The script does not connect to PostgreSQL.  It parses the legacy PostgreSQL
COPY sections, restricts them to project codes supplied by the current DB, and
prints SQL for psql to execute.  The SQL creates a JSONB backup table first,
then removes obvious test accounts/semesters and imports derived groups,
student accounts, students, and memberships.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def sql(value: str | None) -> str:
    if value is None:
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


def parse_copy(dump_path: Path, table_name: str) -> list[dict[str, str | None]]:
    lines = dump_path.read_text(encoding="utf-8", errors="replace").splitlines()
    marker = f'COPY public."{table_name}" '
    for index, line in enumerate(lines):
        if not line.startswith(marker):
            continue
        columns = line[line.index("(") + 1 : line.index(")")].split(", ")
        rows: list[dict[str, str | None]] = []
        for raw in lines[index + 1 :]:
            if raw == r"\.":
                break
            values = raw.split("\t")
            if len(values) != len(columns):
                raise ValueError(
                    f"COPY {table_name} row has {len(values)} values, expected {len(columns)}"
                )

            def decode(value: str) -> str | None:
                if value == r"\N":
                    return None
                return (
                    value.replace(r"\t", "\t")
                    .replace(r"\n", "\n")
                    .replace(r"\r", "\r")
                    .replace(r"\\", "\\")
                )

            rows.append(dict(zip(columns, (decode(value) for value in values))))
        return rows
    raise ValueError(f'COPY section not found for public."{table_name}"')


def clean_text(value: str | None) -> str:
    return unicodedata.normalize("NFC", (value or "").strip())


def normalize_role(value: str | None) -> str:
    folded = clean_text(value).casefold()
    leader_tokens = ("leader", "trưởng", "nhóm trưởng", "lead")
    return "LEADER" if any(token in folded for token in leader_tokens) else "MEMBER"


@dataclass(frozen=True)
class Member:
    project_code: str
    student_code: str
    display_name: str
    membership_role: str


def load_members(dump_path: Path, project_codes: set[str]) -> tuple[list[Member], set[str], int]:
    topics = parse_copy(dump_path, "Topics")
    topic_by_id = {
        str(row["id"]): row
        for row in topics
        if row.get("id") is not None and row.get("topic_code") in project_codes
    }
    missing_topics = project_codes - {str(row.get("topic_code")) for row in topic_by_id.values()}
    if missing_topics:
        raise ValueError(f"Project codes missing from dump Topics: {sorted(missing_topics)}")

    raw_students = parse_copy(dump_path, "Topic_Students")
    members_by_project_code: dict[tuple[str, str], Member] = {}
    skipped_rows = 0
    for row in raw_students:
        topic = topic_by_id.get(str(row.get("topic_id")))
        if topic is None:
            continue
        project_code = str(topic["topic_code"])
        student_code = clean_text(row.get("student_code")).upper()
        display_name = clean_text(row.get("full_name"))
        if not student_code or not display_name:
            skipped_rows += 1
            continue
        member = Member(project_code, student_code, display_name, normalize_role(row.get("role_in_group")))
        key = (project_code, student_code)
        previous = members_by_project_code.get(key)
        if previous is None or (previous.membership_role == "MEMBER" and member.membership_role == "LEADER"):
            members_by_project_code[key] = member

    return list(members_by_project_code.values()), set(topic_by_id), skipped_rows


def validate_backup_table_name(name: str) -> None:
    if not re.fullmatch(r"db_cleanup_backup_[0-9]{8}_[0-9]{6}", name):
        raise ValueError("Backup table must match db_cleanup_backup_YYYYMMDD_HHMMSS")


def build_sql(
    backup_table: str,
    members: list[Member],
    project_codes: set[str],
) -> str:
    validate_backup_table_name(backup_table)
    lines = [r"\set ON_ERROR_STOP on", ""]

    lines.extend(
        [
            "BEGIN;",
            f"CREATE TABLE {backup_table} (",
            "    backup_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
            "    table_name text NOT NULL,",
            "    row_data jsonb NOT NULL,",
            "    backed_up_at timestamptz NOT NULL DEFAULT now()",
            ");",
            f"COMMENT ON TABLE {backup_table} IS {sql('Full public-table snapshot before cleanup/import')};",
            "DO $$",
            "DECLARE source_table record;",
            "BEGIN",
            "    FOR source_table IN",
            "        SELECT table_name FROM information_schema.tables",
            "        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'",
            f"          AND table_name NOT IN ('alembic_version', 'schema_meta', {sql(backup_table)})",
            "          AND table_name NOT LIKE 'db_cleanup_backup_%'",
            "    LOOP",
            f"        EXECUTE format('INSERT INTO {backup_table} (table_name, row_data) SELECT %L, to_jsonb(t) FROM public.%I t', source_table.table_name, source_table.table_name);",
            "    END LOOP;",
            "END $$;",
            "COMMIT;",
            "",
            "BEGIN;",
            "CREATE TEMP TABLE cleanup_delete_accounts ON COMMIT DROP AS",
            "SELECT id FROM accounts",
            "WHERE email LIKE '%@example.com'",
            "   OR email LIKE '%@example.test'",
            "   OR email = 'lecturer@gmail.com';",
            "CREATE TEMP TABLE cleanup_legacy_student ON COMMIT DROP AS",
            "SELECT id FROM accounts WHERE email = 'student1@gmail.com';",
            "DO $$",
            "DECLARE fk record; referenced_count bigint;",
            "BEGIN",
            "    FOR fk IN",
            "        SELECT child.relname AS child_table, child_col.attname AS child_column",
            "        FROM pg_constraint constraint_row",
            "        JOIN pg_class child ON child.oid = constraint_row.conrelid",
            "        JOIN pg_attribute child_col ON child_col.attrelid = child.oid AND child_col.attnum = constraint_row.conkey[1]",
            "        WHERE constraint_row.contype = 'f'",
            "          AND constraint_row.confrelid = 'public.accounts'::regclass",
            "    LOOP",
            "        IF fk.child_table NOT IN ('account_roles', 'auth_sessions', 'lecturers', 'students') THEN",
            "            EXECUTE format('SELECT count(*) FROM public.%I WHERE %I IN (SELECT id FROM cleanup_delete_accounts)', fk.child_table, fk.child_column) INTO referenced_count;",
            "            IF referenced_count > 0 THEN",
            "                RAISE EXCEPTION 'Cannot remove account data: %.% has % reference(s)', fk.child_table, fk.child_column, referenced_count;",
            "            END IF;",
            "        END IF;",
            "    END LOOP;",
            "END $$;",
            "DELETE FROM group_memberships WHERE student_id IN (SELECT id FROM students WHERE account_id IN (SELECT id FROM cleanup_legacy_student));",
            "DELETE FROM students WHERE account_id IN (SELECT id FROM cleanup_legacy_student);",
            "DELETE FROM account_roles WHERE account_id IN (SELECT id FROM cleanup_legacy_student);",
            "UPDATE accounts SET status = 'INACTIVE' WHERE id IN (SELECT id FROM cleanup_legacy_student);",
            "DELETE FROM lecturers WHERE account_id IN (SELECT id FROM cleanup_delete_accounts);",
            "DELETE FROM students WHERE account_id IN (SELECT id FROM cleanup_delete_accounts);",
            "DELETE FROM accounts WHERE id IN (SELECT id FROM cleanup_delete_accounts);",
            "DELETE FROM semesters WHERE code <> 'SU26';",
            "",
        ]
    )

    for student_code in sorted({member.student_code for member in members}):
        display_name = next(member.display_name for member in members if member.student_code == student_code)
        email = f"student.{student_code.lower()}@fpt.edu.vn"
        lines.extend(
            [
                (
                    "INSERT INTO accounts (email, display_name, password_hash) VALUES "
                    f"({sql(email)}, {sql(display_name)}, (SELECT password_hash FROM accounts WHERE email = 'admin@gmail.com')) "
                    "ON CONFLICT (email) DO UPDATE SET display_name = EXCLUDED.display_name, status = 'ACTIVE';"
                ),
                (
                    "INSERT INTO account_roles (account_id, role) "
                    f"SELECT id, 'STUDENT'::system_role FROM accounts WHERE email = {sql(email)} "
                    "ON CONFLICT DO NOTHING;"
                ),
                (
                    "INSERT INTO students (account_id, student_code) "
                    f"SELECT id, {sql(student_code)} FROM accounts WHERE email = {sql(email)} "
                    "ON CONFLICT (student_code) DO UPDATE SET account_id = EXCLUDED.account_id;"
                ),
            ]
        )

    for project_code in sorted({member.project_code for member in members}):
        lines.append(
            "INSERT INTO groups (project_id, code) "
            f"SELECT p.id, {sql('GRP-' + project_code)} FROM projects p "
            "JOIN semesters s ON s.id = p.semester_id "
            f"WHERE s.code = 'SU26' AND p.code = {sql(project_code)} "
            "ON CONFLICT (project_id) DO NOTHING;"
        )

    for member in sorted(members, key=lambda item: (item.project_code, item.student_code)):
        email = f"student.{member.student_code.lower()}@fpt.edu.vn"
        lines.append(
            "INSERT INTO group_memberships (group_id, student_id, membership_role) "
            "SELECT g.id, s.id, "
            f"{sql(member.membership_role)}::membership_role FROM groups g "
            "JOIN projects p ON p.id = g.project_id "
            "JOIN semesters sem ON sem.id = p.semester_id "
            "JOIN students s ON s.student_code = "
            f"{sql(member.student_code)} "
            "WHERE sem.code = 'SU26' AND p.code = "
            f"{sql(member.project_code)} "
            "AND NOT EXISTS (SELECT 1 FROM group_memberships existing "
            "WHERE existing.group_id = g.id AND existing.student_id = s.id AND existing.status = 'ACTIVE');"
        )

    import_summary = {
        "backup_table": backup_table,
        "project_codes_considered": len(project_codes),
        "projects_with_students": len({member.project_code for member in members}),
        "unique_students": len({member.student_code for member in members}),
        "memberships": len(members),
    }
    lines.extend(
        [
            (
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) "
                "SELECT id, 'DATABASE_CLEANUP_AND_GROUP_IMPORT', 'database', "
                f"{sql(backup_table)}, {sql('Removed test semesters/accounts and imported groups/students from defenserflowdb')}, "
                f"{sql(json.dumps(import_summary, ensure_ascii=False))}::jsonb FROM accounts WHERE email = 'admin@gmail.com';"
            ),
            "COMMIT;",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dump", type=Path)
    parser.add_argument("--project-code", action="append", required=True)
    parser.add_argument("--backup-table", required=True)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--output", type=Path, help="Write generated SQL as UTF-8 instead of stdout.")
    args = parser.parse_args()

    project_codes = {clean_text(code).upper() for code in args.project_code if clean_text(code)}
    members, source_codes, skipped_rows = load_members(args.dump.resolve(), project_codes)
    summary: dict[str, Any] = {
        "source": args.dump.resolve().name,
        "project_codes_considered": len(project_codes),
        "source_project_codes_found": len(source_codes),
        "projects_with_students": len({member.project_code for member in members}),
        "unique_students": len({member.student_code for member in members}),
        "memberships": len(members),
        "skipped_rows_without_code_or_name": skipped_rows,
    }
    if args.summary:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    generated_sql = build_sql(args.backup_table, members, project_codes)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(generated_sql, encoding="utf-8")
    else:
        sys.stdout.write(generated_sql)


if __name__ == "__main__":
    main()
