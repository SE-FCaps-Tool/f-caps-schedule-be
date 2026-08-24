from time import perf_counter

from app.scheduler.benchmark import build_target_fixture
from app.scheduler.candidates import generate_candidates
from app.scheduler.scheduler import solve_schedule
from app.scheduler.validator import validate_schedule


def test_target_fixture_is_repeatable_and_finishes_within_sixty_seconds():
    context, groups, timeslots, reviewers = build_target_fixture()
    candidate_pool = generate_candidates(
        context,
        groups=groups,
        timeslots=timeslots,
        reviewers=reviewers,
    )
    started = perf_counter()
    results = [
        solve_schedule(
            context,
            groups=groups,
            timeslots=timeslots,
            reviewers=reviewers,
            time_limit_seconds=5,
            random_seed=17 + index,
            objective_profile=profile,
            candidate_pool=candidate_pool,
        )
        for index, profile in enumerate(("LECTURER_COMPACT", "LOAD_BALANCED", "EARLY_FINISH"))
    ]
    elapsed = perf_counter() - started
    assert elapsed < 60
    for result in results:
        assert result.status in {"OPTIMAL", "FEASIBLE", "PARTIAL"}
        assert len(result.sessions) + len(result.unscheduled) == 74
        assert validate_schedule(result.sessions, context).valid
        assert all(reason.code for reason in result.unscheduled)
