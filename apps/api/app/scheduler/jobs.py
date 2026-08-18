from dataclasses import dataclass, replace
from typing import Any

from app.domain.errors import DomainError

JOB_STATUSES = ("QUEUED", "RUNNING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED")


@dataclass(frozen=True)
class SchedulerJob:
    id: int
    round_id: int
    status: str
    input_snapshot: dict[str, Any]
    algorithm_parameters: dict[str, Any]
    random_seed: int
    attempt: int = 1
    version_id: int | None = None
    error: str | None = None


class SchedulerJobStore:
    """Deterministic lifecycle seam; the database worker can use the same transitions."""

    def __init__(self) -> None:
        self._jobs: dict[int, SchedulerJob] = {}
        self._next_id = 1

    def enqueue(
        self,
        *,
        round_id: int,
        input_snapshot: dict[str, Any],
        algorithm_parameters: dict[str, Any],
        random_seed: int,
    ) -> SchedulerJob:
        job = SchedulerJob(
            id=self._next_id,
            round_id=round_id,
            status="QUEUED",
            input_snapshot=dict(input_snapshot),
            algorithm_parameters=dict(algorithm_parameters),
            random_seed=random_seed,
        )
        self._jobs[job.id] = job
        self._next_id += 1
        return job

    def get(self, job_id: int) -> SchedulerJob:
        if job_id not in self._jobs:
            raise DomainError("SCHEDULER_JOB_NOT_FOUND", "Scheduler job does not exist.")
        return self._jobs[job_id]

    def start(self, job_id: int) -> SchedulerJob:
        job = self.get(job_id)
        if job.status != "QUEUED":
            raise DomainError("SCHEDULER_JOB_NOT_QUEUED", "Only a queued job can start.")
        return self._save(replace(job, status="RUNNING"))

    def complete(self, job_id: int, *, version_id: int, partial: bool = False) -> SchedulerJob:
        job = self.get(job_id)
        if job.version_id is not None:
            if job.version_id != version_id:
                raise DomainError("SCHEDULER_VERSION_ALREADY_BOUND", "Job already has another ScheduleVersion.")
            return job
        if job.status != "RUNNING":
            raise DomainError("SCHEDULER_JOB_NOT_RUNNING", "Only a running job can complete.")
        return self._save(replace(job, status="PARTIAL" if partial else "COMPLETED", version_id=version_id))

    def fail(self, job_id: int, *, error: str) -> SchedulerJob:
        job = self.get(job_id)
        if job.status not in {"QUEUED", "RUNNING"}:
            raise DomainError("SCHEDULER_JOB_NOT_ACTIVE", "Only an active job can fail.")
        return self._save(replace(job, status="FAILED", error=error))

    def cancel(self, job_id: int) -> SchedulerJob:
        job = self.get(job_id)
        if job.status not in {"QUEUED", "RUNNING"}:
            raise DomainError("SCHEDULER_JOB_NOT_ACTIVE", "Only an active job can be cancelled.")
        return self._save(replace(job, status="CANCELLED"))

    def retry(self, job_id: int) -> SchedulerJob:
        job = self.get(job_id)
        if job.version_id is not None:
            return job
        if job.status != "FAILED":
            raise DomainError("SCHEDULER_JOB_NOT_RETRYABLE", "Only a failed job without a version can retry.")
        return self._save(replace(job, status="QUEUED", attempt=job.attempt + 1, error=None))

    def _save(self, job: SchedulerJob) -> SchedulerJob:
        self._jobs[job.id] = job
        return job
