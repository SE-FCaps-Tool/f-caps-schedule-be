from datetime import UTC, datetime

from app.api_contract import ApiDataEnvelope, success_payload
from app.response_models import TargetProjectProgressionResponse
from app.routes.manager_extensions import _project_detail_payload
from app.routes.target_group_project import _project_progression_payload


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


def test_project_progression_payload_matches_frontend_contract() -> None:
    payload = _project_progression_payload(
        {"project_status": "ACTIVE", "group_id": 12},
        [
            {
                "round_type": "REVIEW_1",
                "outcome": "PASS",
                "remediation_status": None,
                "remediation_deadline": None,
                "remediation_verifier_id": None,
            },
            {
                "round_type": "DEFENSE_1_1",
                "outcome": "LEVEL_2",
                "remediation_status": "OPEN",
                "remediation_deadline": datetime(2026, 8, 30, tzinfo=UTC),
                "remediation_verifier_id": 7,
            },
        ],
    )

    assert payload == {
        "status": "ACTIVE",
        "timeline": [
            {"round": "REVIEW_1", "result": "PASS"},
            {"round": "DEFENSE_1_1", "result": "LEVEL_2"},
        ],
        "remediation": {
            "status": "OPEN",
            "deadline": datetime(2026, 8, 30, tzinfo=UTC),
            "verifier_id": "lec_7",
        },
    }
    assert ApiDataEnvelope[TargetProjectProgressionResponse].model_validate(success_payload(payload))
