"""Explicit OpenAPI response models.

The application historically returned raw SQL mapping dictionaries.  That is
fine at runtime, but ``list[dict[str, object]]`` gives FastAPI no field
information and Swagger renders ``additionalProp1``.  These models describe
the public response contract while keeping ``extra='allow'`` during the
transition so older response fields remain backward compatible.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class LoginResponse(ResponseModel):
    role: str
    expires_at: datetime | str


class LogoutResponse(ResponseModel):
    status: str


class MeResponse(ResponseModel):
    role: str
    status: str
    account_id: int | None = None


class PublicMeResponse(ResponseModel):
    role: str
    status: str


class SemesterResponse(ResponseModel):
    id: int
    code: str
    name: str
    start_date: date | None = None
    end_date: date | None = None
    status: str
    created_at: datetime | None = None


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
    status: str | None = None
    semester_id: int | None = None


class ProjectDetailResponse(ProjectResponse):
    group: ProjectGroupSummary | None = None


class GroupMemberResponse(ResponseModel):
    student_id: int
    student_code: str
    display_name: str | None = None
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
    active_member_count: int | None = None
    leader_count: int | None = None
    leader_name: str | None = None


class GroupMutationResponse(ResponseModel):
    id: int
    code: str
    member_count: int | None = None
    status: str | None = None
    project_id: int | None = None


class GroupDetailResponse(GroupResponse):
    members: list[GroupMemberResponse] = Field(default_factory=list)


class LecturerResponse(ResponseModel):
    id: int
    lecturer_code: str
    account_id: int | None = None
    email: str | None = None
    display_name: str | None = None
    account_status: str | None = None
    conflicts: list["ConflictItem"] = Field(default_factory=list)


class ConflictItem(ResponseModel):
    project_id: int
    reason: str | None = None


class RoomResponse(ResponseModel):
    id: int
    code: str
    name: str
    capacity: int
    active: bool = True


class RoundResponse(ResponseModel):
    id: int
    semester_id: int
    type: str
    status: str
    reviewer_count: int
    result_owner_mode: bool = False
    group_selection_mode: bool = False
    session_duration_minutes: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    registration_deadline: datetime | None = None
    h12_sessions_per_part: int | None = None
    h12_sessions_per_day: int | None = None
    h12_semester_quota: int | None = None
    max_groups_per_timeslot: int | None = None
    max_minutes_per_part: int | None = None
    max_minutes_per_day: int | None = None
    soft_weights: dict[str, int] = Field(default_factory=dict)


class RoundResourceResponse(ResponseModel):
    round_id: int
    groups: int
    timeslots: int
    rooms: int


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
    reviewers: list["ReviewerSummary"] | None = None


class ReviewerSummary(ResponseModel):
    id: int
    code: str
    name: str | None = None


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


class VersionDetailResponse(VersionSummaryResponse):
    sessions: list[SessionResponse] = Field(default_factory=list)


class DashboardResponse(ResponseModel):
    totals: dict[str, int] = Field(default_factory=dict)
    availability: dict[str, int] = Field(default_factory=dict)
    groups: dict[str, int] = Field(default_factory=dict)
    pending_reschedule_requests: int = 0
    changes: int = 0
    version: VersionSummaryResponse | None = None
    lecturer_load: list["DashboardLecturerLoadResponse"] = Field(default_factory=list)
    attention_groups: list["AttentionGroupResponse"] = Field(default_factory=list)
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
    defense_1_1: str | None = None
    defense_1_2: str | None = None
    defense_2: str | None = None
    result_verifier_lecturer_id: int | None = None
    remediation_status: str | None = None
    remediation_due_at: datetime | None = None
    remediation_verifier_lecturer_id: int | None = None


class ImportResponse(ResponseModel):
    created: int
    skipped: int
    errors: list[dict[str, Any]] = Field(default_factory=list)


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


class PublishResponse(ResponseModel):
    round_id: int
    version_id: int
    status: str
    recipient_count: int = 0


class SessionEditResponse(ResponseModel):
    session_id: int
    version_id: int
    status: str


class ControlledChangeResponse(ResponseModel):
    version_id: int
    source_version_id: int
    session_id: int
    status: str


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
