# uv Workflow

BugLens uses `uv` for dependency management and task execution.

## Setup

Because this repo lives in OneDrive, use copy mode to avoid Windows cloud hardlink errors:

```powershell
uv sync --extra dev --link-mode=copy
```

## Common Commands

```powershell
uv run pytest
uv run ruff check .
uv run python app.py
```

## Modal Dependencies

Install Modal/runtime dependencies only when working on the GPU backend:

```powershell
uv sync --extra dev --extra modal --link-mode=copy
```

