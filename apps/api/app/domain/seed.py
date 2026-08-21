FIXTURE_VERSION = "seed-v4"

DEMO_PASSWORD = "12345@Abc"


def seed_fixture_v1() -> dict[str, object]:
    accounts = [
        {"email": "admin@gmail.com", "display_name": "Admin", "role": "ADMIN"},
        {"email": "manager@gmail.com", "display_name": "Manager", "role": "MANAGER"},
    ] + [
        {
            "email": "lecturer@gmail.com" if i == 1 else f"lecturer{i}@gmail.com",
            "display_name": f"Lecturer {i}",
            "role": "LECTURER",
            "lecturer_code": f"GV{i:02d}",
        }
        for i in range(1, 11)
    ] + [
        {
            "email": f"student{i}@gmail.com",
            "display_name": f"Student {i}",
            "role": "STUDENT",
            "student_code": f"SV{i:03d}",
        }
        for i in range(1, 121)
    ]
    rooms = [
        {"code": f"{room_type[:1]}{i:02d}", "name": f"{room_type.title()} Room {i}", "capacity": 12, "room_type": room_type}
        for room_type in ("NORMAL", "SEMINAR", "LAB")
        for i in range(1, 3)
    ]
    return {
        "version": FIXTURE_VERSION,
        "password": DEMO_PASSWORD,
        "semester": {
            "code": "SE-2026-2027",
            "name": "Software Engineering 2026–2027",
            "start_date": "2026-05-11",
            "end_date": "2026-08-23",
        },
        "major": {"code": "SE", "name": "Software Engineering"},
        "accounts": accounts,
        "rooms": rooms,
        "demo_round": {
            "name": "DEMO-ROUND-SHARED-SLOT",
            "description": "Demo REVIEW_1 round with one common timeslot for scheduler testing.",
            "type": "REVIEW_1",
            "status": "OPEN_REGISTRATION",
            "reviewer_count": 2,
            "session_duration_minutes": 30,
            "start_date": "2026-08-22",
            "end_date": "2026-08-22",
            "registration_deadline": "2026-08-22T08:00:00+07:00",
            "group_preference_deadline": "2026-08-22T08:00:00+07:00",
            "group_selection_mode": True,
            "h12_sessions_per_part": 4,
            "h12_sessions_per_day": 8,
            "room_types": ["NORMAL", "SEMINAR", "LAB"],
            "timeslot": {
                "day_date": "2026-08-22",
                "start_at": "2026-08-22T09:00:00+07:00",
                "end_at": "2026-08-22T09:30:00+07:00",
                "part": "AM",
            },
        },
        "demo_groups": [
            {
                "group_code": f"DEMO-G{i:02d}",
                "project_code": f"DEMO-P{i:02d}",
                "project_title": f"Demo Capstone Project {i}",
                "supervisor_code": f"GV{((i - 1) % 10) + 1:02d}",
                "student_codes": [f"SV{student:03d}" for student in range((i - 1) * 4 + 1, i * 4 + 1)],
            }
            for i in range(1, 31)
        ],
    }
