FIXTURE_VERSION = "seed-v2"

DEMO_PASSWORD = "12345@Abc"


def seed_fixture_v1() -> dict[str, object]:
    accounts = [
        {"email": "admin@gmail.com", "display_name": "Admin", "role": "ADMIN"},
        {"email": "manager@gmail.com", "display_name": "Manager", "role": "MANAGER"},
        {
            "email": "lecturer@gmail.com",
            "display_name": "Lecturer",
            "role": "LECTURER",
            "lecturer_code": "GV01",
        },
    ] + [
        {
            "email": f"student{i}@gmail.com",
            "display_name": f"Student {i}",
            "role": "STUDENT",
            "student_code": f"SV{i:03d}",
        }
        for i in range(1, 6)
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
    }
