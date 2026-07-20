from fastapi.testclient import TestClient

from aegisx.api import create_app
from aegisx.config import Settings


def test_liveness_security_headers_and_metrics() -> None:
    app = create_app(
        Settings(database_url="sqlite+pysqlite:///:memory:", redis_url="redis://127.0.0.1:1/0")
    )
    client = TestClient(app)
    response = client.get("/health/live", headers={"X-Request-ID": "request-1"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "aegisx_http_responses_total" in metrics.text


def test_readiness_fails_closed_when_redis_is_unavailable() -> None:
    app = create_app(
        Settings(database_url="sqlite+pysqlite:///:memory:", redis_url="redis://127.0.0.1:1/0")
    )
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "dependencies unavailable"}


def test_production_rejects_development_keys() -> None:
    try:
        Settings(environment="production")
    except ValueError as exc:
        assert "production token keys" in str(exc)
    else:
        raise AssertionError("production settings accepted development secrets")
