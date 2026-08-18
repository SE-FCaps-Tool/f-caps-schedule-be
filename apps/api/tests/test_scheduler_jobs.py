import pytest

from app.domain.errors import DomainError
from app.scheduler.jobs import SchedulerJobStore


def test_job_lifecycle_retry_and_version_binding_are_idempotent():
    store = SchedulerJobStore()
    job = store.enqueue(round_id=1, input_snapshot={"groups": [1]}, algorithm_parameters={"limit": 5}, random_seed=7)
    store.start(job.id)
    failed = store.fail(job.id, error="temporary solver failure")
    retried = store.retry(failed.id)
    assert retried.status == "QUEUED"
    assert retried.attempt == 2
    store.start(retried.id)
    completed = store.complete(retried.id, version_id=12)
    assert completed.status == "COMPLETED"
    assert store.complete(retried.id, version_id=12) == completed
    with pytest.raises(DomainError, match="another ScheduleVersion"):
        store.complete(retried.id, version_id=13)

