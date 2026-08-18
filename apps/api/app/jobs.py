from dataclasses import dataclass


@dataclass
class _Job:
    job_id: int
    name: str
    status: str = "queued"


class JobStore:
    """Small in-memory seam for Phase 01; PostgreSQL-backed jobs arrive in Phase 02."""

    def __init__(self) -> None:
        self._next_id = 1
        self._jobs: dict[int, _Job] = {}

    def enqueue(self, name: str) -> int:
        job = _Job(job_id=self._next_id, name=name)
        self._jobs[job.job_id] = job
        self._next_id += 1
        return job.job_id

    def run_once(self) -> dict[str, int | str] | None:
        queued = next((job for job in self._jobs.values() if job.status == "queued"), None)
        if queued is None:
            return None
        queued.status = "completed"
        return {"job_id": queued.job_id, "status": queued.status}

    def status(self, job_id: int) -> str:
        return self._jobs[job_id].status

