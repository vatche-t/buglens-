"""Runtime configuration for BugLens."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum


DEFAULT_MODEL_ID = "openbmb/MiniCPM-V-4.6"


class BackendMode(StrEnum):
    """Supported inference backends."""

    MOCK = "mock"
    MODAL = "modal"
    ZERO_GPU = "zerogpu"


@dataclass(frozen=True)
class Settings:
    """Resolved runtime settings."""

    backend: BackendMode = BackendMode.MOCK
    model_id: str = DEFAULT_MODEL_ID
    modal_endpoint: str = ""


def load_settings() -> Settings:
    """Load settings from environment variables."""

    backend_value = os.getenv("BUGLENS_BACKEND", BackendMode.MOCK.value).strip().lower()
    try:
        backend = BackendMode(backend_value)
    except ValueError:
        backend = BackendMode.MOCK

    return Settings(
        backend=backend,
        model_id=os.getenv("BUGLENS_MODEL_ID", DEFAULT_MODEL_ID).strip() or DEFAULT_MODEL_ID,
        modal_endpoint=os.getenv("BUGLENS_MODAL_ENDPOINT", "").strip(),
    )

