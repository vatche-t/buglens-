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


# Call 2 — turn the factual observation into the validated BugReport JSON. Field
# names match the schema exactly so the output validates directly. Rules mirror
# docs/plans/04 (honesty, severity, regression, edge cases).
STRUCTURE_PROMPT = """Convert the QA observation below into a single JSON bug report.

Return ONLY valid JSON. No markdown, no prose, no code fences.

Use exactly these fields:
{
  "app": "string - the product area or component, e.g. Checkout",
  "title": "string - concise bug title",
  "blurb": "string - one short sentence summarizing the bug",
  "severity": "one of: critical, high, medium, low",
  "severity_why": "string - why this severity, tied to visible or stated impact",
  "vision_read": ["string - the key visible facts you were given"],
  "summary": "string - a few sentences describing the bug from visible evidence",
  "steps": ["string - runnable reproduction steps"],
  "expected": "string",
  "actual": "string",
  "env": [{"key": "string", "value": "string", "known": true}],
  "missing_info": [{"question": "string", "why": "string"}],
  "regression_tests": [{"id": "TC-001", "title": "string", "given": "string", "when": "string", "then": "string"}],
  "edge_cases": [{"title": "string", "detail": "string"}]
}

Rules:
- Ground every claim in the observation. Do not invent browser, OS, device, viewport, user role, environment, backend cause, API response, network state, or account state. If it is not visible in the screenshot or stated in the tester note, record it in env with known=false and add a matching missing_info entry.
- Never claim data loss, data corruption, security, or privacy impact unless it is explicitly visible in the screenshot or stated by the tester. Do not speculate about backend consequences.
- severity:
    - "critical" ONLY when a core user flow is completely and visibly blocked (or the tester states it is) with no workaround. Never use "critical" for an inferred or possible consequence.
    - "high" for a seriously impaired important flow.
    - "medium" for an impaired workflow with a likely workaround.
    - "low" for cosmetic, copy, layout, or uncertain issues.
  Tie severity to visible or tester-stated impact, never to dramatic wording.
- missing_info is the most important field. Provide 3 to 5 specific questions about context a screenshot cannot show (browser/version, environment prod/staging, device/viewport, repro frequency, network/console/API details, affected users, exact route). Give each a short "why". Provide at least 3.
- regression_tests: provide at least 3, specific and short, written as Given/When/Then, with stable ids TC-001, TC-002, TC-003, ...
- edge_cases: provide at least 3 practical risks, not generic filler.
- steps must be runnable by a QA tester."""


def structure_user_text(observation: str, note: str | None = None) -> str:
    """Compose the structuring instructions with the observation and tester note."""

    note = (note or "").strip()
    suffix = note if note else "(none provided)"
    return f"{STRUCTURE_PROMPT}\n\nObservation:\n{observation}\n\nTester note: {suffix}"
