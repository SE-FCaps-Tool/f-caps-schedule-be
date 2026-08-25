"""Explicit OpenAPI response models.

The application historically returned raw SQL mapping dictionaries.  That is
fine at runtime, but ``list[dict[str, object]]`` gives FastAPI no field
information and Swagger renders ``additionalProp1``.  These models describe
the public response contract while keeping ``extra='allow'`` during the
transition so older response fields remain backward compatible.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


class ResponseModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TargetResponseModel(ResponseModel):
    model_config = ConfigDict(extra="allow", alias_generator=to_camel, populate_by_name=True)


class LoginResponse(ResponseModel):
    role: str | None = None
    expires_at: datetime | str | None = None
    requires_role_selection: bool = False
    available_roles: list[str] = Field(default_factory=list)
    email: str | None = None
    display_name: str | None = None


class RoleSelectionResponse(ResponseModel):
    available_roles: list[str] = Field(default_factory=list)


class RoleSelectionPayload(BaseModel):
    role: str


class LogoutResponse(ResponseModel):
    status: str


class MeResponse(ResponseModel):
    role: str
    status: str
    account_id: int | None = None
    email: str | None = None
    display_name: str | None = None


class PublicMeResponse(ResponseModel):
    role: str
    status: str


class AuditActorResponse(ResponseModel):
    id: int
    email: str
    display_name: str


class SemesterResponse(ResponseModel):
    id: int
    code: str
    name: str
    note: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    academic_year: str | None = None
    status: Literal["PLANNING", "ACTIVE", "CLOSED", "ARCHIVED"]
    project_count: int = 0
    group_count: int = 0
    round_count: int = 0
    created_at: datetime | None = None
    created_by: AuditActorResponse | None = None
    updated_at: datetime | None = None
    updated_by: AuditActorResponse | None = None


class AccountResponse(ResponseModel):
    id: int
    email: str
    display_name: str
    status: str
    role: str | None = None
    created_at: datetime | None = None


class MajorResponse(ResponseModel):
    id: int
    code: str
    name: str


class StudentResponse(ResponseModel):
    id: int
    student_code: str
    full_name: str | None = None
    display_name: str | None = None
    email: str | None = None


class SupervisorResponse(ResponseModel):
    lecturer_code: str
    display_name: str | None = None
    type: str | None = None


class ProjectGroupSummary(ResponseModel):
    id: int
    code: str
    status: str | None = None


class ProjectResponse(ResponseModel):
    id: int
    code: str
    title: str
    title_vi: str | None = None
    title_en: str | None = None
    status: str | None = None
    semester_id: int | None = None
    semester_code: str | None = None
    major_id: int | None = None
    major_code: str | None = None
    supervisor_count: int | None = None
    supervisors: list[SupervisorResponse] = Field(default_factory=list)


class ProjectMutationResponse(ResponseModel):
    id: int
    code: str
    title: str
    title_vi: str | None = None
    title_en: str | None = None
    status: str | None = None
    semester_id: int | None = None


class ProjectDetailResponse(ProjectResponse):
    group: ProjectGroupSummary | None = None


class GroupMemberResponse(ResponseModel):
    student_id: int
    student_code: str
    display_name: str | None = None
    email: str | None = None
    role: str | None = None
    status: str | None = None


class GroupResponse(ResponseModel):
    id: int
    code: str
    status: str | None = None
    ui_status: str | None = None
    project_id: int | None = None
    project_code: str | None = None
    title: str | None = None
    title_vi: str | None = None
    title_en: str | None = None
    active_member_count: int | None = None
    leader_count: int | None = None
    leader_name: str | None = None


class GroupMutationResponse(ResponseModel):
    id: int
    code: str
    member_count: int | None = None
    status: str | None = None
    project_id: int | None = None
    members: list[GroupMemberResponse] = Field(default_factory=list)


class GroupDetailResponse(GroupResponse):
    members: list[GroupMemberResponse] = Field(default_factory=list)


class GroupOverviewMemberResponse(TargetResponseModel):
    membership_id: int
    student_id: int
    student_code: str
    full_name: str | None = None
    role: str
    status: str
    left_at: datetime | None = None


class GroupOverviewSupervisorResponse(TargetResponseModel):
    id: int
    code: str
    full_name: str | None = None


class GroupOverviewProjectResponse(TargetResponseModel):
    id: int
    code: str
    name: str
    name_vi: str | None = None
    name_en: str | None = None
    status: str
    main_supervisor: GroupOverviewSupervisorResponse | None = None
    co_supervisor: GroupOverviewSupervisorResponse | None = None


class GroupOverviewResultResponse(TargetResponseModel):
    id: int
    outcome: str
    note: str | None = None
    entered_at: datetime
    verify_status: str | None = None


class GroupOverviewRoundResponse(TargetResponseModel):
    round_id: int
    round_type: str
    round_status: str
    session_id: int | None = None
    session_status: str | None = None
    scheduled_at: datetime | None = None
    room_code: str | None = None
    result: GroupOverviewResultResponse | None = None


class GroupOverviewProgressResponse(TargetResponseModel):
    group_status: str
    rounds: list[GroupOverviewRoundResponse] = Field(default_factory=list)


class GroupOverviewRemediationResponse(TargetResponseModel):
    id: int
    status: str
    due_at: datetime
    verifier_lecturer_id: int | None = None
    note: str | None = None
    round_type: str


class GroupOverviewWarningResponse(TargetResponseModel):
    code: str
    message: str


class GroupOverviewResponse(TargetResponseModel):
    id: int
    code: str
    status: str
    semester: dict[str, Any] | None = None
    member_count: int
    leader: GroupOverviewMemberResponse | None = None
    members: list[GroupOverviewMemberResponse] = Field(default_factory=list)
    project: GroupOverviewProjectResponse | None = None
    progress: GroupOverviewProgressResponse
    remediation: GroupOverviewRemediationResponse | None = None
    warnings: list[GroupOverviewWarningResponse] = Field(default_factory=list)


class LecturerResponse(ResponseModel):
    id: int
    lecturer_code: str
    account_id: int | None = None
    email: str | None = None
    display_name: str | None = None
    account_status: str | None = None
    conflicts: list[ConflictItem] = Field(default_factory=list)


class ConflictItem(ResponseModel):
    project_id: int
    reason: str | None = None


class RoomResponse(ResponseModel):
    id: int
    code: str
    name: str
    capacity: int
    active: bool = True
    room_type: str = "NORMAL"
    type: str = "NORMAL"
    status: str = "ACTIVE"

    @model_validator(mode="before")
    @classmethod
    def _fill_fe_contract_aliases(cls, data: Any) -> Any:
        # FE (rooms-page.tsx) filters on `type`/`status`; the DB and route layer
        # use `room_type`/`active` (docs/be-checklist-open-questions.md A4).
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("type", data.get("room_type"))
            if "status" not in data and "active" in data:
                data["status"] = "ACTIVE" if data["active"] else "INACTIVE"
        return data


class AvailableRoomResponse(RoomResponse):
    available: bool = True


class RoomSuggestionResponse(ResponseModel):
    session_id: int
    room_id: int
    room_code: str | None = None
    room_type: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None


class RoomSuggestionsResponse(ResponseModel):
    suggestions: list[RoomSuggestionResponse] = Field(default_factory=list)


class RoomAssignmentResponse(ResponseModel):
    session_id: int
    room_id: int
    changed: bool = True
    start_at: datetime | None = None
    end_at: datetime | None = None


class RoomSuggestionApplyResponse(ResponseModel):
    round_id: int
    changed_count: int = 0
    unchanged_count: int = 0
    assignments: list[dict[str, int]] = Field(default_factory=list)


class RoomReadinessResponse(ResponseModel):
    readiness: str = "READY"
    missing_sessions: list[int] = Field(default_factory=list)


class RoundResponse(ResponseModel):
    id: int
    semester_id: int
    name: str | None = None
    description: str | None = None
    type: str
    status: str
    reviewer_count: int
    result_owner_mode: bool = False
    group_selection_mode: bool = False
    session_duration_minutes: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    registration_deadline: datetime | None = None
    group_preference_deadline: datetime | None = None
    h12_sessions_per_part: int | None = None
    h12_sessions_per_day: int | None = None
    h12_semester_quota: int | None = None
    max_groups_per_timeslot: int | None = None
    max_minutes_per_part: int | None = None
    max_minutes_per_day: int | None = None
    timeframe_id: int | None = None
    timeframe_version_id: int | None = None
    soft_weights: dict[str, int] = Field(default_factory=dict)
    room_types: list[str] = Field(default_factory=list)


class RoundResourceResponse(ResponseModel):
    round_id: int
    groups: int
    timeslots: int
    rooms: int
    room_types: list[str] = Field(default_factory=list)


class AvailabilityWriteResponse(ResponseModel):
    round_id: int
    lecturer_id: int | None = None
    group_id: int | None = None
    selected_count: int
    total_slots: int
    source: str


class InvitationCreateResponse(ResponseModel):
    round_id: int
    invited_count: int


class DropoutResponse(ResponseModel):
    group_id: int
    student_id: int
    status: str
    warning: str


class LeaderChangeResponse(ResponseModel):
    group_id: int
    leader_student_id: int


class ConflictResponse(ResponseModel):
    id: int
    lecturer_id: int
    project_id: int


class InvitationActionResponse(ResponseModel):
    round_id: int
    lecturer_id: int
    response: str


class AccountRoleResponse(ResponseModel):
    id: int
    role: str
    status: str | None = None


class RoundDayResponse(ResponseModel):
    id: int
    day_date: date
    timeslot_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    part: str | None = None
    active: bool | None = None


class RoundDetailResponse(RoundResponse):
    semester_code: str | None = None
    semester_name: str | None = None
    effective_start_date: date | None = None
    effective_end_date: date | None = None
    group_count: int | None = None
    room_count: int | None = None
    active_timeslot_count: int | None = None
    days: list[RoundDayResponse] = Field(default_factory=list)


class RoundDetailSlotContractResponse(ResponseModel):
    id: str
    start_time: str = Field(alias="startTime")
    end_time: str = Field(alias="endTime")


class RoundDetailDayContractResponse(ResponseModel):
    date: date
    slots: list[RoundDetailSlotContractResponse] = Field(default_factory=list)


class RoundDetailContractResponse(ResponseModel):
    id: str
    semester_id: str = Field(alias="semesterId")
    name: str | None = None
    type: str
    status: str
    description: str | None = None
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    duration_minutes: int = Field(alias="durationMinutes")
    reviewer_count: int = Field(alias="reviewerCount")
    max_groups_per_timeslot: int | None = Field(default=None, alias="maxGroupsPerTimeslot")
    registration_deadline: datetime | None = Field(default=None, alias="registrationDeadline")
    group_selection_mode: bool = Field(alias="groupSelectionMode")
    group_preference_deadline: datetime | None = Field(default=None, alias="groupPreferenceDeadline")
    result_owner_mode: bool = Field(alias="resultOwnerMode")
    room_types: list[str] = Field(default_factory=list, alias="roomTypes")
    timeframe_id: str | None = Field(default=None, alias="timeframeId")
    timeframe_version_id: str | None = Field(default=None, alias="timeframeVersionId")
    committee_count: int = Field(default=0, alias="committeeCount")
    days: list[RoundDetailDayContractResponse] = Field(default_factory=list)


class RoundDetailEnvelopeResponse(ResponseModel):
    data: RoundDetailContractResponse


class TimeslotResponse(ResponseModel):
    id: int
    round_day_id: int
    start_at: datetime
    end_at: datetime
    part: str | None = None
    active: bool = True


class InvitationResponse(ResponseModel):
    round_id: int
    lecturer_id: int
    lecturer_code: str
    display_name: str | None = None
    email: str | None = None
    status: str
    response_reason: str | None = None
    responded_at: datetime | None = None
    available_slot_count: int | None = None
    load_preference: str | None = None


class RoundGroupResponse(ResponseModel):
    group_id: int
    group_code: str
    status: str | None = None
    ui_status: str | None = None
    project_code: str | None = None
    title: str | None = None
    active_member_count: int | None = None
    leader_name: str | None = None
    selected_slot_count: int | None = None


class QuotaResponse(ResponseModel):
    semester_id: int | None = None
    lecturer_id: int
    lecturer_code: str | None = None
    display_name: str | None = None
    quota: int
    used: int | None = None
    updated_at: datetime | None = None


class SessionResponse(ResponseModel):
    id: int
    assignment_id: int | None = None
    version_id: int | None = None
    schedule_version_id: int | None = None
    round_id: int | None = None
    group_id: int | None = None
    group_code: str | None = None
    project_code: str | None = None
    timeslot_id: int | None = None
    room_id: int | None = None
    room_code: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    status: str | None = None
    council_id: int | None = None
    council_members: list[dict[str, Any]] = Field(default_factory=list)
    reviewers: list[ReviewerSummary] | None = None


class ReviewerSummary(ResponseModel):
    id: int
    code: str
    name: str | None = None


class CouncilMemberResponse(ResponseModel):
    lecturer_id: int
    assignment: str = "REVIEWER"
    is_result_owner: bool = False
    snapshot_name: str | None = None


class CouncilResponse(ResponseModel):
    id: int
    round_id: int
    supersedes_council_id: int | None = None
    sealed_at: datetime | None = None
    members: list[CouncilMemberResponse] = Field(default_factory=list)


class RescheduleRequestResponse(ResponseModel):
    id: int
    session_id: int
    requested_by: int | None = None
    requester_name: str | None = None
    reason: str | None = None
    status: str
    reviewed_by: int | None = None
    created_at: datetime | None = None
    reviewed_at: datetime | None = None
    group_id: int | None = None
    group_code: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    room_code: str | None = None


class ResultResponse(ResponseModel):
    id: int
    session_id: int
    group_id: int | None = None
    group_code: str | None = None
    round_type: str | None = None
    outcome: str | None = None
    note: str | None = None
    entered_at: datetime | None = None
    verify_status: str | None = None
    remediation_due_at: datetime | None = None
    verifier_lecturer_id: int | None = None


class VersionSummaryResponse(ResponseModel):
    version_id: int | None = None
    id: int | None = None
    round_id: int | None = None
    version_no: int | None = None
    status: str | None = None
    ui_status: str | None = None
    is_active: bool | None = None
    solver_status: str | None = None
    total_score: float | None = None
    soft_scores: dict[str, float] = Field(default_factory=dict)
    random_seed: int | None = None
    created_at: datetime | None = None
    activated_at: datetime | None = None
    type: str | None = None
    semester_id: int | None = None
    semester_code: str | None = None
    generated_at: datetime | None = None
    objective_profile: str | None = None
    objective_label: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class VersionDetailResponse(VersionSummaryResponse):
    sessions: list[SessionResponse] = Field(default_factory=list)
    assignments: list[dict[str, Any]] = Field(default_factory=list)


class DashboardSemesterResponse(ResponseModel):
    id: int
    code: str
    name: str
    status: Literal["PLANNING", "ACTIVE", "CLOSED", "ARCHIVED"]


class DashboardResponse(ResponseModel):
    current_semester: DashboardSemesterResponse | None = None
    totals: dict[str, int] = Field(default_factory=dict)
    availability: dict[str, int] = Field(default_factory=dict)
    groups: dict[str, int] = Field(default_factory=dict)
    pending_reschedule_requests: int = 0
    changes: int = 0
    version: VersionSummaryResponse | None = None
    lecturer_load: list[DashboardLecturerLoadResponse] = Field(default_factory=list)
    attention_groups: list[AttentionGroupResponse] = Field(default_factory=list)
    attention: dict[str, int] = Field(default_factory=dict)


class ReportEnvelope(ResponseModel):
    round_id: int | None = None
    version: VersionSummaryResponse | None = None
    rows: list[dict[str, Any]] = Field(default_factory=list)


class LecturerLoadResponse(ResponseModel):
    lecturer_id: int
    lecturer_code: str
    display_name: str | None = None
    session_count: int = 0
    quota: int | None = None
    quota_percent: float | None = None


class DashboardLecturerLoadResponse(ResponseModel):
    id: int
    lecturer_code: str
    display_name: str | None = None
    session_count: int = 0


class AttentionGroupResponse(ResponseModel):
    id: int
    code: str
    status: str


class QualityRowResponse(ResponseModel):
    id: int
    code: str
    active_members: int = 0
    leaders: int = 0


class RemediationReportRowResponse(ResponseModel):
    id: int
    group_id: int
    group_code: str | None = None
    due_at: datetime | None = None
    status: str
    verifier_lecturer_id: int | None = None


class OutcomeRowResponse(ResponseModel):
    type: str
    outcome: str | None = None
    count: int = 0


class LecturerLoadReportResponse(ResponseModel):
    round_id: int | None = None
    version: VersionSummaryResponse | None = None
    rows: list[LecturerLoadResponse] = Field(default_factory=list)


class QualityReportResponse(ResponseModel):
    version: VersionSummaryResponse | None = None
    rows: list[QualityRowResponse] = Field(default_factory=list)


class RemediationReportResponse(ResponseModel):
    round_id: int | None = None
    version: VersionSummaryResponse | None = None
    rows: list[RemediationReportRowResponse] = Field(default_factory=list)


class OutcomesReportResponse(ResponseModel):
    round_id: int | None = None
    version: VersionSummaryResponse | None = None
    rows: list[OutcomeRowResponse] = Field(default_factory=list)


class GroupProgressResponse(ResponseModel):
    group_id: int
    group_code: str
    project_name: str | None = None
    group_status: str | None = None
    review_1: str | None = None
    review_2: str | None = None
    review_3: str | None = None
    defense_1: str | None = None
    defense_2: str | None = None
    result_verifier_lecturer_id: int | None = None
    remediation_status: str | None = None
    remediation_due_at: datetime | None = None
    remediation_verifier_lecturer_id: int | None = None


class ImportResponse(ResponseModel):
    created: int
    skipped: int
    errors: list[dict[str, Any]] = Field(default_factory=list)


class LecturerImportResponse(ImportResponse):
    accounts: list[dict[str, Any]] = Field(default_factory=list)


class UnscheduledReportResponse(ResponseModel):
    round_id: int
    generated_at: datetime
    versions: list[dict[str, Any]] = Field(default_factory=list)


class NotificationResponse(ResponseModel):
    id: int
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str
    sent_at: datetime | None = None
    created_at: datetime | None = None


class NotificationRetryResponse(ResponseModel):
    id: int
    status: str
    dedupe_key: str | None = None


class PersonalScheduleResponse(ResponseModel):
    version: VersionSummaryResponse | None = None
    generated_at: datetime
    sessions: list[SessionResponse] = Field(default_factory=list)


class ActionResponse(ResponseModel):
    id: int | None = None
    status: str | None = None
    round_id: int | None = None
    group_id: int | None = None
    lecturer_id: int | None = None
    student_id: int | None = None
    version_id: int | None = None
    source_version_id: int | None = None
    session_id: int | None = None
    result_owner_id: int | None = None
    timeslot_id: int | None = None
    active: bool | None = None
    response: str | None = None
    count: int | None = None
    invited: int | None = None
    responded: int | None = None
    lecturer_availability: int | None = None
    group_availability: int | None = None
    resent: bool | None = None
    deleted: bool | None = None
    role: str | None = None
    project_id: int | None = None
    leader_student_id: int | None = None
    warning: str | None = None
    invited_count: int | None = None
    selected_count: int | None = None
    total_slots: int | None = None
    source: str | None = None
    groups: int | None = None
    timeslots: int | None = None
    rooms: int | None = None
    makeup_of_session_id: int | None = None


class TargetAuditActorResponse(TargetResponseModel):
    id: int
    email: str
    display_name: str


class TargetSemesterResponse(TargetResponseModel):
    id: int
    code: str
    name: str
    note: str | None
    start_date: date | None
    end_date: date | None
    academic_year: str | None
    status: Literal["PLANNING", "ACTIVE", "CLOSED", "ARCHIVED"]
    project_count: int
    group_count: int
    round_count: int
    created_at: datetime | None
    created_by: TargetAuditActorResponse | None
    updated_at: datetime | None
    updated_by: TargetAuditActorResponse | None


class TargetStudentResponse(TargetResponseModel):
    id: int
    student_code: str
    full_name: str | None
    email: str | None


class TargetConflictItemResponse(TargetResponseModel):
    project_id: int
    reason: str | None


class TargetLecturerResponse(TargetResponseModel):
    id: int
    lecturer_code: str
    account_id: int
    email: str
    display_name: str
    account_status: str
    conflicts: list[TargetConflictItemResponse]


class TargetRoomResponse(TargetResponseModel):
    id: int
    code: str
    name: str
    capacity: int
    active: bool
    room_type: str


class TargetPersonSummaryResponse(TargetResponseModel):
    id: str
    code: str
    full_name: str | None


class TargetProjectGroupSummaryResponse(TargetResponseModel):
    id: str
    code: str


class TargetProjectListItemResponse(TargetResponseModel):
    id: str
    code: str
    name: str
    name_vi: str
    name_en: str | None
    status: str
    main_supervisor: TargetPersonSummaryResponse | None
    co_supervisor: TargetPersonSummaryResponse | None
    group: TargetProjectGroupSummaryResponse | None


class TargetWarningResponse(TargetResponseModel):
    code: str
    message: str


class TargetGroupProjectSummaryResponse(TargetResponseModel):
    id: str
    code: str
    name: str
    name_vi: str
    name_en: str | None
    status: str


class TargetGroupListItemResponse(TargetResponseModel):
    id: str
    code: str
    status: str
    member_count: int
    leader: TargetPersonSummaryResponse | None
    project: TargetGroupProjectSummaryResponse | None
    warnings: list[TargetWarningResponse]


class TargetGroupCreateResponse(TargetResponseModel):
    id: str
    code: str
    status: str


class TargetGroupMemberResponse(TargetResponseModel):
    membership_id: str
    student_id: str
    student_code: str
    display_name: str | None
    email: str | None
    role: str
    status: str


class TargetLeaderChangeResponse(TargetResponseModel):
    group_id: int
    leader_student_id: int


class TargetGroupLeaveResponse(TargetResponseModel):
    group_id: str
    membership_id: str
    status: str
    member_count: int
    leader_id: str | None


class TargetGroupProjectAssignmentResponse(TargetResponseModel):
    id: str | int
    code: str
    status: str
    project_id: str | int | None


class TargetProjectCreateResponse(TargetResponseModel):
    id: str
    code: str
    name_vi: str
    name_en: str | None
    status: str


class TargetProjectProgressionResponse(TargetResponseModel):
    project_id: int
    code: str
    title: str
    title_vi: str | None
    title_en: str | None
    project_status: str
    group_id: int | None
    group_status: str | None


class TargetProjectResultResponse(TargetResponseModel):
    id: int
    session_id: int
    round_type: str
    outcome: str | None
    note: str | None
    entered_at: datetime | None
    verify_status: str | None
    remediation_due_at: datetime | None


class TargetRoundResponse(TargetResponseModel):
    id: int
    semester_id: int
    name: str | None
    description: str | None
    type: str
    status: str
    reviewer_count: int
    result_owner_mode: bool
    group_selection_mode: bool
    session_duration_minutes: int | None
    start_date: date | None
    end_date: date | None
    registration_deadline: datetime | None
    group_preference_deadline: datetime | None
    h12_sessions_per_part: int | None
    h12_sessions_per_day: int | None
    h12_semester_quota: int | None
    max_groups_per_timeslot: int | None
    max_minutes_per_part: int | None
    max_minutes_per_day: int | None
    timeframe_id: int | None
    timeframe_version_id: int | None
    soft_weights: dict[str, int]
    room_types: list[str]


class TargetEligibilityChecksResponse(TargetResponseModel):
    has_group: bool
    has_active_leader: bool
    has_main_supervisor: bool
    progression_allowed: bool


class TargetEligibleProjectResponse(TargetResponseModel):
    project_id: str
    group_id: str | None
    eligible: bool
    checks: TargetEligibilityChecksResponse
    blocking_reasons: list[str]
    warnings: list[TargetWarningResponse]


class TargetRegistrationSummaryResponse(TargetResponseModel):
    invited: int
    responded: int
    lecturer_availability: int
    group_availability: int


class TargetUnusableCommitteeResponse(TargetResponseModel):
    committee_id: int
    code: str
    missing_lecturer_ids: list[int]


class TargetSchedulingReadinessResponse(TargetResponseModel):
    ready: bool
    blockers: list[str]
    unusable_committees: list[TargetUnusableCommitteeResponse]
    id: int
    status: str
    groups: int
    timeslots: int
    accepted_invitations: int


class TargetRoundTransitionResponse(TargetResponseModel):
    round_id: int
    status: str


class TargetAvailabilityRoundResponse(TargetResponseModel):
    id: int
    type: str
    status: str
    group_selection_mode: bool
    registration_deadline: datetime | None
    group_preference_deadline: datetime | None


class TargetAvailabilityTimeslotResponse(TargetResponseModel):
    id: int
    start_at: datetime
    end_at: datetime
    day_date: date


class TargetAvailabilityGroupResponse(TargetResponseModel):
    id: int
    code: str


class TargetLecturerAvailabilitySelectionResponse(TargetResponseModel):
    lecturer_id: int
    timeslot_id: int
    state: str
    load_preference: str
    source: str


class TargetGroupAvailabilitySelectionResponse(TargetResponseModel):
    group_id: int
    timeslot_id: int
    selected: bool
    source: str


class TargetAvailabilityResponse(TargetResponseModel):
    round: TargetAvailabilityRoundResponse
    timeslots: list[TargetAvailabilityTimeslotResponse]
    lecturer_id: int | None = None
    selected_timeslot_ids: list[int] = Field(default_factory=list)
    groups: list[TargetAvailabilityGroupResponse] = Field(default_factory=list)
    selected_by_group: dict[int, list[int]] | list[TargetGroupAvailabilitySelectionResponse] | None = None
    selected_by_lecturer: list[TargetLecturerAvailabilitySelectionResponse] = Field(default_factory=list)


class TargetLecturerAvailabilityWriteResponse(TargetResponseModel):
    round_id: int
    lecturer_id: int
    selected_count: int
    total_slots: int
    source: str


class TargetGroupAvailabilityWriteResponse(TargetResponseModel):
    round_id: int
    group_id: int
    selected_count: int
    total_slots: int
    source: str


class TargetInvitationDecisionResponse(TargetResponseModel):
    round_id: int
    lecturer_id: int
    response: str


class TargetInvitationCreateResponse(TargetResponseModel):
    round_id: str
    invited_count: int


class TargetInvitationReminderResponse(TargetResponseModel):
    round_id: int
    lecturer_id: int
    status: str
    resent: bool


class TargetGroupPreferenceTimeslotResponse(TargetResponseModel):
    timeslot_id: int
    start_at: datetime
    end_at: datetime
    selected: bool | None
    source: str | None


class TargetGroupPreferencesResponse(TargetResponseModel):
    round_id: int
    group_id: int
    timeslots: list[TargetGroupPreferenceTimeslotResponse]


class TargetPortalInvitationRoundResponse(TargetResponseModel):
    id: str
    name: str
    type: str
    registration_deadline: datetime | None


class TargetPortalInvitationResponse(TargetResponseModel):
    id: str
    round: TargetPortalInvitationRoundResponse
    status: str
    responded_at: datetime | None


class TargetLecturerPortalSessionResponse(TargetResponseModel):
    id: int
    round_id: int
    start_at: datetime
    end_at: datetime
    status: str
    group_id: int
    group_code: str
    project_code: str
    room_code: str | None
    round_type: str


class TargetLeaderPortalSessionResponse(TargetLecturerPortalSessionResponse):
    room_id: int | None


class TargetPortalProjectMemberResponse(TargetResponseModel):
    id: int
    code: str
    name: str | None
    role: str
    status: str


class TargetPortalProjectLeaderResponse(TargetResponseModel):
    id: int
    code: str
    name: str | None


class TargetPortalProjectGroupResponse(TargetResponseModel):
    id: int
    code: str
    member_count: int
    leader: TargetPortalProjectLeaderResponse | None
    members: list[TargetPortalProjectMemberResponse]


class TargetSupervisedProjectResponse(TargetResponseModel):
    id: int
    code: str
    title: str
    title_vi: str | None
    title_en: str | None
    status: str
    semester_id: int
    semester_code: str
    supervisor_type: str
    group: TargetPortalProjectGroupResponse | None


class TargetPortalRemediationResponse(TargetResponseModel):
    id: int
    group_id: int
    group_code: str
    status: str
    due_at: datetime
    verifier_lecturer_id: int | None
    note: str | None
    round_type: str


class TargetLeaderDashboardGroupResponse(TargetResponseModel):
    id: str
    code: str
    member_count: int
    max_members: int


class TargetLeaderDashboardProjectResponse(TargetResponseModel):
    id: str
    code: str
    title_vi: str
    title_en: str | None
    status: str


class TargetLeaderDashboardSupervisorResponse(TargetResponseModel):
    id: str
    name: str


class TargetLeaderDashboardRoundResponse(TargetResponseModel):
    id: str
    name: str
    type: str
    status: str


class TargetLeaderDashboardSessionResponse(TargetResponseModel):
    id: str
    date: str
    start_time: str
    end_time: str
    room: str | None


class TargetLeaderDashboardResultResponse(TargetResponseModel):
    round_type: str
    kind: str
    value: str
    date: str


class TargetLeaderDashboardRemediationResponse(TargetResponseModel):
    deadline: datetime
    status: str


class TargetLeaderDashboardResponse(TargetResponseModel):
    group: TargetLeaderDashboardGroupResponse | None
    project: TargetLeaderDashboardProjectResponse | None
    main_supervisor: TargetLeaderDashboardSupervisorResponse | None
    co_supervisor: TargetLeaderDashboardSupervisorResponse | None
    current_round: TargetLeaderDashboardRoundResponse | None
    preference_status: str | None
    deadline: datetime | None
    upcoming_session: TargetLeaderDashboardSessionResponse | None
    latest_result: TargetLeaderDashboardResultResponse | None
    remediation: TargetLeaderDashboardRemediationResponse | None


class TargetScheduleDiscardResponse(TargetResponseModel):
    id: int
    deleted: bool


class TargetPublishBlockerResponse(TargetResponseModel):
    code: str
    message: str
    room_id: int | None = None
    session_id: int | None = None
    round_id: int | None = None
    schedule_version_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    round_type: str | None = None
    version_status: str | None = None


class TargetPublishReadinessResponse(TargetResponseModel):
    ready: bool
    version_id: int | None
    blockers: list[TargetPublishBlockerResponse]


class TargetPublishResponse(TargetResponseModel):
    round_id: int
    version_id: int
    status: str
    recipient_count: int


class TargetControlledChangeResponse(TargetResponseModel):
    change_kind: str
    schedule_version_id: int
    replacement_version_id: int | None
    session_id: int
    status: str
    before_council_id: int | None
    after_council_id: int | None
    version_id: int
    source_version_id: int


class TargetEntityStatusResponse(TargetResponseModel):
    id: int
    status: str


class TargetGroupProgressResponse(TargetResponseModel):
    group_id: int
    group_code: str
    project_name: str
    group_status: str
    review_1_1: str | None
    review_1: str | None
    review_2_1: str | None
    review_2: str | None
    defense_1_1: str | None
    review_3: str | None
    defense_1_2: str | None
    defense_1: str | None
    defense_2: str | None
    result_verifier_lecturer_id: int | None
    remediation_status: str | None
    remediation_due_at: datetime | None
    remediation_verifier_lecturer_id: int | None


class TargetRemediationResponse(TargetResponseModel):
    id: int
    group_id: int
    group_code: str
    status: str
    ui_status: str
    due_at: datetime
    verifier_lecturer_id: int | None
    note: str | None
    round_type: str


class AuditResponse(ResponseModel):
    id: int
    actor_id: int | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    reason: str | None = None
    before_json: Any = None
    after_json: Any = None
    occurred_at: datetime | None = None


class MyRoundResponse(ResponseModel):
    id: int
    round_id: int | None = None
    semester_id: int | None = None
    semester_code: str | None = None
    type: str | None = None
    status: str | None = None
    invitation_status: str | None = None


class MyInvitationResponse(ResponseModel):
    round_id: int
    lecturer_id: int | None = None
    lecturer_code: str | None = None
    status: str | None = None
    type: str | None = None


class ReplacementSuggestionResponse(ResponseModel):
    timeslot_id: int
    room_id: int | None = None
    reviewer_ids: list[int] = Field(default_factory=list)
    replaces: list[int] = Field(default_factory=list)


class RemediationResponse(ResponseModel):
    id: int
    group_id: int
    group_code: str | None = None
    status: str
    ui_status: str | None = None
    due_at: datetime | None = None
    verifier_lecturer_id: int | None = None
    note: str | None = None
    round_type: str | None = None


class RegistrationResponse(ResponseModel):
    invited: int = 0
    responded: int = 0
    lecturer_availability: int = 0
    group_availability: int = 0


class AvailabilityResponse(ResponseModel):
    round_id: int | None = None
    lecturer_id: int | None = None
    group_id: int | None = None
    selected_timeslot_ids: list[int] = Field(default_factory=list)
    load_preference: str | None = None


class MyAvailabilityResponse(ResponseModel):
    round: dict[str, Any] = Field(default_factory=dict)
    timeslots: list[dict[str, Any]] = Field(default_factory=list)
    lecturer_id: int | None = None
    selected_timeslot_ids: list[int] = Field(default_factory=list)
    groups: list[dict[str, Any]] = Field(default_factory=list)
    selected_by_group: Any = None
    selected_by_lecturer: list[dict[str, Any]] = Field(default_factory=list)


class ResultDetailResponse(ResponseModel):
    session_id: int
    round_type: str | None = None
    group_status: str | None = None
    result: Any = None


class ResultWriteResponse(ResponseModel):
    id: int
    session_id: int
    outcome: str | None = None
    group_status: str | None = None


class CompareResponse(ResponseModel):
    version_a: Any = None
    version_b: Any = None
    changed_sessions: list[dict[str, Any]] = Field(default_factory=list)


class ScheduleRunResponse(ResponseModel):
    version_id: int
    status: str
    scheduled_count: int = 0
    unscheduled: list[dict[str, Any]] = Field(default_factory=list)
    soft_scores: dict[str, Any] = Field(default_factory=dict)
    objective_profile: str | None = None
    objective_label: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    versions: list[dict[str, Any]] = Field(default_factory=list)


class PublishResponse(ResponseModel):
    round_id: int
    version_id: int
    status: str
    recipient_count: int = 0


class SessionEditResponse(ResponseModel):
    session_id: int
    assignment_id: int | None = None
    version_id: int
    status: str


class ControlledChangeResponse(ResponseModel):
    change_kind: str = "VERSION_REPLACED"
    schedule_version_id: int
    replacement_version_id: int | None = None
    session_id: int
    status: str
    before_council_id: int | None = None
    after_council_id: int | None = None
    # Deprecated compatibility aliases retained for older clients.
    version_id: int | None = None
    source_version_id: int | None = None


class ResultOwnerResponse(ResponseModel):
    version_id: int
    session_id: int
    result_owner_id: int


class HealthResponse(ResponseModel):
    status: str
    service: str | None = None


class SeedFixtureResponse(ResponseModel):
    fixture: str | None = None
    counts: dict[str, Any] = Field(default_factory=dict)


class RoundDayCreateResponse(ResponseModel):
    round_id: int
    day_id: int
    timeslot_ids: list[int] = Field(default_factory=list)


class TimeframeRevisionResponse(ResponseModel):
    id: int
    timeframe_id: int | None = Field(default=None, alias="timeframeId")
    version_number: int = Field(alias="versionNumber")
    status: str
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    block_duration_minutes: int | None = Field(alias="blockDurationMinutes")
    group_duration_minutes: int = Field(alias="groupDurationMinutes")
    break_between_blocks_minutes: int | None = Field(alias="breakBetweenBlocksMinutes")
    manual_timelines: list[TimeframeManualTimelineResponse] | None = Field(
        default=None,
        alias="manualTimelines",
    )
    break_windows: list[TimeframeBreakWindowResponse] = Field(
        default_factory=list,
        alias="breakWindows",
    )
    change_reason: str | None = Field(default=None, alias="changeReason")
    created_by: int | None = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")


class TimeframeGroupSlotResponse(ResponseModel):
    sequence_number: int = Field(alias="sequenceNumber")
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")


class TimeframeManualTimelineResponse(ResponseModel):
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    groups_per_slot: int = Field(alias="groupsPerSlot")


class TimeframeBreakWindowResponse(ResponseModel):
    name: str
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")


class TimeframeBlockResponse(ResponseModel):
    sequence_number: int = Field(alias="sequenceNumber")
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    duration_minutes: int = Field(alias="durationMinutes")
    groups_per_block: int = Field(alias="groupsPerBlock")
    group_duration_minutes: int = Field(alias="groupDurationMinutes")
    group_slots: list[TimeframeGroupSlotResponse] = Field(alias="groupSlots")


class TimeframeResponse(ResponseModel):
    id: int
    name: str
    type: str
    archived_at: datetime | None = Field(default=None, alias="archivedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    version: dict[str, Any]
    revisions: list[TimeframeRevisionResponse] = Field(default_factory=list)
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    block_duration_minutes: int | None = Field(alias="blockDurationMinutes")
    group_duration_minutes: int = Field(alias="groupDurationMinutes")
    break_between_blocks_minutes: int | None = Field(alias="breakBetweenBlocksMinutes")
    manual_timelines: list[TimeframeManualTimelineResponse] | None = Field(
        default=None,
        alias="manualTimelines",
    )
    break_windows: list[TimeframeBreakWindowResponse] = Field(
        default_factory=list,
        alias="breakWindows",
    )
    blocks_per_day: int = Field(alias="blocksPerDay")
    groups_per_block: int | None = Field(alias="groupsPerBlock")
    capacity_per_day: int = Field(alias="capacityPerDay")
    unused_minutes: int = Field(alias="unusedMinutes")
    break_window_minutes: int = Field(alias="breakWindowMinutes")
    applied_block_break_minutes: int = Field(alias="appliedBlockBreakMinutes")
    total_break_minutes: int = Field(alias="totalBreakMinutes")
    blocks: list[TimeframeBlockResponse] = Field(default_factory=list)


class TimeframeEnvelopeResponse(ResponseModel):
    data: TimeframeResponse


class TimeframeListEnvelopeResponse(ResponseModel):
    data: list[TimeframeResponse] = Field(default_factory=list)
    meta: dict[str, int]


class TimeframePreviewResponse(ResponseModel):
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    block_duration_minutes: int | None = Field(alias="blockDurationMinutes")
    group_duration_minutes: int = Field(alias="groupDurationMinutes")
    break_between_blocks_minutes: int | None = Field(alias="breakBetweenBlocksMinutes")
    manual_timelines: list[TimeframeManualTimelineResponse] | None = Field(
        default=None,
        alias="manualTimelines",
    )
    break_windows: list[TimeframeBreakWindowResponse] = Field(
        default_factory=list,
        alias="breakWindows",
    )
    blocks_per_day: int = Field(alias="blocksPerDay")
    groups_per_block: int | None = Field(alias="groupsPerBlock")
    capacity_per_day: int = Field(alias="capacityPerDay")
    unused_minutes: int = Field(alias="unusedMinutes")
    break_window_minutes: int = Field(alias="breakWindowMinutes")
    applied_block_break_minutes: int = Field(alias="appliedBlockBreakMinutes")
    total_break_minutes: int = Field(alias="totalBreakMinutes")
    blocks: list[TimeframeBlockResponse] = Field(default_factory=list)


class TimeframePreviewEnvelopeResponse(ResponseModel):
    data: TimeframePreviewResponse


class CommitteeMemberResponse(ResponseModel):
    lecturer_id: int = Field(alias="lecturerId")
    lecturer_code: str | None = Field(default=None, alias="lecturerCode")
    display_name: str | None = Field(default=None, alias="displayName")
    role: str
    sequence_number: int = Field(alias="sequenceNumber")
    role_label: str = Field(alias="roleLabel")


class CommitteeResponse(ResponseModel):
    id: int
    code: str
    member_count: int = Field(alias="memberCount")
    created_by: int | None = Field(default=None, alias="createdBy")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    members: list[CommitteeMemberResponse] = Field(default_factory=list)


class CommitteeEnvelopeResponse(ResponseModel):
    data: CommitteeResponse


class CommitteeListEnvelopeResponse(ResponseModel):
    data: list[CommitteeResponse] = Field(default_factory=list)
    meta: dict[str, int]


class CommitteePreviewGroupErrorResponse(ResponseModel):
    code: str
    message: str


class CommitteePreviewGroupResponse(ResponseModel):
    code: str
    member_count: int = Field(alias="memberCount")
    ok: bool
    members: list[CommitteeMemberResponse] = Field(default_factory=list)
    errors: list[CommitteePreviewGroupErrorResponse] = Field(default_factory=list)


class CommitteePreviewResponse(ResponseModel):
    groups: list[CommitteePreviewGroupResponse] = Field(default_factory=list)


class CommitteePreviewEnvelopeResponse(ResponseModel):
    data: CommitteePreviewResponse


class CommitteeBulkCreateResponse(ImportResponse):
    committees: list[dict[str, Any]] = Field(default_factory=list)


class CommitteeBulkCreateEnvelopeResponse(ResponseModel):
    data: CommitteeBulkCreateResponse


class CommitteeBulkDeleteResponse(ResponseModel):
    deleted: int
    deleted_ids: list[int] = Field(alias="deletedIds")
    in_use_ids: list[int] = Field(default_factory=list, alias="inUseIds")


class CommitteeBulkDeleteEnvelopeResponse(ResponseModel):
    data: CommitteeBulkDeleteResponse
