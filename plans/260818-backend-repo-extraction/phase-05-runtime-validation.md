# Phase 05 — Target runtime validation

Start target postgres, api and worker using copied Compose. Validate PostgreSQL readiness, API health, Alembic current, service logs and existing backend test commands only where they do not write official data.

Full write-capable pytest, if run, must use a unique database named scheduler_test_<UTC timestamp> created inside target PostgreSQL. Before creation, query pg_database and abort if that name exists; before pytest, run SELECT current_database(), compare it to the generated name, assert DATABASE_URL contains that name and assert it does not contain /scheduler. Cleanup may target only that generated name and only after evidence is captured. Never point it at official scheduler data. Do not use test output to claim dependency/build repairs; report source-parity failures separately.

Machine-checkable guard sequence:

    $testDb = 'scheduler_test_' + (Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmssfff')
    if ($testDb -notmatch '^scheduler_test_[0-9]{17}$') { throw 'Unsafe test database name' }
    $exists = docker exec $targetPostgres psql -U scheduler -d postgres -At -c "SELECT 1 FROM pg_database WHERE datname='$testDb'"
    if ($LASTEXITCODE -ne 0 -or $exists.Trim() -eq '1') { throw 'Test database already exists or query failed' }
    docker exec $targetPostgres psql -U scheduler -d postgres -c "CREATE DATABASE $testDb OWNER scheduler"
    if ($LASTEXITCODE -ne 0) { throw 'Test database creation failed' }
    $current = docker exec $targetPostgres psql -U scheduler -d $testDb -At -c 'SELECT current_database()'
    if ($LASTEXITCODE -ne 0 -or $current.Trim() -ne $testDb) { throw 'current_database guard failed' }
    $testUrl = "postgresql+psycopg://scheduler:scheduler@postgres:5432/$testDb"
    if ($testUrl -notmatch [regex]::Escape('/' + $testDb) -or $testUrl -match '/scheduler([/?]|$)') { throw 'DATABASE_URL guard failed' }
    # Run pytest with DATABASE_URL=$testUrl only; preserve evidence before dropping $testDb.

If pytest fails, preserve logs and do not run cleanup blindly; any cleanup command must use the same allowlisted $testDb value.

Validate runtime worker command is unchanged from source Compose and apps/worker/main.py remains present and unchanged.
