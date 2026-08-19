# Phase 10 — Frontend cutover, deprecation, and cleanup

## Objective

Move consumers to the target contract safely and remove compatibility code only after evidence supports it.

## Scope

- Publish the final OpenAPI contract and migration guide for the frontend repository.
- Add deprecation headers, route usage telemetry, and a documented sunset date for aliases.
- Run full integration, migration upgrade/downgrade, benchmark, and authorization suites.
- Remove only aliases with zero consumer traffic and explicit sign-off.

## External dependency and handoff

The frontend repository is outside this workspace. Phase completion therefore requires a versioned OpenAPI export, endpoint migration matrix, consumer sign-off or issue link from the frontend team, and route-usage telemetry proving the alias is unused. Backend-only tests cannot substitute for that evidence.

## Tests to write first

- End-to-end screen-to-endpoint contract matrix from the spec.
- Clean database bootstrap and upgrade from the previous production head.
- Legacy alias smoke tests during the deprecation window.
- Rollback rehearsal using the additive migration strategy.

## Acceptance criteria

Every target endpoint has an owner, test evidence, and frontend consumer; no alias is removed while telemetry shows usage; release notes document any intentional breaking change.

## Rollback

Disable target routes or restore the previous application image while retaining additive migrations. Never delete historical status mappings as part of cleanup.
