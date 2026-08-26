from app.domain.enums import LecturerSeniorityLevel, TopicType
from app.routes.manager_extensions import ProjectUpdate
from app.routes.master_data import LecturerCreate, LecturerUpdate, ProjectCreate
from app.routes.target_group_project import TargetProjectCreate


def test_topic_type_defaults_to_regular_for_both_project_create_contracts() -> None:
    legacy = ProjectCreate(
        semester_id=1,
        major_id=1,
        code="P001",
        title="A project",
        supervisors=["GV001:MAIN"],
    )
    target = TargetProjectCreate(
        code="P001",
        nameVi="Một đề tài",
        mainSupervisorId="lec_1",
    )

    assert legacy.topic_type is TopicType.REGULAR
    assert target.topic_type is TopicType.REGULAR
    assert target.model_dump(mode="json", by_alias=True)["topicType"] == "REGULAR"


def test_topic_type_accepts_all_supported_values() -> None:
    for value in ("APPLICATION", "RESEARCH", "INTEGRATED", "REGULAR"):
        payload = ProjectCreate(
            semester_id=1,
            major_id=1,
            code="P001",
            title="A project",
            topicType=value,
            supervisors=["GV001:MAIN"],
        )
        assert payload.topic_type.value == value


def test_lecturer_seniority_is_optional_and_explicit_null_is_preserved() -> None:
    create = LecturerCreate(
        lecturerCode="GV001",
        email="gv001@example.com",
        displayName="Lecturer 001",
        password="long-enough-password",
    )
    clear = LecturerUpdate(seniorityLevel=None)
    set_level = LecturerUpdate(seniorityLevel="Senior")

    assert create.seniority_level is None
    assert clear.model_dump(exclude_unset=True) == {"seniority_level": None}
    assert set_level.seniority_level is LecturerSeniorityLevel.SENIOR
    assert set_level.model_dump(mode="json", by_alias=True) == {"seniorityLevel": "Senior"}


def test_project_update_distinguishes_omitted_topic_type_from_update() -> None:
    omitted = ProjectUpdate()
    updated = ProjectUpdate(topicType="RESEARCH")

    assert "topic_type" not in omitted.model_dump(exclude_unset=True)
    assert updated.model_dump(mode="json", by_alias=True)["topicType"] == "RESEARCH"
