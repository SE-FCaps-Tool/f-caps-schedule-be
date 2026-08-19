# Phase 02 — Status enums, DTOs, envelopes, and errors

## Objective

Align domain values and typed response models before adding the missing route families.

## Scope

- Introduce explicit target mappings for Group, Project, Invitation, Room, Session, and Round statuses.
- Add reversible migrations or translation views for historical values; do not silently discard legacy statuses.
- Extend `response_models.py` for nested objects, actor fields, pagination metadata, and string IDs.
- Centralize error codes/details and authorization failure mapping.

## Tests to write first

- Legacy-to-target and target-to-legacy status round trips.
- Migration upgrade/downgrade with historical rows.
- DTO serialization for null actors, nested resources, and paginated lists.
- Role/scope and archived-semester guard contract tests.

## Acceptance criteria

- Four-state group semantics (`FORMING`, `FORMED`, `ASSIGNED`, `DISBANDED`) are represented without breaking historical data.
- Project and invitation statuses match the migration/spec contract or have an explicit documented compatibility mapping.
- All new handlers can return the target envelope and error shape through shared helpers.

## Risks

Enum changes can invalidate existing filters and seed data. Require a disposable database migration test and an explicit mapping table before deployment.
