from time import perf_counter

from app.scheduler.benchmark import build_target_fixture
from app.scheduler.scheduler import solve_schedule
from app.scheduler.validator import validate_schedule


def test_target_fixture_is_repeatable_and_finishes_within_sixty_seconds():
    context, groups, timeslots, rooms, reviewers = build_target_fixture()
    started = perf_counter()
    result = solve_schedule(
        context,
        groups=groups,
        timeslots=timeslots,
        rooms=rooms,
        reviewers=reviewers,
        time_limit_seconds=5,
        random_seed=17,
    )
    elapsed = perf_counter() - started
    assert elapsed < 60
    assert result.status in {"OPTIMAL", "FEASIBLE", "PARTIAL"}
    assert len(result.sessions) + len(result.unscheduled) == 74
    assert validate_schedule(result.sessions, context).valid
    assert all(reason.code for reason in result.unscheduled)
