from app.domain.seed import FIXTURE_VERSION, seed_fixture_v1


def test_seed_fixture_is_deterministic_and_has_target_shape():
    first = seed_fixture_v1()
    second = seed_fixture_v1()

    assert first == second
    assert first["version"] == FIXTURE_VERSION
    assert first["password"] == "12345@Abc"
    assert first["semester"]["code"] == "SE-2026-2027"
    assert first["major"]["code"] == "SE"

    accounts = first["accounts"]
    assert len(accounts) == 8
    assert [a["email"] for a in accounts if a["role"] == "ADMIN"] == ["admin@gmail.com"]
    assert [a["email"] for a in accounts if a["role"] == "MANAGER"] == ["manager@gmail.com"]
    assert [a["email"] for a in accounts if a["role"] == "LECTURER"] == ["lecturer@gmail.com"]
    assert [a["email"] for a in accounts if a["role"] == "STUDENT"] == [
        f"student{i}@gmail.com" for i in range(1, 6)
    ]

    rooms = first["rooms"]
    assert len(rooms) == 6
    for room_type in ("NORMAL", "SEMINAR", "LAB"):
        matching = [r for r in rooms if r["room_type"] == room_type]
        assert len(matching) == 2
        assert all(r["capacity"] == 12 for r in matching)
