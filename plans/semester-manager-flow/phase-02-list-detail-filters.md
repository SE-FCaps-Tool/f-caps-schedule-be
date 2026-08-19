# Phase 02 — List, detail, counts, and filters

## Goal

Expose the complete semester read contract used by the Manager list and detail
screens.

## Changes

- Add a shared semester select/serializer with actor joins.
- Count projects by `projects.semester_id`, groups through projects, and rounds by
  `rounds.semester_id` in independent aggregate subqueries.
- Extend `GET /api/v1/semesters` with optional `search`, `status`, and
  `academic_year`; apply all supplied filters with AND semantics.
- Add `GET /api/v1/semesters/{semester_id}` and return `404 SEMESTER_NOT_FOUND`.
- Use `ILIKE` over code/name for case-insensitive search.

## Acceptance

- Empty semesters return all counts as zero.
- Counts are not multiplied by joins.
- Invalid status/year receives FastAPI validation error.
- List and detail return identical complete item fields.
