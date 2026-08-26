from app.main import create_app


def test_phase03_target_group_project_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/semesters/{semesterId}/groups"),
        ("post", "/api/v1/semesters/{semesterId}/groups"),
        ("get", "/api/v1/groups/{groupId}/members"),
        ("get", "/api/v1/groups/{groupId}/overview"),
        ("post", "/api/v1/groups/{groupId}/actions/change-leader"),
        ("post", "/api/v1/groups/{groupId}/members/{membershipId}/actions/leave"),
        ("put", "/api/v1/groups/{groupId}/project"),
        ("post", "/api/v1/semesters/{semesterId}/projects"),
        ("get", "/api/v1/projects/{projectId}/progression"),
        ("get", "/api/v1/projects/{projectId}/results"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected


def test_group_overview_accepts_public_group_identifier_in_openapi():
    operation = create_app().openapi()["paths"]["/api/v1/groups/{groupId}/overview"]["get"]
    parameter = next(item for item in operation["parameters"] if item["name"] == "groupId")
    assert {item["type"] for item in parameter["schema"]["anyOf"]} == {"string", "integer"}


def test_project_get_routes_accept_public_project_identifier_in_openapi():
    paths = create_app().openapi()["paths"]
    for path, method in (
        ("/api/v1/projects/{projectId}", "get"),
        ("/api/v1/projects/{projectId}/progression", "get"),
        ("/api/v1/projects/{projectId}/results", "get"),
    ):
        parameter = next(item for item in paths[path][method]["parameters"] if item["name"] == "projectId")
        assert {item["type"] for item in parameter["schema"]["anyOf"]} == {"string", "integer"}
