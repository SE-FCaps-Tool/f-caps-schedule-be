# Phase 04 — Tests và tài liệu

## Goal

Make the new contract executable and visible in OpenAPI/Markdown documentation.

## Tasks

1. Extend `apps/api/tests/test_phase03_api.py` or add a focused semester lifecycle test module.
2. Add tests for:
   - valid 105-day and 120-day periods;
   - 104-day and 121-day rejection;
   - reversed dates;
   - omitted status defaults to `UPCOMING`;
   - caller-supplied status is rejected/ignored according to the final contract;
   - duplicate code;
   - one active semester;
   - valid/invalid transitions;
   - authorization and audit payload.
3. Add migration regression test with a legacy `DRAFT` row.
4. Update `docs/api/master-data.md`, `docs/api/schemas.md`, `docs/api/admin-api.md` and
   `docs/api/api-reorganization.md`.
5. Ensure `/openapi.json` describes date fields, enum values and transition body.

## Acceptance

- Focused tests pass.
- Existing non-integration tests remain green.
- Docs examples match runtime response shapes.

