# Phase 06 — Final acceptance and rollback evidence

1. Re-run source hash, source health, counts and keys; prove no source mutation.
2. Re-run target path/hash allowlist; expected source-content diff only allowed FE/Compose removal. Exclude and report plan-owned/generated metadata separately.
3. Re-run service list, actual volume inspect, health, Alembic head and read-only parity.
4. Confirm workbook, importer, worker, docs, plans, specs and root metadata exist at expected paths.
5. Update feature_list.json evidence with captured command outputs; do not mark feature complete until verification passes.
