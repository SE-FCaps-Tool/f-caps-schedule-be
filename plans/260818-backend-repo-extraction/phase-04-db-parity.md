# Phase 04 — Read-only database parity

Use read-only source/target queries or a verifier outside runtime. Compare Alembic head, all baseline counts, exact round types, canonical deterministic keys for projects/groups/lecturers/rooms/rounds/sessions/session reviewers, and deterministic keys for every current excel_* table. Check no orphaned Excel links.

Verifier must reject write SQL and fail on mismatch. Recheck source/target IDs and actual volume names before queries. Source health/counts/keys after restore must equal the pre-extraction baseline.
