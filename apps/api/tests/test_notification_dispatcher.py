from app.services.notification_dispatcher import NoopEmailAdapter


def test_noop_email_adapter_has_the_same_event_contract_as_the_outbox():
    adapter = NoopEmailAdapter()

    assert adapter.send(recipient="manager@example.test", event_type="SCHEDULE_PUBLISHED", payload={"version_id": 1}) is None
