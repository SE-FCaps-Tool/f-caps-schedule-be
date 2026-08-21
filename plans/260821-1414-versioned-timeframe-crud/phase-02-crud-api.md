# Phase 2 — Global CRUD API

Status: implemented.

- `POST /api/v1/timeframes/preview`
- `POST /api/v1/timeframes`
- `GET /api/v1/timeframes`
- `GET /api/v1/timeframes/{timeframeId}`
- `PATCH /api/v1/timeframes/{timeframeId}`
- `DELETE /api/v1/timeframes/{timeframeId}`

ADMIN/MANAGER only. PATCH is full replacement and creates a new revision.
DELETE archives. List excludes archived unless `includeArchived=true`.
