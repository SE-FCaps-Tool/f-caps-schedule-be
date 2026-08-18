from app.scheduler.versions import VersionStore


def test_version_activation_keeps_history_and_allows_one_active_version():
    store = VersionStore()
    first = store.create(round_id=1, snapshot={"seed": 1})
    second = store.create(round_id=1, snapshot={"seed": 2})
    store.activate(second.id)
    assert store.get(first.id).status == "DRAFT"
    assert store.get(second.id).status == "ACTIVE"
    assert [version.id for version in store.list(round_id=1)] == [first.id, second.id]


def test_version_metadata_is_immutable_and_comparable():
    store = VersionStore()
    snapshot = {"groups": [1]}
    first = store.create(
        round_id=1,
        snapshot=snapshot,
        algorithm_parameters={"time_limit": 5},
        random_seed=7,
        solver_status="OPTIMAL",
        objective=1,
        soft_scores={"S1": 2},
    )
    snapshot["groups"].append(2)
    second = store.create(round_id=1, snapshot={"groups": [1, 2]}, objective=2, soft_scores={"S1": 3})
    assert store.get(first.id).snapshot == {"groups": [1]}
    assert store.compare(first.id, second.id)["objective_delta"] == 1
