from app.jobs import JobStore


def test_noop_job_is_claimed_and_completed_idempotently():
    store = JobStore()
    job_id = store.enqueue("noop")

    first = store.run_once()
    second = store.run_once()

    assert first == {"job_id": job_id, "status": "completed"}
    assert second is None
    assert store.status(job_id) == "completed"

