FIXTURE_VERSION = "seed-v5"

DEMO_PASSWORD = "12345@Abc"


def seed_fixture_v1() -> dict[str, object]:
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
