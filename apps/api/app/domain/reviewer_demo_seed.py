from datetime import datetime, timedelta

from app.domain.seed import DEMO_PASSWORD, seed_fixture_v1

LECTURER_NAMES = [
    "TriPT9",
    "VuLNS",
    "TaiNT51",
    "NhanDT35",
    "DucDNM2",
    "VanTTN2",
    "PhuongLHK",
    "MinhTTH5",
    "HuongNTC2",
    "LongT5",
    "LamNN15",
    "SangNM18",
    "TamPM",
    "NguyenTT15",
]


def _slug(value: str) -> str:
    return value.lower()


def reviewer_demo_fixture() -> dict[str, object]:
    base = seed_fixture_v1()
    lecturer_accounts = [
        {
            "email": f"{_slug(name)}@gmail.com",
            "display_name": name,
            "role": "LECTURER",
            "lecturer_code": name.upper(),
        }
        for name in LECTURER_NAMES
    ]
    groups: list[dict[str, object]] = []
    student_accounts: list[dict[str, str]] = []
    for group_number in range(1, 45):
        lecturer_index = (group_number - 1) % len(LECTURER_NAMES)
        lecturer_name = LECTURER_NAMES[lecturer_index]
        lecturer_slug = _slug(lecturer_name)
        member_count = 4 + ((group_number * 11 + 1) % 2)
        student_codes: list[str] = []
        for member_number in range(1, member_count + 1):
            student_slug = f"student{lecturer_slug}{group_number:02d}{member_number}"
            student_code = f"R44-{lecturer_slug.upper()}-{group_number:02d}-{member_number}"
            student_accounts.append(
                {
                    "email": f"{student_slug}@gmail.com",
                    "display_name": f"{lecturer_name} Student {group_number:02d}-{member_number}",
                    "role": "STUDENT",
                    "student_code": student_code,
                }
            )
            student_codes.append(student_code)
        groups.append(
            {
                "group_code": f"REVIEW44-G{group_number:02d}",
                "project_code": f"REVIEW44-P{group_number:02d}",
                "project_title": f"Reviewer Pair Demo Project {group_number:02d}",
                "supervisor_code": lecturer_name.upper(),
                "student_codes": student_codes,
                "preferred_slot_index": (group_number - 1) % 8,
            }
        )

    first_slot = datetime.fromisoformat("2026-08-22T09:00:00+07:00")
    timeslots = [
        {
            "day_date": "2026-08-22",
            "start_at": (first_slot + timedelta(minutes=30 * index)).isoformat(),
            "end_at": (first_slot + timedelta(minutes=30 * index + 30)).isoformat(),
            "part": "AM",
        }
        for index in range(8)
    ]
    return {
        "version": "reviewer-demo-v1",
        "password": DEMO_PASSWORD,
        "semester": base["semester"],
        "major": base["major"],
        "accounts": [
            {"email": "admin@gmail.com", "display_name": "Admin", "role": "ADMIN"},
            {"email": "manager@gmail.com", "display_name": "Manager", "role": "MANAGER"},
            *lecturer_accounts,
            *student_accounts,
        ],
        "rooms": base["rooms"],
        "demo_round": {
            "name": "REVIEWER-DEMO-44-PAIRS",
            "description": "44 groups and 44 scheduler-generated Reviewer pairs.",
            "type": "REVIEW_1",
            "status": "OPEN_REGISTRATION",
            "reviewer_count": 2,
            "session_duration_minutes": 30,
            "start_date": "2026-08-22",
            "end_date": "2026-08-22",
            "registration_deadline": "2026-08-22T08:00:00+07:00",
            "group_preference_deadline": "2026-08-22T08:00:00+07:00",
            "group_selection_mode": True,
            "h12_sessions_per_part": 8,
            "h12_sessions_per_day": 8,
            "group_preference_mode": "SINGLE_SLOT",
            "room_types": ["NORMAL", "SEMINAR", "LAB"],
            "timeslots": timeslots,
        },
        "demo_groups": groups,
    }
