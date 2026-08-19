from app.main import create_app


def test_phase03_target_group_project_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/semesters/{semester_id}/groups"),
        ("post", "/api/v1/semesters/{semester_id}/groups"),
        ("get", "/api/v1/groups/{group_id}/members"),
        ("post", "/api/v1/groups/{group_id}/actions/change-leader"),
        ("post", "/api/v1/groups/{group_id}/members/{membership_id}/actions/leave"),
        ("put", "/api/v1/groups/{group_id}/project"),
        ("post", "/api/v1/semesters/{semester_id}/projects"),
        ("get", "/api/v1/projects/{project_id}/progression"),
        ("get", "/api/v1/projects/{project_id}/results"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
