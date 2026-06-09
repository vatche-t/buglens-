"""Client for the Modal GPU backend.

The lightweight Gradio frontend calls this to run real inference on the Modal
endpoint over HTTPS. Kept dependency-light (requests only) so the Space image
stays small; the model itself lives on Modal.
"""

from __future__ import annotations

import base64

import requests

DEFAULT_TIMEOUT = 120.0


class BackendError(Exception):
    """Raised when the Modal backend is unreachable or returns an error."""


def analyze_via_modal(
    endpoint: str,
    image_bytes: bytes,
    note: str = "",
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """POST a screenshot + note to the Modal endpoint and return the payload."""

    if not endpoint:
        raise BackendError("Modal endpoint URL is not configured.")

    payload = {
        "image_b64": base64.b64encode(image_bytes).decode("ascii"),
        "note": note or "",
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise BackendError(f"Could not reach the Modal backend: {exc}") from exc

    if resp.status_code >= 400:
        raise BackendError(f"Modal backend returned {resp.status_code}: {resp.text[:200]}")
    return resp.json()
