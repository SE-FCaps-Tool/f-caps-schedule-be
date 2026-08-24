import os

FIXTURE_VERSION = "seed-v5"

DEMO_PASSWORD = "12345@Abc"


def seed_fixture_v1() -> dict[str, object]:
    if os.getenv("APP_ENV", "development").strip().lower() == "test":
        return _test_seed_fixture()

    accounts = [
        {"email": "admin@gmail.com", "display_name": "Admin", "role": "ADMIN"},
        {"email": "manager@gmail.com", "display_name": "Manager", "role": "MANAGER"},
        {
            "email": "lecturer@gmail.com",
            "display_name": "Lecturer 1",
            "role": "LECTURER",
            "lecturer_code": "GV01",
        },
        {
            "email": "student1@gmail.com",
            "display_name": "Student 1",
            "role": "STUDENT",
            "student_code": "SV001",
        },
    ]
    return {
        "version": FIXTURE_VERSION,
        "password": DEMO_PASSWORD,
        "semester": {
            "code": "SU26",
            "name": "Summer 2026",
            "start_date": "2026-05-11",
            "end_date": "2026-08-23",
        },
        "major": {"code": "SE", "name": "Software Engineering"},
        "accounts": accounts,
        "rooms": [],
    }


def _test_seed_fixture() -> dict[str, object]:
    """Return the deterministic, data-rich fixture used by integration tests.

    Development/production bootstrap deliberately uses the small current-semester
    fixture above. Tests need stable groups, reviewers, rooms, and availability so
    the API flows can exercise scheduling behavior without importing external data.
    """

    accounts = [
        {"email": "admin@gmail.com", "display_name": "Admin", "role": "ADMIN"},
        {"email": "manager@gmail.com", "display_name": "Manager", "role": "MANAGER"},
    ] + [
        {
            "email": "lecturer@gmail.com" if index == 1 else f"lecturer{index}@gmail.com",
            "display_name": f"Lecturer {index}",
            "role": "LECTURER",
            "lecturer_code": f"GV{index:02d}",
        }
        for index in range(1, 11)
    ] + [
        {
            "email": f"student{index}@gmail.com",
            "display_name": f"Student {index}",
            "role": "STUDENT",
            "student_code": f"SV{index:03d}",
        }
        for index in range(1, 121)
    ] + [
        {
            "email": f"available-student{index}@gmail.com",
            "display_name": f"Available Student {index}",
            "role": "STUDENT",
            "student_code": f"SV{120 + index:03d}",
        }
        for index in range(1, 9)
    ]
    rooms = [
        {
            "code": f"{room_type[:1]}{index:02d}",
            "name": f"{room_type.title()} Room {index}",
            "capacity": 12,
            "room_type": room_type,
        }
        for room_type in ("NORMAL", "SEMINAR", "LAB")
        for index in range(1, 3)
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
                "group_code": f"DEMO-G{index:02d}",
                "project_code": f"DEMO-P{index:02d}",
                "project_title": f"Demo Capstone Project {index}",
                "supervisor_code": f"GV{((index - 1) % 10) + 1:02d}",
                "student_codes": [
                    f"SV{student:03d}"
                    for student in range((index - 1) * 4 + 1, index * 4 + 1)
                ],
            }
            for index in range(1, 31)
        ],
    }
