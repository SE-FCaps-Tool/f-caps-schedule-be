from app.api_contract import TARGET_OPERATIONS
from app.main import create_app


def test_fast_fix_target_registry_is_represented_in_openapi():
    paths = create_app().openapi()["paths"]
    missing = []
    for operation in TARGET_OPERATIONS:
        # Registry placeholders are shape-equivalent to FastAPI's snake_case
        # placeholders; compare by static path segments and method.
        static = [segment for segment in operation.path.split("/") if not segment.startswith("{")]
        if not any(operation.method.lower() in paths[p] and [s for s in p.split("/") if not s.startswith("{")] == static for p in paths):
            missing.append(f"{operation.method} {operation.path}")
    assert not missing, missing
