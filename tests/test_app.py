"""Smoke tests for the BugLens backend endpoints."""

import base64

from fastapi.testclient import TestClient

from app import server
from buglens import backend

client = TestClient(server)

_PNG_B64 = base64.b64encode(b"fake-png-bytes").decode("ascii")


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


def test_upload_in_mock_mode_returns_501(monkeypatch) -> None:
    monkeypatch.delenv("BUGLENS_BACKEND", raising=False)  # default is mock
    resp = client.post("/api/analyze", json={"image_b64": _PNG_B64, "note": "hi"})
    assert resp.status_code == 501


def test_upload_in_modal_mode_forwards_to_backend(monkeypatch) -> None:
    monkeypatch.setenv("BUGLENS_BACKEND", "modal")
    monkeypatch.setenv("BUGLENS_MODAL_ENDPOINT", "https://x.modal.run")
    seen = {}

    def fake_analyze(endpoint, image_bytes, note):
        seen["endpoint"] = endpoint
        seen["bytes"] = image_bytes
        seen["note"] = note
        return {"title": "live report"}

    monkeypatch.setattr(backend, "analyze_via_modal", fake_analyze)

    resp = client.post("/api/analyze", json={"image_b64": _PNG_B64, "note": "broken"})

    assert resp.status_code == 200
    assert resp.json() == {"title": "live report"}
    assert seen["endpoint"] == "https://x.modal.run"
    assert seen["bytes"] == b"fake-png-bytes"
    assert seen["note"] == "broken"


def test_upload_with_invalid_base64_returns_400(monkeypatch) -> None:
    monkeypatch.setenv("BUGLENS_BACKEND", "modal")
    monkeypatch.setenv("BUGLENS_MODAL_ENDPOINT", "https://x.modal.run")
    resp = client.post("/api/analyze", json={"image_b64": "!!!not base64!!!", "note": ""})
    assert resp.status_code == 400


def test_upload_backend_error_returns_502(monkeypatch) -> None:
    monkeypatch.setenv("BUGLENS_BACKEND", "modal")
    monkeypatch.setenv("BUGLENS_MODAL_ENDPOINT", "https://x.modal.run")

    def boom(*a, **k):
        raise backend.BackendError("down")

    monkeypatch.setattr(backend, "analyze_via_modal", boom)
    resp = client.post("/api/analyze", json={"image_b64": _PNG_B64})
    assert resp.status_code == 502


def test_static_assets_served() -> None:
    # The jsx modules referenced by the HTML must be reachable under /static.
    resp = client.get("/static/buglens-data.jsx")
    assert resp.status_code == 200
    assert "EXAMPLES" in resp.text
