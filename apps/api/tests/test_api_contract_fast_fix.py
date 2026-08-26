import pytest
from fastapi import HTTPException

from app.api_contract import external_id, parse_external_id, target_id_fields
from app.routes.manager_extensions import _parse_project_id as _parse_manager_project_id
from app.routes.target_group_project import (
    TargetGroupCreate,
    TargetProjectCreate,
    _parse_group_id,
)
from app.routes.target_group_project import (
    _parse_project_id as _parse_target_project_id,
)
from app.routes.target_round_contract import (
    TargetAvailabilitySubmit,
    TargetInvitationResponse,
    TargetRoundCreate,
)


@pytest.mark.parametrize("value", [123, "123", "grp_123"])
def test_external_id_codec_accepts_legacy_and_prefixed_values(value):
    assert parse_external_id(value, prefix="grp") == 123
    assert external_id(value, "grp") == "grp_123"


def test_external_id_codec_rejects_wrong_prefix_and_malformed_values():
    with pytest.raises(ValueError):
        parse_external_id("prj_123", prefix="grp")
    with pytest.raises(ValueError):
        parse_external_id("grp_bad", prefix="grp")


@pytest.mark.parametrize("value", [28, "28", "grp_28"])
def test_target_group_path_id_accepts_numeric_and_public_forms(value):
    assert _parse_group_id(value) == 28


def test_target_group_path_id_rejects_other_resource_prefix():
    with pytest.raises(HTTPException) as exc_info:
        _parse_group_id("prj_28")
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("parser", [_parse_manager_project_id, _parse_target_project_id])
@pytest.mark.parametrize("value", [104, "104", "prj_104"])
def test_project_path_id_accepts_numeric_and_public_forms(parser, value):
    assert parser(value) == 104


@pytest.mark.parametrize("parser", [_parse_manager_project_id, _parse_target_project_id])
def test_project_path_id_rejects_other_resource_prefix(parser):
    with pytest.raises(HTTPException) as exc_info:
        parser("grp_104")
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["code"] == "VALIDATION_ERROR"


def test_target_id_fields_adapts_sql_mapping_without_mutating_source():
    source = {"id": 7, "group_id": 12, "code": "G-01"}
    result = target_id_fields(source, "grp", "id", "group_id")
    assert result == {"id": "grp_7", "group_id": "grp_12", "code": "G-01"}
    assert source["id"] == 7


def test_target_resource_models_accept_documented_camel_case_payloads():
    group = TargetGroupCreate.model_validate({"code": "G01", "studentIds": ["stu_1"], "leaderId": "stu_1"})
    project = TargetProjectCreate.model_validate({"code": "P01", "nameVi": "Đề tài", "mainSupervisorId": "lec_1"})
    availability = TargetAvailabilitySubmit.model_validate({"preferredLoad": "HIGH", "slots": [{"timeslotId": "ts_1", "available": True}]})
    invitation = TargetInvitationResponse.model_validate({"decision": "ACCEPTED"})
    assert group.student_ids == ["stu_1"]
    assert project.name_vi == "Đề tài"
    assert availability.slots[0].timeslot_id == "ts_1"
    assert invitation.decision == "ACCEPTED"


def test_round_result_owner_contract_rejects_review_round():
    with pytest.raises(ValueError):
        TargetRoundCreate.model_validate({
            "name": "Review", "type": "REVIEW_1", "durationMinutes": 60,
            "reviewerCount": 2, "maxGroupsPerTimeslot": 3,
            "registrationDeadline": "2026-08-09T22:31:00+07:00",
            "groupSelectionMode": False, "resultOwnerMode": True,
            "roomTypes": ["NORMAL"], "days": [{"date": "2026-08-20", "slots": [{"startTime": "08:00", "endTime": "09:00"}]}],
        })
