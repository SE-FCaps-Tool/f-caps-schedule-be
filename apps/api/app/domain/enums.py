from enum import Enum


class DomainEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class SystemRole(DomainEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    LECTURER = "LECTURER"
    STUDENT = "STUDENT"


class TopicType(DomainEnum):
    APPLICATION = "APPLICATION"
    RESEARCH = "RESEARCH"
    INTEGRATED = "INTEGRATED"
    REGULAR = "REGULAR"


class LecturerSeniorityLevel(DomainEnum):
    SENIOR = "Senior"
    MID_LEVEL = "MidLevel"
    JUNIOR = "Junior"
    ROOKIE = "Rookie"


class SemesterStatus(DomainEnum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class AssignmentRole(DomainEnum):
    SUPERVISOR = "SUPERVISOR"
    REVIEWER = "REVIEWER"
    RESULT_OWNER = "RESULT_OWNER"
    REMEDIATION_VERIFIER = "REMEDIATION_VERIFIER"
    PROJECT_LEADER = "PROJECT_LEADER"


class RoundStatus(DomainEnum):
    DRAFT = "DRAFT"
    OPEN_REGISTRATION = "OPEN_REGISTRATION"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    SCHEDULING = "SCHEDULING"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    ONGOING = "ONGOING"
    POSTPONED = "POSTPONED"
    COMPLETED = "COMPLETED"
    LOCKED = "LOCKED"
    CANCELLED = "CANCELLED"


class DefenseType(DomainEnum):
    REVIEW_1_1 = "REVIEW_1_1"
    REVIEW_2_1 = "REVIEW_2_1"
    REVIEW_1 = "REVIEW_1"
    REVIEW_2 = "REVIEW_2"
    DEFENSE_1_1 = "DEFENSE_1_1"
    DEFENSE_1_2 = "DEFENSE_1_2"
    # Legacy names kept so historical rows and clients remain readable.
    REVIEW_3 = "REVIEW_3"
    REVIEW = "REVIEW"
    DEFENSE_1 = "DEFENSE_1"
    DEFENSE_2 = "DEFENSE_2"
    REMEDIATION = "REMEDIATION"


class GroupStatus(DomainEnum):
    PENDING_D11 = "PENDING_D11"
    ELIGIBLE_D12 = "ELIGIBLE_D12"
    D12_CONDITIONAL = "D12_CONDITIONAL"
    PENDING_D2 = "PENDING_D2"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DROPPED = "DROPPED"


class ResultOutcome(DomainEnum):
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    PASS = "PASS"
    NEEDS_FIX = "NEEDS_FIX"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"
    COMPLETED = "COMPLETED"
