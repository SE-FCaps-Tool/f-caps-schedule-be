from app.routes.manager_extensions import _project_detail_payload


def test_project_detail_payload_matches_frontend_contract() -> None:
    payload = _project_detail_payload(
        {
            "id": 104,
            "code": "PRJ-104",
            "name": "Research title",
            "name_vi": "Đề tài nghiên cứu",
            "name_en": "Research title",
            "topic_type": "RESEARCH",
            "status": "ACTIVE",
        },
        [
            {"id": 7, "code": "GV001", "full_name": "Main Supervisor", "supervisor_type": "MAIN"},
            {"id": 8, "code": "GV002", "full_name": "Co Supervisor", "supervisor_type": "CO"},
        ],
        {
            "id": 12,
            "code": "G-12",
            "member_count": 3,
            "leader_id": 21,
            "leader_code": "SV021",
            "leader_full_name": "Group Leader",
        },
    )

    assert payload == {
        "id": "prj_104",
        "code": "PRJ-104",
        "name": "Research title",
        "name_vi": "Đề tài nghiên cứu",
        "name_en": "Research title",
        "topic_type": "RESEARCH",
        "status": "ACTIVE",
        "main_supervisor": {"id": "lec_7", "code": "GV001", "full_name": "Main Supervisor"},
        "co_supervisor": {"id": "lec_8", "code": "GV002", "full_name": "Co Supervisor"},
        "group": {
            "id": "grp_12",
            "code": "G-12",
            "member_count": 3,
            "leader": {"id": "stu_21", "code": "SV021", "full_name": "Group Leader"},
        },
    }
