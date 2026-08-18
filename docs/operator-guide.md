# Local operator guide

This guide describes the Scheduler-only V1 workflow. It assumes the Docker Compose stack is running and the operator has an active Admin or Manager account.

## 1. Start and migrate

```powershell
docker compose up --build -d
docker compose ps
docker compose logs --tail=50 api worker
```

The API and worker apply all Alembic migrations on startup. Confirm `http://localhost:8000/health` returns an OK response before using the UI.

## 2. Load local demonstration data

Use the Admin seed endpoint once for a clean local demonstration. The fixture is deterministic and idempotent; it creates the 26-lecturer, 74-group dataset used by the scheduler benchmark.

```powershell
curl.exe -X POST http://localhost:8000/api/v1/admin/seed-fixture `
  -H "X-Test-Session: active-admin"
```

For normal operation, create or edit data through the Admin/Manager forms. Excel import/export is not part of V1.

## 3. Configure a round

1. Create or select the semester.
2. Create a round with one of `REVIEW_1`, `REVIEW_2`, `DEFENSE_1_1`, `DEFENSE_1_2` or `DEFENSE_2`.
3. Set reviewer count and session duration. Review rounds use two Reviewers; Defense rounds use three.
4. Add round days and timeslots, then register available rooms and eligible groups.
5. Send lecturer invitations and collect lecturer availability before the deadline.
6. Enable group availability only when the round should use Project Leader slot selection. The active group Leader is the only student allowed to submit it.
7. For D1.1/D2, assign exactly one Result Owner who is also a Reviewer. Review and D1.2 do not use Result Owner.
8. Use the explicit round transition endpoint or the UI action to move the round into scheduling only after required inputs are complete.

The server validates all of these rules. A client-side disabled button is not a permission boundary.

## 4. Run and inspect a schedule

Run the scheduler from the round workspace with a seed and time limit. Every run creates an independent ScheduleVersion and preserves scheduled and unscheduled groups with reason codes. Inspect violations, reviewer load, H12 counts and unscheduled reasons before activation.

Only a valid version can be activated. Activation requires an `activated_at` value and makes the version the round's current working schedule. Compare versions before choosing one.

## 5. Publish and change a schedule

Publish only after the manager has reviewed the complete valid version. Publishing sends in-app notifications to affected Reviewers, Supervisors, active Leaders and group members and writes an audit event/outbox record.

After publication:

- small draft edits are no longer allowed on the published version;
- use Controlled Change with a reason;
- the server validates the complete resulting schedule;
- a new version is created and the source version remains queryable;
- affected users receive a change notification;
- a completed session's Reviewer snapshot cannot be rewritten.

Postpone/cancel/reschedule actions also require the relevant role and audit the actor, reason and decision. H11 waiver is the only permitted hard-constraint waiver; only a Manager may grant it for the current group and round, with a non-empty reason.

## 6. Enter results and remediation

The assigned Reviewer enters the result for a session. Managers may correct a result only with a reason. Result Owner is enforced on D1.1 and D2; it is not applied to Review or D1.2.

D1.1 transitions are:

- `LEVEL_1` → eligible for D1.2;
- `LEVEL_2` → D1.2 conditional and an open remediation case with a Verifier;
- `LEVEL_3` → pending D2;
- `LEVEL_4` → failed.

D1.2 accepts only `COMPLETED` and never fails a group because a session is postponed or cancelled. D2 uses `PASS` or `FAIL` as the final outcome. A Verifier records remediation verification; overdue cases are failed by a Manager with a reason. All result and transition changes preserve before/after history.

## 7. Notifications and worker health

The worker claims PostgreSQL outbox jobs with row locking, marks deliveries sent/failed and creates remediation reminders. Monitor it with:

```powershell
docker compose logs -f worker
```

Notification delivery is idempotent through dedupe keys. The default local email adapter is a no-op; in-app notification records remain the local source of observable delivery.

## 8. Backup and reset for local work

Create a logical backup before testing destructive scenarios:

```powershell
docker compose exec -T postgres pg_dump -U scheduler -d scheduler > scheduler-backup.sql
```

To recreate local containers and volumes after explicitly deciding to discard local data:

```powershell
docker compose down -v
docker compose up --build -d
```

The second command recreates the schema from migrations. Do not use `down -v` when the local database contains work that has not been backed up.
