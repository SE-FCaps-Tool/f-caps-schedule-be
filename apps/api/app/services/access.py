"""Server-side resource scoping for schedule, result and notification reads."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import CurrentUser


def is_management_user(user: CurrentUser) -> bool:
    return user.role in {"ADMIN", "MANAGER"}


def visible_session_ids(db: Session, user: CurrentUser, *, version_id: int | None = None) -> set[int]:
    """Return the sessions the actor may read.

    Management users can inspect the complete operational schedule. A Lecturer sees
    sessions where they are a Reviewer or a Supervisor of the group's project. A
    Student sees only sessions for groups where their active membership exists.
    Missing account identity deliberately yields no private records.
    """
    if is_management_user(user):
        rows = db.execute(
            text(
                "SELECT s.id FROM sessions s "
                "WHERE (:version_id IS NULL OR s.schedule_version_id = :version_id)"
            ),
            {"version_id": version_id},
        ).all()
        return {int(row[0]) for row in rows}
    if user.account_id is None:
        return set()
    if user.role == "LECTURER":
        rows = db.execute(
            text(
                "SELECT DISTINCT s.id FROM sessions s "
                "JOIN groups g ON g.id = s.group_id "
                "LEFT JOIN project_supervisors ps ON ps.project_id = g.project_id "
                "LEFT JOIN lecturers own_l ON own_l.id = ps.lecturer_id "
                "LEFT JOIN session_reviewers sr ON sr.session_id = s.id "
                "LEFT JOIN lecturers reviewer_l ON reviewer_l.id = sr.lecturer_id "
                "WHERE (:version_id IS NULL OR s.schedule_version_id = :version_id) "
                "AND (own_l.account_id = :account_id OR reviewer_l.account_id = :account_id)"
            ),
            {"version_id": version_id, "account_id": user.account_id},
        ).all()
        return {int(row[0]) for row in rows}
    if user.role == "STUDENT":
        rows = db.execute(
            text(
                "SELECT DISTINCT s.id FROM sessions s "
                "JOIN group_memberships gm ON gm.group_id = s.group_id "
                "JOIN students st ON st.id = gm.student_id "
                "WHERE (:version_id IS NULL OR s.schedule_version_id = :version_id) "
                "AND gm.status = 'ACTIVE' AND st.account_id = :account_id"
            ),
            {"version_id": version_id, "account_id": user.account_id},
        ).all()
        return {int(row[0]) for row in rows}
    return set()


def can_read_session(db: Session, user: CurrentUser, session_id: int) -> bool:
    return session_id in visible_session_ids(db, user)


def lecturer_id_for_account(db: Session, account_id: int | None) -> int | None:
    if account_id is None:
        return None
    return db.execute(
        text("SELECT id FROM lecturers WHERE account_id = :account_id"),
        {"account_id": account_id},
    ).scalar_one_or_none()


def student_id_for_account(db: Session, account_id: int | None) -> int | None:
    if account_id is None:
        return None
    return db.execute(
        text("SELECT id FROM students WHERE account_id = :account_id"),
        {"account_id": account_id},
    ).scalar_one_or_none()


def is_active_group_leader(db: Session, user: CurrentUser, group_id: int) -> bool:
    student_id = student_id_for_account(db, user.account_id)
    if student_id is None or user.role != "STUDENT":
        return False
    return (
        db.execute(
            text(
                "SELECT 1 FROM group_memberships WHERE group_id = :group_id "
                "AND student_id = :student_id AND status = 'ACTIVE' AND membership_role = 'LEADER'"
            ),
            {"group_id": group_id, "student_id": student_id},
        ).scalar_one_or_none()
        is not None
    )


def affected_schedule_recipients(db: Session, version_id: int) -> set[int]:
    """Return Reviewer, Supervisor, active Leader and Student accounts."""
    rows = db.execute(
        text(
            "SELECT DISTINCT a.id FROM accounts a WHERE a.id IN ("
            "SELECT la.account_id FROM session_reviewers sr "
            "JOIN lecturers la ON la.id = sr.lecturer_id WHERE sr.schedule_version_id = :version_id "
            "UNION SELECT sa.account_id FROM sessions s JOIN groups g ON g.id = s.group_id "
            "JOIN project_supervisors ps ON ps.project_id = g.project_id "
            "JOIN lecturers sa ON sa.id = ps.lecturer_id WHERE s.schedule_version_id = :version_id "
            "UNION SELECT st.account_id FROM sessions s JOIN group_memberships gm ON gm.group_id = s.group_id "
            "JOIN students st ON st.id = gm.student_id WHERE s.schedule_version_id = :version_id "
            ")"
        ),
        {"version_id": version_id},
    ).all()
    return {int(row[0]) for row in rows if row[0] is not None}


def affected_group_recipients(db: Session, group_id: int) -> set[int]:
    rows = db.execute(
        text(
            "SELECT DISTINCT a.id FROM accounts a WHERE a.id IN ("
            "SELECT l.account_id FROM project_supervisors ps JOIN projects p ON p.id = ps.project_id "
            "JOIN groups g ON g.project_id = p.id JOIN lecturers l ON l.id = ps.lecturer_id WHERE g.id = :group_id "
            "UNION SELECT st.account_id FROM group_memberships gm JOIN students st ON st.id = gm.student_id "
            "WHERE gm.group_id = :group_id AND gm.status = 'ACTIVE'"
            ")"
        ),
        {"group_id": group_id},
    ).all()
    return {int(row[0]) for row in rows if row[0] is not None}


def public_session_projection(row: dict[str, Any]) -> dict[str, Any]:
    """Keep private schedule details out of Student-facing list responses."""
    return row
