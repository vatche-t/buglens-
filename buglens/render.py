"""Export a validated report to Jira, GitHub, and CSV formats.

These power the Copy / Download buttons in the UI; the React frontend renders
the four cards directly from `BugReport.to_ui_payload()`, so rendering here is
limited to the text exports a PM or QA engineer pastes elsewhere. Every function
is deterministic and model-free, so the same report always exports identically.
"""

from __future__ import annotations

import csv
import io

from buglens.schema import BugReport

CSV_HEADER = ("id", "title", "given", "when", "then")


def to_jira_markdown(report: BugReport) -> str:
    """Format a report as Jira wiki markup ready to paste into a ticket."""

    lines = [
        f"h2. {report.title}",
        "",
        f"*Severity:* {report.severity.value.capitalize()} — {report.severity_why}",
        f"*Component:* {report.app}",
        "",
        "h3. Summary",
        report.summary,
        "",
        "h3. Steps to Reproduce",
    ]
    lines += [f"# {step}" for step in report.steps]
    lines += ["", "h3. Expected", report.expected]
    lines += ["", "h3. Actual", report.actual]
    lines += ["", "h3. Environment"]
    lines += [
        f"* {fact.key}: {fact.value}{'' if fact.known else ' _(unconfirmed)_'}"
        for fact in report.env
    ]
    lines += ["", "h3. Missing Info (confirm before filing)"]
    lines += [f"* {item.question} — {item.why}" for item in report.missing_info]
    lines += ["", "h3. Regression Tests"]
    for test in report.regression_tests:
        lines.append(
            f"* {test.id} {test.title}: "
            f"given {test.given}, when {test.when}, then {test.then}"
        )
    lines += ["", "h3. Edge Cases"]
    lines += [f"* {case.title}: {case.detail}" for case in report.edge_cases]
    return "\n".join(lines)


def to_github_issue(report: BugReport) -> str:
    """Format a report as GitHub-flavored Markdown for a new issue body."""

    lines = [
        f"# {report.title}",
        "",
        f"**Severity:** {report.severity.value.capitalize()} — {report.severity_why}  ",
        f"**Component:** {report.app}",
        "",
        "## Summary",
        report.summary,
        "",
        "## Steps to Reproduce",
    ]
    lines += [f"{index}. {step}" for index, step in enumerate(report.steps, start=1)]
    lines += ["", "## Expected", report.expected]
    lines += ["", "## Actual", report.actual]
    lines += ["", "## Environment", "", "| Field | Value | Confirmed |", "| --- | --- | --- |"]
    lines += [
        f"| {fact.key} | {fact.value} | {'yes' if fact.known else 'no'} |"
        for fact in report.env
    ]
    lines += ["", "## Missing Info (confirm before filing)"]
    lines += [f"- [ ] **{item.question}** — {item.why}" for item in report.missing_info]
    lines += ["", "## Regression Tests"]
    for test in report.regression_tests:
        lines.append(f"- **{test.id} {test.title}**")
        lines.append(f"  - _Given_ {test.given}")
        lines.append(f"  - _When_ {test.when}")
        lines.append(f"  - _Then_ {test.then}")
    lines += ["", "## Edge Cases"]
    lines += [f"- **{case.title}** — {case.detail}" for case in report.edge_cases]
    return "\n".join(lines)


def regression_tests_to_csv(report: BugReport) -> str:
    """Serialize regression tests to CSV with a stable header and `\\n` endings.

    Uses the standard library writer so commas and quotes in any Given/When/Then
    field are escaped correctly.
    """

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    for test in report.regression_tests:
        writer.writerow([test.id, test.title, test.given, test.when, test.then])
    return buffer.getvalue()
