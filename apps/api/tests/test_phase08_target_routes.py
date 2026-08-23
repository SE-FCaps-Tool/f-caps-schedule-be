from app.main import create_app


def test_phase08_results_remediation_target_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("post", "/api/v1/remediations/{remediationId}/verify"),
        ("post", "/api/v1/remediations/{remediationId}/actions/overdue-fail"),
        ("get", "/api/v1/semesters/{semesterId}/remediations"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
