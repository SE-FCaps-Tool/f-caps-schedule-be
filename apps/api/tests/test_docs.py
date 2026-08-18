def test_docs_uses_local_swagger_assets(client):
    response = client.get("/docs")

    assert response.status_code == 200
    assert 'href="/_docs/swagger-ui.css"' in response.text
    assert 'src="/_docs/swagger-ui-bundle.js"' in response.text
    assert "cdn.jsdelivr.net" not in response.text


def test_docs_assets_are_served_by_the_api(client):
    css = client.get("/_docs/swagger-ui.css")
    bundle = client.get("/_docs/swagger-ui-bundle.js")

    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]
    assert bundle.status_code == 200
    assert "javascript" in bundle.headers["content-type"]


def test_docs_oauth_redirect_is_available(client):
    response = client.get("/docs/oauth2-redirect")

    assert response.status_code == 200
    assert "window.opener.swaggerUIRedirectOauth2" in response.text
