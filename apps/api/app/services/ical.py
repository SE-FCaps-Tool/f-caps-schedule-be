from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any


def build_ical(sessions: Iterable[dict[str, Any]], *, calendar_name: str) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Capstone Defense Scheduler//EN",
        f"X-WR-CALNAME:{_escape(calendar_name)}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for session in sessions:
        start = _utc(session["start_at"])
        end = _utc(session["end_at"])
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:scheduler-session-{session['id']}@capstone.local",
                f"DTSTAMP:{_utc(datetime.now(UTC)).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:Defense {_escape(session['group_code'])}",
                f"LOCATION:{_escape(session.get('room_code', 'TBA'))}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
