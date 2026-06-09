# BugLens Plan 04 - Prompt, Schema, And Quality Plan

Research date: 2026-06-09

Purpose: define the exact behavior that makes BugLens useful and honest.

## Core Principle

BugLens is not a chatbot. It is a structured QA artifact generator.

Every output must be:

- Visible-evidence grounded.
- Validated against a schema.
- Useful to a PM, QA engineer, or developer.
- Honest about missing context.

## Call 1: Screenshot Observation Prompt

Use this intent, not necessarily this exact wording:

```text
You are a QA assistant inspecting a UI screenshot.

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
```

Expected output shape:

```text
Visible facts:
- ...

Tester note:
- ...

Ambiguities:
- ...

Not visible:
- ...
```

Quality checks:

- Does it quote visible error text accurately?
- Does it avoid guessing environment?
- Does it separate tester note from visual evidence?
- Does it mention ambiguity?

## Call 2: Structuring Prompt

Use this intent:

```text
Convert the QA observation into a JSON bug artifact.

Return only valid JSON. No markdown. No prose. No code fence.

Schema:
{
  "title": "string",
  "severity": "P1 | P2 | P3",
  "component": "string",
  "steps": ["string"],
  "expected": "string",
  "actual": "string",
  "missing_info": ["string"],
  "regression_tests": [{"id": "string", "desc": "string"}],
  "edge_cases": ["string"]
}

Rules:
- Do not invent browser, OS, device, user role, environment, backend cause, API response, or account state.
- If context is not visible or not provided by the tester, put it in missing_info.
- If severity is uncertain, choose P3 unless the visible issue blocks a critical flow.
- Steps must be runnable by a QA tester.
- Regression tests must be specific and short.
- Edge cases must describe practical risks, not generic filler.
```

## Severity Rules

Use simple rules so output is consistent:

| Severity | Use when |
|---|---|
| P1 | Core business flow blocked, data loss, payment/deposit failure, security/privacy issue |
| P2 | Important workflow impaired but workaround likely exists |
| P3 | Visual defect, unclear state, copy issue, minor UX issue, uncertain severity |

Never mark P1 only because text looks dramatic. Tie it to visible or tester-stated impact.

## Missing Info Rules

This card is the differentiator. It should include:

- Browser.
- OS.
- Device/viewport.
- User role/account type.
- Environment: prod, staging, local.
- Repro frequency.
- Exact route/page URL.
- Network/API error details.
- Console logs.
- Backend trace/request ID.
- Whether other users are affected.

But only include what is actually missing for the current issue. Avoid dumping every possible field every time.

Good missing info:

- "Confirm browser and version; not visible in the screenshot."
- "Confirm whether this is production or staging."
- "Confirm whether the button remains disabled after required fields are filled."
- "Check network response for the deposit request; backend response is not visible."

Bad missing info:

- "The API is down." That is a guess.
- "User probably lacks permission." That is a guess.
- "Use Chrome." Not a question.

## Regression Test Rules

Regression tests should be short but runnable.

Good:

```text
TC-001: Verify the deposit button becomes enabled after all required fields are valid.
TC-002: Verify an inline error appears when the payment provider rejects a deposit.
TC-003: Verify duplicate clicks do not create duplicate deposit requests.
```

Bad:

```text
TC-001: Test the app.
TC-002: Check everything works.
```

## Edge Case Rules

Edge cases should show product depth:

- Double-click submit.
- Slow network.
- Timeout.
- Empty state.
- Very long text.
- Small mobile viewport.
- Expired session.
- Permission mismatch.
- Currency/locale mismatch.
- Partial backend success.

## Schema Validation Strategy

Validation requirements:

- Parse JSON.
- Strip accidental markdown fences.
- Validate with Pydantic.
- Clamp severity to allowed enum only through a clear fallback.
- Ensure at least one missing-info item if browser/device/environment are unknown.
- Ensure regression test IDs are stable: `TC-001`, `TC-002`, `TC-003`.

Failure behavior:

1. First parse fails.
2. Retry once with a strict "return JSON only" repair prompt.
3. If retry fails, show:
   - Factual observation.
   - Error message.
   - "Try again" button.

Do not silently swallow the error.

## Golden Test Cases

Create four golden screenshots and expected behavior notes.

### 1. Broken Payment

Input note:

```text
Deposit button does not respond after entering amount.
```

Expected:

- Severity likely P1 or P2 depending on visible context.
- Missing info includes environment, browser/device, console/network details.
- Regression tests include disabled/enabled state and duplicate-submit handling.

### 2. Login Error

Input note:

```text
User cannot log in even with correct credentials.
```

Expected:

- Missing info includes account type, auth provider, environment, browser/device.
- Edge cases include expired session, locked account, SSO fallback.

### 3. Empty Dashboard

Input note:

```text
Dashboard is blank after refresh.
```

Expected:

- Missing info includes API/network status and whether data exists for the user.
- Regression tests include empty state and data-loaded state.

### 4. Mobile Overflow

Input note:

```text
Text overlaps on mobile.
```

Expected:

- Severity likely P3 unless it blocks action.
- Missing info includes device/viewport.
- Regression tests include narrow viewport and long localized strings.

## Evaluation Checklist

Before submission, run each example and answer:

- Did the model make a claim it could not know?
- Is Missing Info useful, not generic?
- Would a PM paste the Bug Report card into Jira?
- Would a QA engineer run the regression tests?
- Are edge cases specific to this bug?
- Does invalid JSON fail gracefully?
- Does the same input produce roughly stable output?

## Field Notes Material To Capture

Save these during development:

- Screenshot of bad hallucinated output before prompt fix.
- Screenshot of improved missing-info card.
- Table of before/after prompt changes.
- One paragraph on why small models are enough for narrow QA tasks.
- One paragraph on where small models struggle.

This becomes the Field Notes blog/report and helps judges see real engineering judgment.

