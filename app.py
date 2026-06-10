"""BugLens entrypoint — a custom frontend served on Gradio's Server (FastAPI).

`gradio.Server` is a FastAPI subclass with Gradio's API engine (queue, SSE,
concurrency) layered on top. We use it to serve the custom `buglens-ui` React
prototype as the frontend (the Off-Brand path) while exposing the analysis as
a backend endpoint.

Example screenshots are always served from the built-in mock reports (so the
app is fully explorable without a GPU). Uploaded screenshots are analyzed for
real by POSTing to the Modal backend when BUGLENS_BACKEND=modal.
"""

from __future__ import annotations

import base64
import binascii
import mimetypes
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from gradio import Server
from pydantic import BaseModel

from buglens import backend
from buglens.config import load_settings
from buglens.examples import get_example, list_examples
from buglens.render import (
    regression_tests_to_csv,
    to_github_issue,
    to_jira_markdown,
)
from buglens.schema import BugReport

UI_DIR = Path(__file__).parent / "buglens-ui"
INDEX_FILE = UI_DIR / "BugLens.html"

mimetypes.add_type("text/babel", ".jsx")

server = Server(title="BugLens")


def analyze(example_id: str | None = None) -> BugReport:
    """Return a built-in example report for gallery clicks and exports."""

    report = get_example(example_id) if example_id else None
    if report is None:
        raise HTTPException(status_code=404, detail="Unknown example id.")
    return report


@server.get("/api/examples")
def api_examples() -> list[dict]:
    """Gallery metadata for the example screenshots."""

    return list_examples()


@server.get("/api/analyze")
def api_analyze(id: str | None = None) -> dict:
    """Return a built-in example's report payload (gallery clicks)."""

    return analyze(id).to_ui_payload()


class AnalyzeUpload(BaseModel):
    """JSON body for analyzing an uploaded screenshot."""

    image_b64: str
    note: str = ""


@server.post("/api/analyze")
def api_analyze_upload(payload: AnalyzeUpload) -> dict:
    """Analyze an uploaded screenshot via the configured inference backend."""

    settings = load_settings()
    if settings.backend.value != "modal":
        raise HTTPException(
            status_code=501,
            detail=(
                "Live screenshot analysis needs the Modal backend "
                "(set BUGLENS_BACKEND=modal). Pick an example to preview the app."
            ),
        )
    try:
        image_bytes = base64.b64decode(payload.image_b64, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid image data.") from exc

    try:
        return backend.analyze_via_modal(settings.modal_endpoint, image_bytes, payload.note)
    except backend.BackendError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@server.get("/api/export/{fmt}")
def api_export(fmt: str, id: str | None = None):
    """Return a text export (jira | github | csv) for an example."""

    report = analyze(id)
    if fmt == "jira":
        return {"format": "jira", "text": to_jira_markdown(report)}
    if fmt == "github":
        return {"format": "github", "text": to_github_issue(report)}
    if fmt == "csv":
        return {"format": "csv", "text": regression_tests_to_csv(report)}
    raise HTTPException(status_code=404, detail="Unknown export format.")


@server.get("/")
def index() -> FileResponse:
    """Serve the custom BugLens frontend."""

    return FileResponse(INDEX_FILE)


# Frontend assets (the jsx modules) under a dedicated prefix so we never shadow
# Gradio's own /gradio_api/* routes or our /api/* endpoints.
server.mount("/static", StaticFiles(directory=UI_DIR), name="static")


def main() -> None:
    """Launch the BugLens server."""

    server.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
