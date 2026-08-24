# Group Overview FE Handoff

## Endpoint

```http
GET /api/v1/groups/{groupId}/overview
```

Role: `ADMIN`, `MANAGER`.

Response is target-style:

```json
{
  "data": {
    "id": 123,
    "code": "GRP-SU26SE001",
    "status": "ASSIGNED",
    "semester": { "id": 7, "code": "SU26", "name": "Summer 2026" },
    "memberCount": 4,
    "leader": null,
    "members": [],
    "project": null,
    "progress": { "groupStatus": "ASSIGNED", "rounds": [] },
    "remediation": null,
    "warnings": []
  }
}
```

The overview is the read model for the Group 360 screen. FE should not join
`groups`, `sessions`, `results` and `remediation` responses itself.

## Data included

- `id`, `code`, `status`, `semester`, `memberCount`, `leader`, `members`.
- `project` with project identity, status and `mainSupervisor`/
  `coSupervisor`.
- `progress.groupStatus` and `progress.rounds`.
- Each progress row includes `roundId`, `roundType`, `roundStatus`, optional
  `sessionId`, `sessionStatus`, `scheduledAt`, `roomCode` and `result`.
- `result` is `null` when the session has no result yet. This is expected and
  should render as “Chưa có kết quả”, not as an error.
- `remediation` is the current non-terminal remediation case, or `null`.
- `warnings` contains actionable codes such as `NO_PROJECT`, `NO_LEADER` and
  `FEWER_THAN_RECOMMENDED_MEMBERS`.

## Recommended layout

1. Header: group code/status and semester.
2. Project and supervisors.
3. Members table.
4. Progress/review table, including rows with no result.
5. Current result/remediation summary.
6. Warnings panel only when `warnings.length > 0`.

Keep the first version read-only. Existing group/result/remediation mutation
flows remain separate.

## React Query behavior

Suggested query key:

```ts
["manager", "group", groupId, "overview"]
```

Fetch the overview when a group detail route/dialog opens. Invalidate or refetch
this key after successful mutations that can change the overview:

- `POST /api/v1/sessions/{sessionId}/result` — submit or correct result.
- `POST /api/v1/remediations/{remediationId}/verify` — verify remediation.
- `POST /api/v1/remediation/{caseId}/overdue-fail` — fail overdue case.
- Group leader/member/project mutations if the detail screen performs them.

Do not manually patch nested `progress`, `result` or `remediation` objects;
refetching keeps the aggregate authoritative.

## Loading, errors and nulls

- Loading: show a detail skeleton.
- `404`: group no longer exists; close the detail view and refresh the list.
- `403`: show the existing permission error state.
- `result: null`: normal no-result state.
- `project: null`, `leader: null`, `remediation: null`: normal incomplete
  states, surfaced through the relevant warning or empty-state copy.

## FE questions / contract notes

- Use the generated OpenAPI types after BE publishes the endpoint.
- Field names are camelCase at the wire level.
- Dates are ISO-8601 strings; format them in the user's locale.
- A corrected result appears after the overview query is invalidated; FE does
  not need a separate “correction history” request in V1.
