# Lecturer Semester Context API

## Semester catalog

```http
GET /api/v1/lecturer/me/semesters
```

The endpoint is available to the authenticated `LECTURER` only. It returns
semesters related to the current lecturer through invitations, scheduled
sessions, supervised projects, or remediation cases. Unrelated semesters are
never included.

```json
{
  "data": [
    {
      "id": 2,
      "code": "SU26",
      "name": "Summer 2026",
      "status": "ACTIVE",
      "startDate": "2026-05-04",
      "endDate": "2026-08-16"
    }
  ]
}
```

Results are ordered with `ACTIVE` first, then the latest semester start date.
The frontend uses the first accessible `ACTIVE` semester by default and falls
back to the latest related semester.

## Semester-scoped portal lists

The following Lecturer list endpoints accept the optional `semesterId` query
parameter:

```http
GET /api/v1/lecturer/me/invitations?semesterId=2
GET /api/v1/lecturer/me/sessions?semesterId=2
GET /api/v1/lecturer/me/supervised-projects?semesterId=2
GET /api/v1/lecturer/me/remediations?semesterId=2
```

When supplied, the backend filters by the owning semester relationship. The
Lecturer scope is still enforced independently; passing an unrelated semester
returns an empty list rather than another lecturer's data.

Round-based responses include semester context:

- invitations: `round.semester` with `id`, `code`, `name`, `status`, `startDate`, and `endDate`;
- sessions: flat `semesterId` and `semesterCode`;
- supervised projects: existing `semesterId` and `semesterCode`;
- remediations: flat `semesterId` and `semesterCode`.

The frontend must not issue an unscoped list request while the selected
semester is unresolved. An empty related-semester catalog is a valid state and
should be shown separately from an API error.
