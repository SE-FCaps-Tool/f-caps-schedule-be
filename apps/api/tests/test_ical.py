from datetime import UTC, datetime

from app.services.ical import build_ical


def test_ical_uses_utc_values_and_half_open_event_boundaries():
    content = build_ical(
        [
            {
                "id": 7,
                "group_code": "G-07",
                "room_code": "R-01",
                "start_at": datetime(2030, 1, 1, 2, 0, tzinfo=UTC),
                "end_at": datetime(2030, 1, 1, 2, 30, tzinfo=UTC),
            }
        ],
        calendar_name="Capstone Scheduler",
    )
    assert "BEGIN:VCALENDAR" in content
    assert "DTSTART:20300101T020000Z" in content
    assert "DTEND:20300101T023000Z" in content
    assert "SUMMARY:Defense G-07" in content
    assert "X-WR-CALNAME:Capstone Scheduler" in content
