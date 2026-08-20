"""PostgreSQL outbox delivery for the in-app notification channel.

The email adapter intentionally stays local and deterministic in V1. It consumes
the same outbox event as the in-app channel so a future SMTP/provider adapter
cannot invent a second schedule payload.
"""

from dataclasses import dataclass
from typing import Any, Protocol

from sqlalchemy import text
from sqlalchemy.orm import Session


class EmailAdapter(Protocol):
    def send(self, *, recipient: str, event_type: str, payload: dict[str, Any]) -> None: ...


@dataclass(frozen=True)
class NoopEmailAdapter:
    """Local/P2 adapter: records no external side effect."""

    def send(self, *, recipient: str, event_type: str, payload: dict[str, Any]) -> None:
        return None


def process_outbox(
    db: Session,
    *,
    limit: int = 50,
    email_adapter: EmailAdapter | None = None,
) -> dict[str, int]:
    """Claim and deliver pending jobs exactly once per dedupe key."""
    adapter = email_adapter or NoopEmailAdapter()
    claimed = db.execute(
        text(
            "SELECT id, topic, payload, dedupe_key FROM outbox_jobs "
            "WHERE status = 'PENDING' AND available_at <= now() "
            "ORDER BY id FOR UPDATE SKIP LOCKED LIMIT :limit"
        ),
        {"limit": min(max(limit, 1), 200)},
    ).mappings().all()
    if not claimed:
        db.commit()
        return {"claimed": 0, "sent": 0, "failed": 0}
    sent = 0
    failed = 0
    for job in claimed:
        db.execute(text("UPDATE outbox_jobs SET status = 'PROCESSING', attempts = attempts + 1 WHERE id = :id"), {"id": job["id"]})
        try:
            payload = dict(job["payload"] or {})
            recipient_id = payload.get("recipient_id")
            recipient = db.execute(text("SELECT email FROM accounts WHERE id = :id"), {"id": recipient_id}).scalar_one_or_none()
            adapter.send(recipient=str(recipient or ""), event_type=str(job["topic"]), payload=payload)
            db.execute(text("UPDATE outbox_jobs SET status = 'SENT', processed_at = now() WHERE id = :id"), {"id": job["id"]})
            if job["dedupe_key"]:
                db.execute(text("UPDATE notifications SET status = 'SENT', sent_at = now() WHERE dedupe_key = :dedupe_key"), {"dedupe_key": job["dedupe_key"]})
            sent += 1
        except Exception:  # noqa: BLE001 - a failed delivery must be persisted and retried.
            db.execute(text("UPDATE outbox_jobs SET status = 'FAILED' WHERE id = :id"), {"id": job["id"]})
            if job["dedupe_key"]:
                db.execute(text("UPDATE notifications SET status = 'FAILED' WHERE dedupe_key = :dedupe_key"), {"dedupe_key": job["dedupe_key"]})
            failed += 1
    db.commit()
    return {"claimed": len(claimed), "sent": sent, "failed": failed}


def process_remediation_reminders(db: Session) -> int:
    """Create one reminder two days before due date and mark overdue cases."""
    upcoming = db.execute(
        text(
            "SELECT rc.id, rc.group_id, rc.due_at, l.account_id FROM remediation_cases rc "
            "JOIN lecturers l ON l.id = rc.verifier_lecturer_id "
            "WHERE rc.status = 'OPEN' AND rc.due_at > now() AND rc.due_at <= now() + interval '2 days'"
        )
    ).mappings().all()
    for case in upcoming:
        key = f"remediation-reminder:{case['id']}:{case['account_id']}"
        payload = {"remediation_id": case["id"], "group_id": case["group_id"], "due_at": case["due_at"], "recipient_id": case["account_id"]}
        _insert_event(db, "REMEDIATION_REMINDER", key, payload, case["account_id"])
    overdue = db.execute(
        text("UPDATE remediation_cases SET status = 'OVERDUE' WHERE status = 'OPEN' AND due_at <= now() RETURNING id, group_id, verifier_lecturer_id")
    ).mappings().all()
    for case in overdue:
        account_id = db.execute(text("SELECT account_id FROM lecturers WHERE id = :id"), {"id": case["verifier_lecturer_id"]}).scalar_one_or_none()
        if account_id is not None:
            key = f"remediation-overdue:{case['id']}:{account_id}"
            payload = {"remediation_id": case["id"], "group_id": case["group_id"], "recipient_id": account_id}
            _insert_event(db, "REMEDIATION_OVERDUE", key, payload, account_id)
    db.commit()
    return len(upcoming) + len(overdue)


def process_availability_reminders(db: Session) -> int:
    """Remind accepted Reviewers and active group Leaders before registration closes."""
    lecturer_rows = db.execute(
        text(
            "SELECT r.id AS round_id, "
            "COALESCE(GREATEST(r.registration_deadline, r.group_preference_deadline), "
            "r.registration_deadline, r.group_preference_deadline) AS effective_registration_deadline, "
            "ri.lecturer_id, l.account_id "
            "FROM rounds r JOIN round_invitations ri ON ri.round_id = r.id "
            "JOIN lecturers l ON l.id = ri.lecturer_id "
            "WHERE ri.status = 'ACCEPTED' "
            "AND COALESCE(GREATEST(r.registration_deadline, r.group_preference_deadline), "
            "r.registration_deadline, r.group_preference_deadline) > now() "
            "AND COALESCE(GREATEST(r.registration_deadline, r.group_preference_deadline), "
            "r.registration_deadline, r.group_preference_deadline) <= now() + interval '2 days' "
            "AND NOT EXISTS (SELECT 1 FROM lecturer_availabilities la "
            "WHERE la.round_id = r.id AND la.lecturer_id = ri.lecturer_id)"
        )
    ).mappings().all()
    for row in lecturer_rows:
        key = f"availability-reminder:lecturer:{row['round_id']}:{row['lecturer_id']}"
        _insert_event(
            db,
            "AVAILABILITY_REMINDER",
            key,
            {"round_id": row["round_id"], "lecturer_id": row["lecturer_id"], "deadline": row["effective_registration_deadline"], "recipient_id": row["account_id"]},
            row["account_id"],
        )
    leader_rows = db.execute(
        text(
            "SELECT r.id AS round_id, "
            "COALESCE(GREATEST(r.registration_deadline, r.group_preference_deadline), "
            "r.registration_deadline, r.group_preference_deadline) AS effective_registration_deadline, "
            "gm.group_id, st.account_id "
            "FROM rounds r JOIN round_groups rg ON rg.round_id = r.id "
            "JOIN group_memberships gm ON gm.group_id = rg.group_id AND gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER' "
            "JOIN students st ON st.id = gm.student_id "
            "WHERE r.group_selection_mode = TRUE "
            "AND COALESCE(GREATEST(r.registration_deadline, r.group_preference_deadline), "
            "r.registration_deadline, r.group_preference_deadline) > now() "
            "AND COALESCE(GREATEST(r.registration_deadline, r.group_preference_deadline), "
            "r.registration_deadline, r.group_preference_deadline) <= now() + interval '2 days' "
            "AND NOT EXISTS (SELECT 1 FROM group_slot_preferences gp "
            "WHERE gp.round_id = r.id AND gp.group_id = rg.group_id)"
        )
    ).mappings().all()
    for row in leader_rows:
        key = f"availability-reminder:group:{row['round_id']}:{row['group_id']}"
        _insert_event(
            db,
            "GROUP_AVAILABILITY_REMINDER",
            key,
            {"round_id": row["round_id"], "group_id": row["group_id"], "deadline": row["effective_registration_deadline"], "recipient_id": row["account_id"]},
            row["account_id"],
        )
    db.commit()
    return len(lecturer_rows) + len(leader_rows)


def process_round_auto_close(db: Session) -> int:
    """Close registration once a round's end_date has passed."""
    closed = db.execute(
        text(
            "UPDATE rounds SET status = 'REGISTRATION_CLOSED', lecturer_registration_closed_at = now() "
            "WHERE status = 'OPEN_REGISTRATION' AND end_date IS NOT NULL AND end_date < CURRENT_DATE "
            "RETURNING id"
        )
    ).mappings().all()
    for round_row in closed:
        db.execute(
            text(
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) "
                "VALUES (NULL, 'ROUND_TRANSITION', 'round', :entity_id, 'end_date passed', "
                "CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"
            ),
            {
                "entity_id": str(round_row["id"]),
                "before_json": '{"status": "OPEN_REGISTRATION"}',
                "after_json": '{"status": "REGISTRATION_CLOSED"}',
            },
        )
    db.commit()
    return len(closed)


def _insert_event(db: Session, event_type: str, key: str, payload: dict[str, Any], recipient_id: int) -> None:
    import json

    data = json.dumps(payload, default=str)
    db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, :event_type, CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "event_type": event_type, "payload": data, "key": key})
    db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES (:event_type, CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"event_type": event_type, "payload": data, "key": key})
