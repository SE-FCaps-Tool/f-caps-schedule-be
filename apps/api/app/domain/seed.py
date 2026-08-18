FIXTURE_VERSION = "seed-v1"


def seed_fixture_v1() -> dict[str, object]:
    lecturers = [
        {
            "lecturer_code": f"GV{i:02d}",
            "email": f"lecturer{i}@gmail.com" if i <= 2 else f"gv{i:02d}@scheduler.test",
            "display_name": f"Giảng viên {i:02d}",
        }
        for i in range(1, 27)
    ]
    rooms = [
        {"code": f"R{i:02d}", "name": f"Phòng Defense {i:02d}", "capacity": 12}
        for i in range(1, 5)
    ]
    students = []
    groups = []
    for group_number in range(1, 75):
        members = []
        for member_number in range(1, 5):
            student_number = (group_number - 1) * 4 + member_number
            student_code = f"SV{student_number:03d}"
            students.append(
                {
                    "student_code": student_code,
                    "email": (
                        f"student{student_number}@gmail.com"
                        if student_number <= 2
                        else f"{student_code.lower()}@scheduler.test"
                    ),
                    "display_name": f"Sinh viên {student_number:03d}",
                }
            )
            members.append(
                {
                    "student_code": student_code,
                    "role": "LEADER" if member_number == 1 else "MEMBER",
                }
            )
        supervisor_number = ((group_number - 1) % 26) + 1
        groups.append(
            {
                "code": f"G{group_number:03d}",
                "project_code": f"P{group_number:03d}",
                "title": f"Capstone Project {group_number:03d}",
                "supervisors": [f"GV{supervisor_number:02d}:MAIN"],
                "members": members,
            }
        )
    return {
        "version": FIXTURE_VERSION,
        "semester": {"code": "SE-2026-2027", "name": "Software Engineering 2026–2027"},
        "major": {"code": "SE", "name": "Software Engineering"},
        "lecturers": lecturers,
        "rooms": rooms,
        "students": students,
        "groups": groups,
    }
