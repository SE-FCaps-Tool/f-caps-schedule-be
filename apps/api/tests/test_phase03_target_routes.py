from app.main import create_app


def test_phase03_target_group_project_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/semesters/{semesterId}/groups"),
        ("post", "/api/v1/semesters/{semesterId}/groups"),
        ("get", "/api/v1/groups/{groupId}/members"),
        ("post", "/api/v1/groups/{groupId}/actions/change-leader"),
        ("post", "/api/v1/groups/{groupId}/members/{membershipId}/actions/leave"),
        ("put", "/api/v1/groups/{groupId}/project"),
        ("post", "/api/v1/semesters/{semesterId}/projects"),
        ("get", "/api/v1/projects/{projectId}/progression"),
        ("get", "/api/v1/projects/{projectId}/results"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
