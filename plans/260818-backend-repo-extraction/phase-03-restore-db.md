# Phase 03 — Restore database vào volume riêng

1. Start only target postgres and wait readiness.
2. Resolve source/target IDs; abort if empty/equal.
3. Inspect source mount and require capstonedefensescheduler_postgres_data; reject if source ID is empty.
4. Inspect target mount and require f_caps_schedule_be_postgres_data and absence of source volume; reject if target ID equals source ID.
5. Copy validated dump only to target.
6. In the same PowerShell block immediately before pg_restore, re-assert target ID and mount. Run pg_restore --exit-on-error --clean --if-exists --no-owner --no-privileges only in target; check exit code; remove target temporary dump.
7. Do not run importer or seed.

Abort before restore if identity/mount check fails or any command touches source container.
