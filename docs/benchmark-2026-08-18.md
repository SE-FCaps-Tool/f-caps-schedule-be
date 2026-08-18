# Scheduler benchmark evidence — 2026-08-18

## Fixture

The deterministic target fixture is `74 groups / 26 lecturers / 40 timeslots / 4 rooms`.
It uses the shared CP-SAT solver and the shared H1–H12 validator. Because the fixture uses one selected slot per group, the available 40 timeslots are the limiting resource; the expected result is a valid partial schedule with every group represented either as a session or an unscheduled reason.

## Repeated run

Command:

```powershell
Push-Location apps/api
@'
from statistics import median
from time import perf_counter
from app.scheduler.benchmark import build_target_fixture
from app.scheduler.scheduler import solve_schedule
from app.scheduler.validator import validate_schedule

times = []
for seed in range(17, 24):
    context, groups, timeslots, rooms, reviewers = build_target_fixture()
    started = perf_counter()
    result = solve_schedule(context, groups=groups, timeslots=timeslots, rooms=rooms, reviewers=reviewers, time_limit_seconds=5, random_seed=seed)
    elapsed = perf_counter() - started
    assert len(result.sessions) + len(result.unscheduled) == 74
    assert validate_schedule(result.sessions, context).valid
    times.append(elapsed)
    print(seed, result.status, len(result.sessions), len(result.unscheduled), elapsed)
ordered = sorted(times)
print("p50", median(times), "p95", ordered[min(len(ordered) - 1, int(len(ordered) * .95))], "max", max(times))
'@ | uv run python -
Pop-Location
```

Observed results:

| Seed | Solver status | Scheduled | Unscheduled | Elapsed |
|---:|---|---:|---:|---:|
| 17 | PARTIAL | 40 | 34 | 0.086 s |
| 18 | PARTIAL | 40 | 34 | 0.094 s |
| 19 | PARTIAL | 40 | 34 | 0.085 s |
| 20 | PARTIAL | 40 | 34 | 0.117 s |
| 21 | PARTIAL | 40 | 34 | 0.083 s |
| 22 | PARTIAL | 40 | 34 | 0.096 s |
| 23 | PARTIAL | 40 | 34 | 0.069 s |

Summary: `p50 = 0.086 s`, `p95 = 0.117 s`, `max = 0.117 s`. Every run satisfied the 74-item accounting invariant and the shared validator returned zero violations.

### Final Docker rerun

The same seven-seed command was rerun inside the rebuilt API container. It produced 40 scheduled / 34 unscheduled on every seed with `p50 = 0.1184 s`, `p95 = 0.1445 s`, `max = 0.1445 s`; all runs passed the shared validator.

## Reviewer-load distribution smoke

The representative availability case uses `8 groups / 4 Reviewers / 8 slots / 2 rooms`, with every Reviewer available for every slot and an 8-session semester quota. With S1 enabled, the solver scheduled all 8 groups and produced `6 / 6 / 6 / 6` Reviewer sessions, so the max/min load ratio was `1.0×` (target `≤1.5×`). The shared validator returned zero violations. The regression is executable as `test_solver_balances_reviewer_load_when_quota_and_s1_are_configured` in `apps/api/tests/test_scheduler_engine.py`.

## Dashboard/list API latency

After login against the Docker API, each endpoint was requested 30 times from the local host. The observed p95 values were:

| Endpoint | p50 | p95 | Max |
|---|---:|---:|---:|
| `/api/v1/dashboard` | 23.4 ms | 31.2 ms | 36.8 ms |
| `/api/v1/rounds` | 17.5 ms | 25.5 ms | 26.5 ms |
| `/api/v1/reports/lecturer-load` | 15.8 ms | 20.1 ms | 25.5 ms |

These are local Docker measurements, not a production capacity guarantee. They are below the two-second p95 target for the current seeded semester.

## Interpretation

This is a local development-machine measurement, not a production capacity guarantee. It proves the Phase 04 target fixture is comfortably below the 60-second requirement and gives a repeatable baseline for later solver changes. The partial result is expected for this fixture because 74 groups compete for 40 selected slots.

## Backup/restore rehearsal

On the same date, PostgreSQL was logically copied into the exact temporary database `scheduler_restore_verify_20260818`:

```powershell
docker compose exec -T postgres psql -U scheduler -d postgres -c "CREATE DATABASE scheduler_restore_verify_20260818;"
docker compose exec -T postgres pg_dump -U scheduler -d scheduler | docker compose exec -T postgres psql -U scheduler -d scheduler_restore_verify_20260818
docker compose exec -T postgres psql -U scheduler -d scheduler_restore_verify_20260818 -c "SELECT (SELECT count(*) FROM accounts), (SELECT count(*) FROM semesters), (SELECT count(*) FROM groups), (SELECT count(*) FROM schedule_versions);"
docker compose exec -T postgres psql -U scheduler -d postgres -c "DROP DATABASE scheduler_restore_verify_20260818;"
```

Restore verification returned `356 accounts`, `38 semesters`, `110 groups` and `72 schedule_versions`; the temporary database was then removed.
