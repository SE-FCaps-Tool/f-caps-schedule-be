from app.main import create_app

# This list is self-contained so backend coverage cannot drift with a frontend checkout.
FE_USED_JSON_OPERATIONS = (
    ("GET", "/api/v1/semesters", 200),
    ("GET", "/api/v1/students", 200),
    ("GET", "/api/v1/semesters/{semesterId}/projects", 200),
    ("POST", "/api/v1/semesters/{semesterId}/projects", 201),
    ("GET", "/api/v1/lecturers", 200),
    ("GET", "/api/v1/rooms", 200),
    ("POST", "/api/v1/rounds/{roundId}/invitations", 201),
    ("GET", "/api/v1/reports/group-progress", 200),
    ("GET", "/api/v1/semesters/{semesterId}/groups", 200),
    ("POST", "/api/v1/semesters/{semesterId}/groups", 201),
    ("GET", "/api/v1/groups/{groupId}/members", 200),
    ("POST", "/api/v1/groups/{groupId}/actions/change-leader", 200),
    ("POST", "/api/v1/groups/{groupId}/members/{membershipId}/actions/leave", 200),
    ("PUT", "/api/v1/groups/{groupId}/project", 200),
    ("GET", "/api/v1/projects/{projectId}/progression", 200),
    ("GET", "/api/v1/projects/{projectId}/results", 200),
    ("GET", "/api/v1/semesters/{semesterId}/rounds", 200),
    ("POST", "/api/v1/semesters/{semesterId}/rounds", 201),
    ("GET", "/api/v1/rounds/{roundId}/eligible-projects", 200),
    ("GET", "/api/v1/rounds/{roundId}/registration-summary", 200),
    ("GET", "/api/v1/rounds/{roundId}/scheduling-readiness", 200),
    ("POST", "/api/v1/rounds/{roundId}/actions/open-registration", 200),
    ("POST", "/api/v1/rounds/{roundId}/actions/close-registration", 200),
    ("GET", "/api/v1/rounds/{roundId}/availability/me", 200),
    ("PUT", "/api/v1/rounds/{roundId}/availability/me", 200),
    ("POST", "/api/v1/rounds/{roundId}/invitations/me/respond", 200),
    ("POST", "/api/v1/rounds/{roundId}/invitations/{invitationId}/remind", 200),
    ("GET", "/api/v1/rounds/{roundId}/groups/{groupId}/preferences", 200),
    ("PUT", "/api/v1/rounds/{roundId}/groups/{groupId}/preferences", 200),
    ("POST", "/api/v1/rounds/{roundId}/schedules/{scheduleId}/actions/discard", 200),
    ("DELETE", "/api/v1/committees/{committeeId}", 200),
    ("PATCH", "/api/v1/rooms/{roomId}", 200),
    ("GET", "/api/v1/rounds/{roundId}/publish-readiness", 200),
    ("POST", "/api/v1/rounds/{roundId}/actions/publish", 200),
    ("POST", "/api/v1/sessions/{sessionId}/actions/change-room", 200),
    ("POST", "/api/v1/sessions/{sessionId}/actions/replace-reviewer", 200),
    ("POST", "/api/v1/sessions/{sessionId}/actions/postpone", 200),
    ("POST", "/api/v1/remediations/{remediationId}/verify", 200),
    ("GET", "/api/v1/lecturer/me/invitations", 200),
    ("GET", "/api/v1/lecturer/me/sessions", 200),
    ("GET", "/api/v1/lecturer/me/supervised-projects", 200),
    ("GET", "/api/v1/lecturer/me/remediations", 200),
    ("GET", "/api/v1/leader/me/dashboard", 200),
    ("GET", "/api/v1/leader/me/sessions", 200),
    ("GET", "/api/v1/remediation", 200),
)


def _resolve_schema(spec: dict, schema: dict) -> dict:
    ref = schema.get("$ref")
    if ref is None:
        return schema
    assert ref.startswith("#/components/schemas/")
    return spec["components"]["schemas"][ref.rsplit("/", 1)[-1]]


def test_every_frontend_json_operation_has_a_concrete_success_schema():
    spec = create_app().openapi()

    assert len(FE_USED_JSON_OPERATIONS) == 45
    assert len(set(FE_USED_JSON_OPERATIONS)) == 45
    for method, path, status in FE_USED_JSON_OPERATIONS:
        operation = spec["paths"][path][method.lower()]
        response = operation["responses"][str(status)]
        schema = response.get("content", {}).get("application/json", {}).get("schema")

        assert schema, (method, path, status)
        assert schema.get("$ref", "").startswith("#/components/schemas/ApiDataEnvelope"), (
            method,
            path,
            status,
        )
        envelope = _resolve_schema(spec, schema)
        data_schema = _resolve_schema(spec, envelope["properties"]["data"])
        concrete_schema = (
            _resolve_schema(spec, data_schema["items"])
            if data_schema.get("type") == "array"
            else data_schema
        )
        assert concrete_schema.get("properties"), (method, path, status)
