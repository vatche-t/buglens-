"""Smoke tests for the BugLens backend endpoints (mock mode)."""

from fastapi.testclient import TestClient

from app import server

client = TestClient(server)


def test_index_serves_custom_frontend() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "BugLens" in resp.text


def test_examples_endpoint_lists_four() -> None:
    resp = client.get("/api/examples")
    assert resp.status_code == 200
    assert len(resp.json()) == 4


def test_analyze_returns_frontend_payload() -> None:
    resp = client.get("/api/analyze", params={"id": "payment"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["severityWhy"]
    assert body["missing"][0]["q"]
    assert body["tests"][0]["then"]
    assert body["edges"][0]["d"]


def test_analyze_unknown_and_missing_id_404() -> None:
    assert client.get("/api/analyze", params={"id": "nope"}).status_code == 404
    assert client.get("/api/analyze").status_code == 404


def test_export_formats() -> None:
    csv_resp = client.get("/api/export/csv", params={"id": "payment"})
    assert csv_resp.status_code == 200
    assert csv_resp.json()["text"].startswith("id,title,given,when,then")

    assert client.get("/api/export/jira", params={"id": "payment"}).status_code == 200
    assert client.get("/api/export/bogus", params={"id": "payment"}).status_code == 404


def test_static_assets_served() -> None:
    # The jsx modules referenced by the HTML must be reachable under /static.
    resp = client.get("/static/buglens-data.jsx")
    assert resp.status_code == 200
    assert "EXAMPLES" in resp.text
