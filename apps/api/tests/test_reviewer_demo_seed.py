from app.domain.reviewer_demo_seed import LECTURER_NAMES, reviewer_demo_fixture


def test_reviewer_demo_fixture_has_44_groups_and_88_reviewer_slots():
    fixture = reviewer_demo_fixture()
    lecturers = [account for account in fixture["accounts"] if account["role"] == "LECTURER"]
    students = [account for account in fixture["accounts"] if account["role"] == "STUDENT"]

    assert [account["display_name"] for account in lecturers] == LECTURER_NAMES
    assert len(lecturers) == 14
    assert len(fixture["demo_groups"]) == 44
    assert {len(group["student_codes"]) for group in fixture["demo_groups"]} == {4, 5}
    assert len(students) == sum(len(group["student_codes"]) for group in fixture["demo_groups"])
    assert len(fixture["demo_round"]["timeslots"]) == 8
    assert {group["preferred_slot_index"] for group in fixture["demo_groups"]} == set(range(8))
    assert fixture["demo_round"]["reviewer_count"] == 2
    assert fixture["demo_round"]["name"] == "REVIEWER-DEMO-44-PAIRS"
