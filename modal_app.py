"""Modal GPU endpoint serving MiniCPM-V 4.6 for the BugLens pipeline.

Deploy:  modal deploy modal_app.py
Modal prints an https://<...>.modal.run URL. Put it in the HF Space secret
BUGLENS_MODAL_ENDPOINT and set BUGLENS_BACKEND=modal; the Space then POSTs the
screenshot here and renders the returned BugReport payload.

The heavy lifting (observe -> structure) lives in the already-tested
buglens.vision / buglens.structure modules; this file just wires them onto a
GPU container with the model loaded once per container.
"""

from __future__ import annotations

import base64
import io

import modal
from pydantic import BaseModel

from buglens.config import DEFAULT_MODEL_ID

MINUTES = 60

# MiniCPM-V 4.6 needs transformers>=5.7; use `av` instead of `torchcodec` to
# avoid the CUDA-version conflict the model card warns about. Local buglens
# package is baked in last so pip layers stay cached.
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "transformers[torch]>=5.7.0",
        "torchvision",
        "av",
        "accelerate",
        "pillow==12.2.0",
        "pydantic==2.13.4",
        "fastapi[standard]",
    )
    .add_local_python_source("buglens", copy=True)
)

app = modal.App("buglens", image=image)


class AnalyzeRequest(BaseModel):
    """JSON body for the analyze endpoint."""

    image_b64: str
    note: str = ""


@app.cls(gpu="A10G", scaledown_window=5 * MINUTES, timeout=10 * MINUTES)
class BugLens:
    @modal.enter()
    def load(self) -> None:
        """Load the model once per container (persists across requests)."""

        from buglens.vision import load_model

        self.model, self.processor = load_model(DEFAULT_MODEL_ID)

    @modal.fastapi_endpoint(method="POST", docs=True)
    def analyze(self, req: AnalyzeRequest) -> dict:
        """Screenshot (base64) + note -> validated BugReport payload."""

        from fastapi import HTTPException
        from PIL import Image, UnidentifiedImageError

        from buglens.structure import StructureError, fallback_report, structure
        from buglens.vision import observe

        try:
            screenshot = Image.open(io.BytesIO(base64.b64decode(req.image_b64))).convert("RGB")
        except (ValueError, UnidentifiedImageError) as exc:
            raise HTTPException(status_code=400, detail="Could not decode image_b64.") from exc

        observation = observe(self.model, self.processor, screenshot, req.note)
        try:
            report = structure(self.model, self.processor, observation, req.note)
        except StructureError:
            report = fallback_report(observation, req.note)
        return report.to_ui_payload()
