# Phase 2 — Groups and projects contract

## Objective

Align manager group/project list, create, detail, assignment, and progression APIs with spec fields,
filters, pagination, and string IDs.

## Scope

- `GET /semesters/{semesterId}/groups`: `search`, `status`, `hasProject`, `hasLeader`, `warning`,
  `page`, `pageSize`; return leader/project summaries, member count, and warnings.
- `POST /semesters/{semesterId}/groups`: accept `studentIds` and `leaderId`; allow a group to exist
  before project assignment when domain rules permit it.
- `GET/POST /semesters/{semesterId}/projects`: accept `nameVi`, `nameEn`, `mainSupervisorId`,
  `coSupervisorId`; return target `Project` fields and initial `DRAFT` status.
- Normalize nested member IDs, project assignment, project progression/results, and validation error
  codes. Preserve old `members`, `title`, `supervisors`, and integer inputs as aliases.

## Likely files and ownership

- `apps/api/app/routes/target_group_project.py` — target handlers and query params.
- `apps/api/app/routes/master_data.py`, `manager_extensions.py` — delegate legacy writes/read logic.
- `apps/api/app/response_models.py`, `apps/api/app/domain/membership.py` — DTO and validation mapping.
- `apps/api/tests/test_phase03_api.py`, new `test_groups_projects_contract.py`.

## Tests to write first

- Scoped list filters and pagination metadata.
- Create group with student IDs, leader validation, duplicate membership, and no project.
- Create project with main/co-supervisor aliases and same-supervisor rejection.
- Assign project across semesters, already-assigned project, and archived-semester rejection.
- Target IDs/fields/envelopes plus legacy group/project regression.

## Acceptance criteria

- FE sample requests in spec §§41–48 succeed without FE-side transformation.
- All documented query params are present in OpenAPI and produce deterministic filtering.
- Group/project IDs and nested IDs are prefixed strings in target responses.
- Errors include the documented stable codes (`GROUP_CODE_DUPLICATE`, `STUDENT_NOT_ENROLLED`,
  `PROJECT_ALREADY_ASSIGNED`, etc.).

## Rollback

Disable only target handlers or their DTO adapters. Keep existing group/project tables and legacy
write functions unchanged; revert only additive response/query code if necessary.

