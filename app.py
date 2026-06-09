"""BugLens entrypoint — a custom frontend served on Gradio's Server (FastAPI).

`gradio.Server` is a FastAPI subclass with Gradio's API engine (queue, SSE,
concurrency) layered on top. We use it to serve the custom `buglens-ui` React
prototype as the frontend (the Off-Brand path) while exposing the analysis as
a backend endpoint.

In this step the backend runs in mock mode: it returns the built-in example
reports. The vision/structuring/Modal pipeline plugs into `analyze()` next.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from gradio import Server

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

server = Server(title="BugLens")


def analyze(example_id: str | None = None) -> BugReport:
    """Resolve a screenshot to a structured report.

    Mock mode (current): look the report up from the built-in examples. The real
    backends (Modal / ZeroGPU running MiniCPM-V 4.6) will replace this body while
    keeping the same return contract.
    """

    settings = load_settings()
    if settings.backend.value != "mock":  # pragma: no cover - real backends land later
        raise HTTPException(
            status_code=501,
            detail=f"Backend '{settings.backend.value}' not wired yet.",
        )

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
    """Return the structured report payload the frontend renders into cards."""

    return analyze(id).to_ui_payload()


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
