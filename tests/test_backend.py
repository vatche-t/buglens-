"""Tests for the Modal backend client (no network)."""

import base64

import pytest
import requests

from buglens import backend


class _FakeResp:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json


def test_requires_endpoint() -> None:
    with pytest.raises(backend.BackendError):
        backend.analyze_via_modal("", b"img")


def test_posts_base64_payload(monkeypatch) -> None:
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return _FakeResp(json_data={"title": "ok"})

    monkeypatch.setattr(requests, "post", fake_post)

    out = backend.analyze_via_modal("https://x.modal.run", b"PNGDATA", "note")

    assert out == {"title": "ok"}
    assert captured["url"] == "https://x.modal.run"
    assert captured["json"]["note"] == "note"
    assert base64.b64decode(captured["json"]["image_b64"]) == b"PNGDATA"


def test_http_error_raises(monkeypatch) -> None:
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResp(status_code=422, text="bad"))
    with pytest.raises(backend.BackendError, match="422"):
        backend.analyze_via_modal("https://x.modal.run", b"img")


def test_network_error_raises(monkeypatch) -> None:
    def boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(requests, "post", boom)
    with pytest.raises(backend.BackendError, match="reach"):
        backend.analyze_via_modal("https://x.modal.run", b"img")
