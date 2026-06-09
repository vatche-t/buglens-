"""Call 2 of the pipeline: observation -> validated BugReport.

The model is asked for strict JSON; we parse defensively (stripping accidental
code fences / prose), validate against the canonical schema, and retry once with
a repair instruction before surfacing a graceful error. Like `vision`, the model
and processor are passed in so the orchestration is testable and Modal-managed.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from buglens.prompts import structure_user_text
from buglens.schema import BugReport

DEFAULT_MAX_NEW_TOKENS = 768
_FENCE_OPEN = re.compile(r"^```[a-zA-Z]*\n?")
_FENCE_CLOSE = re.compile(r"\n?```$")


class StructureError(Exception):
    """Raised when the model can't produce valid JSON even after a retry.

    Carries the last raw model output so the UI can fall back to showing it.
    """

    def __init__(self, message: str, raw: str = "") -> None:
        super().__init__(message)
        self.raw = raw


def extract_json(text: str) -> str:
    """Pull the JSON object out of a model response, tolerating fences/prose."""

    text = text.strip()
    if text.startswith("```"):
        text = _FENCE_CLOSE.sub("", _FENCE_OPEN.sub("", text)).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in model output")
    return text[start : end + 1]


def parse_report(text: str) -> BugReport:
    """Extract, parse, and validate a BugReport from raw model text."""

    return BugReport.model_validate(json.loads(extract_json(text)))


def generate_json(
    model: Any,
    processor: Any,
    prompt_text: str,
    *,
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
) -> str:
    """Run a text-only generation and return the decoded output."""

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt_text}]}]
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    generated = model.generate(**inputs, max_new_tokens=max_new_tokens)
    prompt_len = inputs["input_ids"].shape[-1]
    return processor.decode(generated[0][prompt_len:], skip_special_tokens=True).strip()


def structure(
    model: Any,
    processor: Any,
    observation: str,
    note: str | None = None,
    *,
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
) -> BugReport:
    """Structure an observation into a validated BugReport, retrying once."""

    prompt = structure_user_text(observation, note)
    raw = generate_json(model, processor, prompt, max_new_tokens=max_new_tokens)
    try:
        return parse_report(raw)
    except (ValueError, ValidationError, json.JSONDecodeError):
        repair = (
            f"{prompt}\n\nYour previous response was not valid JSON for the schema. "
            "Return ONLY the JSON object — no prose, no code fences."
        )
        raw = generate_json(model, processor, repair, max_new_tokens=max_new_tokens)
        try:
            return parse_report(raw)
        except (ValueError, ValidationError, json.JSONDecodeError) as exc:
            raise StructureError(
                "Model did not return valid JSON after one retry.", raw=raw
            ) from exc
