"""Versioned prompts for the BugLens model pipeline.

Kept in one place so prompt changes are reviewable and the vision/structuring
calls never drift from the behavior described in docs/plans/04.
"""

from __future__ import annotations

# Call 1 — perception only. The model must describe what is visible and must
# never guess context it cannot see. This honesty is the whole product.
VISION_PROMPT = """You are a QA assistant inspecting a UI screenshot.

Describe only what is visible in the screenshot and what the tester note explicitly says.

Include:
- screen or page type if visible
- visible buttons and whether they appear enabled, disabled, loading, or selected
- visible error text, empty states, warnings, labels, amounts, or table states
- visible layout issues, overlap, truncation, missing content, or broken states
- the tester's note as user-provided context

Do not infer causes.
Do not guess browser, OS, device, user role, environment, backend state, API status, account status, or network state.
If something is ambiguous, say it is ambiguous.

Respond using exactly these sections:
Visible facts:
- ...

Tester note:
- ...

Ambiguities:
- ...

Not visible:
- ..."""


def vision_user_text(note: str | None) -> str:
    """Compose the vision instructions plus the tester note (or a clear absence)."""

    note = (note or "").strip()
    suffix = note if note else "(none provided)"
    return f"{VISION_PROMPT}\n\nTester note: {suffix}"
