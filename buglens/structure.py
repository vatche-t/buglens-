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
from buglens.schema import BugReport, Severity

DEFAULT_MAX_NEW_TOKENS = 1536
_FENCE_OPEN = re.compile(r"^```[a-zA-Z]*\n?")
_FENCE_CLOSE = re.compile(r"\n?```$")
_PAYMENT_TERMS = ("payment", "checkout", "card", "pay", "purchase", "deposit")
_BLOCKED_TERMS = ("blocked", "disabled", "can't", "cannot", "won't", "stuck")


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


def _observation_lines(observation: str) -> list[str]:
    """Keep factual observation bullets without section headers."""

    lines: list[str] = []
    for raw in observation.splitlines():
        line = raw.strip().lstrip("-* ").strip()
        if not line or line.endswith(":"):
            continue
        lines.append(line)
    return lines or ["The uploaded screenshot contains a UI state that needs QA review."]


def fallback_report(observation: str, note: str | None = None) -> BugReport:
    """Build a conservative report when model JSON is invalid.

    The fallback keeps the live demo useful without inventing causes. It is
    intentionally generic, but still meets the same missing-info/test/edge-case
    floors required from the model prompt.
    """

    note = (note or "").strip()
    evidence = _observation_lines(observation)
    text = f"{observation}\n{note}".lower()
    is_payment = any(term in text for term in _PAYMENT_TERMS)
    appears_blocked = any(term in text for term in _BLOCKED_TERMS)

    app = "Checkout" if is_payment else "Application"
    title = (
        "Payment flow appears blocked"
        if is_payment and appears_blocked
        else "Issue visible in uploaded screenshot"
    )
    impact = (
        "an important payment flow appears blocked"
        if is_payment and appears_blocked
        else "the screenshot shows an issue that needs context before release risk is known"
    )
    severity = Severity.HIGH if is_payment and appears_blocked else Severity.MEDIUM
    visible_state = evidence[0]
    note_step = f"Use the tester note as context: {note}" if note else "Review the visible UI state"

    return BugReport(
        app=app,
        title=title,
        blurb=f"BugLens could not validate model JSON, but {impact}.",
        severity=severity,
        severity_why=(
            "High because a visible or tester-stated payment path appears blocked; "
            "scope and root cause still need confirmation."
            if severity is Severity.HIGH
            else "Medium because the visible issue may impair the workflow, but scope "
            "and workaround are not confirmed."
        ),
        vision_read=evidence[:6],
        summary=(
            "The screenshot and tester note indicate a UI problem, but the model's "
            "structured JSON response was invalid. This fallback report preserves "
            "only the visible/tester-stated evidence and lists the context QA needs "
            "before assigning broader impact."
        ),
        steps=[
            f"Open the {app.lower()} flow shown in the screenshot.",
            note_step,
            "Compare the current UI behavior with the expected successful path.",
        ],
        expected=(
            "The user can continue through the visible flow once required inputs are valid."
        ),
        actual=(
            f"From the available evidence, {visible_state}. No backend cause or broader "
            "impact is visible from the screenshot alone."
        ),
        env=[
            {
                "key": "Visible in screenshot",
                "value": "uploaded UI state",
                "known": True,
            },
            {
                "key": "Tester note",
                "value": note or "not provided",
                "known": bool(note),
            },
            {
                "key": "Browser / OS",
                "value": "not visible - please confirm",
                "known": False,
            },
            {
                "key": "Environment",
                "value": "not visible - please confirm prod, staging, or local",
                "known": False,
            },
            {
                "key": "Network / console / API response",
                "value": "not visible - please attach logs if available",
                "known": False,
            },
        ],
        missing_info=[
            {
                "question": "Which browser, OS, and viewport were used?",
                "why": "The screenshot cannot confirm whether the issue is device-specific.",
            },
            {
                "question": "Was this captured in production, staging, or local development?",
                "why": "Environment affects severity, routing, data, and release urgency.",
            },
            {
                "question": "Are there console errors, failed network requests, or API responses?",
                "why": "The screenshot cannot show whether the UI, validation, or backend failed.",
            },
            {
                "question": "How often does this reproduce and how many users are affected?",
                "why": "Frequency and scope are needed before escalating impact.",
            },
        ],
        regression_tests=[
            {
                "id": "TC-001",
                "title": "Visible flow reaches the expected next state",
                "given": f"I am on the {app.lower()} screen shown in the screenshot",
                "when": "I complete the visible required inputs using valid values",
                "then": "the primary action becomes available or the flow advances successfully",
            },
            {
                "id": "TC-002",
                "title": "Invalid input shows a clear recoverable state",
                "given": f"I am on the {app.lower()} screen",
                "when": "I enter invalid or incomplete data",
                "then": "the UI shows an actionable validation message without getting stuck",
            },
            {
                "id": "TC-003",
                "title": "Repeated attempt does not leave the UI disabled",
                "given": "the visible flow has already shown the reported state once",
                "when": "I correct the input and retry the primary action",
                "then": "the UI updates to the correct enabled, loading, success, or error state",
            },
        ],
        edge_cases=[
            {
                "title": "Slow or failed request",
                "detail": "Confirm the UI recovers cleanly when the related request times out.",
            },
            {
                "title": "Paste and autofill input",
                "detail": "Check whether pasted or autofilled values trigger validation updates.",
            },
            {
                "title": "Small viewport",
                "detail": "Verify the visible labels, errors, and primary action remain reachable.",
            },
        ],
    )


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
