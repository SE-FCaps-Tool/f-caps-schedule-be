from app.domain.seed import FIXTURE_VERSION, seed_fixture_v1


def test_seed_fixture_is_deterministic_and_has_target_shape():
    first = seed_fixture_v1()
    second = seed_fixture_v1()

    assert first == second
    assert first["version"] == FIXTURE_VERSION
    assert len(first["lecturers"]) == 26
    assert len(first["rooms"]) == 4
    assert len(first["groups"]) == 74
    assert len(first["students"]) == 296
    assert all(len(group["members"]) == 4 for group in first["groups"])
    assert [item["email"] for item in first["lecturers"][:2]] == [
        "lecturer1@gmail.com",
        "lecturer2@gmail.com",
    ]
    assert [item["email"] for item in first["students"][:2]] == [
        "student1@gmail.com",
        "student2@gmail.com",
    ]
    assert first["groups"][0]["members"][:2] == [
        {"student_code": "SV001", "role": "LEADER"},
        {"student_code": "SV002", "role": "MEMBER"},
    ]
