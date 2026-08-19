from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ScheduledSession:
    session_id: int
    group_id: int
    project_id: int
    timeslot_id: int
    room_id: int | None
    start_at: datetime
    end_at: datetime
    reviewer_ids: tuple[int, ...]
    day: str
    part: str


@dataclass(frozen=True)
class RoundInput:
    round_type: str
    expected_reviewer_count: int
    group_status: dict[int, str]
    group_project: dict[int, int]
    project_supervisors: dict[int, set[int]]
    lecturer_availability: set[tuple[int, int]]
    conflicts: set[tuple[int, int]]
    group_selected_slots: dict[int, set[int]]
    group_selection_mode: bool
    prior_reviewer_ids: dict[int, set[int]]
    remediation_verifier_ids: dict[int, set[int]]
    h11_waiver_groups: set[int]
    h12_sessions_per_part: int
    h12_sessions_per_day: int
    h12_semester_quota: int | None
    existing_semester_load: dict[int, int]
    result_owner_mode: bool = False
    soft_weights: dict[str, int] = field(default_factory=dict)
    h11_waiver_actors: dict[int, str] = field(default_factory=dict)
    h11_waiver_reasons: dict[int, str] = field(default_factory=dict)
    lecturer_load_preferences: dict[int, str] = field(default_factory=dict)
    group_leader_valid: dict[int, bool] = field(default_factory=dict)
    max_groups_per_timeslot: int | None = None
    max_minutes_per_part: int | None = None
    max_minutes_per_day: int | None = None


@dataclass(frozen=True)
class Violation:
    rule: str
    objects: tuple[str, ...]
    severity: str
    explanation: str
    remediation_hint: str


@dataclass(frozen=True)
class ValidationResult:
    violations: tuple[Violation, ...]

    @property
    def valid(self) -> bool:
        return not self.violations


@dataclass(frozen=True)
class Candidate:
    group_id: int
    timeslot_id: int
    start_at: datetime
    end_at: datetime
    day: str
    part: str
    reviewer_ids: tuple[int, ...]
    soft_score: int = 0


@dataclass(frozen=True)
class UnscheduledReason:
    code: str
    explanation: str
    remediation_hint: str


@dataclass(frozen=True)
class SolverResult:
    status: str
    sessions: tuple[ScheduledSession, ...]
    unscheduled: tuple[UnscheduledReason, ...]
    soft_scores: dict[str, int]
    random_seed: int
    objective: int


@dataclass(frozen=True)
class ScheduleVersion:
    id: int
    round_id: int
    snapshot: dict[str, Any]
    status: str = "DRAFT"
    algorithm_parameters: dict[str, Any] = field(default_factory=dict)
    random_seed: int | None = None
    solver_status: str | None = None
    objective: int = 0
    soft_scores: dict[str, int] = field(default_factory=dict)
    unscheduled: tuple[dict[str, Any], ...] = ()
