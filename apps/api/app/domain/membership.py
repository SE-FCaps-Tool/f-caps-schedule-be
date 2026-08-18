from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.errors import DomainError


@dataclass
class MembershipRecord:
    group_id: int
    student_id: int
    role: str
    status: str = "ACTIVE"
    joined_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    left_at: datetime | None = None
    reason: str | None = None


class MembershipLedger:
    def __init__(self) -> None:
        self.records: list[MembershipRecord] = []

    def add(self, *, group_id: int, student_id: int, role: str = "MEMBER") -> MembershipRecord:
        if any(
            record.group_id == group_id
            and record.student_id == student_id
            and record.status == "ACTIVE"
            for record in self.records
        ):
            raise DomainError("MEMBERSHIP_DUPLICATE", "A student already has active membership in this group.")
        if role == "LEADER" and any(
            record.group_id == group_id
            and record.role == "LEADER"
            and record.status == "ACTIVE"
            for record in self.records
        ):
            raise DomainError("MEMBERSHIP_LEADER_EXISTS", "A group may have only one active leader.")
        record = MembershipRecord(group_id=group_id, student_id=student_id, role=role)
        self.records.append(record)
        return record

    def drop(self, *, group_id: int, student_id: int, reason: str) -> MembershipRecord:
        if not reason.strip():
            raise DomainError("MEMBERSHIP_REASON_REQUIRED", "A dropout reason is required.")
        for record in self.records:
            if record.group_id == group_id and record.student_id == student_id and record.status == "ACTIVE":
                record.status = "DROPPED"
                record.left_at = datetime.now(UTC)
                record.reason = reason
                return record
        raise DomainError("MEMBERSHIP_NOT_FOUND", "No active membership exists for this student and group.")

    def active_members(self, *, group_id: int) -> list[MembershipRecord]:
        return [record for record in self.records if record.group_id == group_id and record.status == "ACTIVE"]

    def history(self, *, group_id: int, student_id: int) -> list[MembershipRecord]:
        return [
            record
            for record in self.records
            if record.group_id == group_id and record.student_id == student_id
        ]
