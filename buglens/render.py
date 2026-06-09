"""Render validated reports to UI cards and export formats.

Every function here is deterministic and model-free, so the same `BugReport`
always produces the same text. That keeps exports easy to test and safe to call
directly from the Gradio UI. All functions consume the single `BugReport`
contract from `buglens.schema`; rendering never invents its own shape.
"""

from __future__ import annotations

import csv
import io

from buglens.schema import BugReport

CSV_HEADER = ("id", "description")


def to_jira_markdown(report: BugReport) -> str:
    """Format a report as Jira wiki markup ready to paste into a ticket."""

    lines = [
        f"h2. {report.title}",
        "",
        f"*Severity:* {report.severity.value}",
        f"*Component:* {report.component}",
        "",
        "h3. Steps to Reproduce",
    ]
    lines += [f"# {step}" for step in report.steps]
    lines += ["", "h3. Expected", report.expected]
    lines += ["", "h3. Actual", report.actual]
    lines += ["", "h3. Missing Info"]
    lines += [f"* {item}" for item in report.missing_info]
    lines += ["", "h3. Regression Tests"]
    lines += [f"* {test.id}: {test.desc}" for test in report.regression_tests]
    lines += ["", "h3. Edge Cases"]
    lines += [f"* {item}" for item in report.edge_cases]
    return "\n".join(lines)


def to_github_issue(report: BugReport) -> str:
    """Format a report as GitHub-flavored Markdown for a new issue body."""

    lines = [
        f"# {report.title}",
        "",
        f"**Severity:** {report.severity.value}  ",
        f"**Component:** {report.component}",
        "",
        "## Steps to Reproduce",
    ]
    lines += [f"{index}. {step}" for index, step in enumerate(report.steps, start=1)]
    lines += ["", "## Expected", report.expected]
    lines += ["", "## Actual", report.actual]
    lines += ["", "## Missing Info"]
    lines += [f"- [ ] {item}" for item in report.missing_info]
    lines += ["", "## Regression Tests"]
    lines += [f"- **{test.id}**: {test.desc}" for test in report.regression_tests]
    lines += ["", "## Edge Cases"]
    lines += [f"- {item}" for item in report.edge_cases]
    return "\n".join(lines)


def regression_tests_to_csv(report: BugReport) -> str:
    """Serialize regression tests to CSV text with a stable header and newlines.

    Uses the standard library writer so commas and quotes in descriptions are
    escaped correctly, and pins ``\\n`` line endings for deterministic output.
    """

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    for test in report.regression_tests:
        writer.writerow([test.id, test.desc])
    return buffer.getvalue()


def bug_report_card(report: BugReport) -> str:
    """Markdown for the Bug Report card shown in the UI."""

    steps = "\n".join(f"{index}. {step}" for index, step in enumerate(report.steps, start=1))
    return (
        f"### {report.title}\n\n"
        f"**Severity:** {report.severity.value} · **Component:** {report.component}\n\n"
        f"**Steps to reproduce**\n{steps}\n\n"
        f"**Expected:** {report.expected}\n\n"
        f"**Actual:** {report.actual}"
    )


def missing_info_card(report: BugReport) -> str:
    """Markdown for the Missing Info card, the honesty differentiator."""

    items = "\n".join(f"- {item}" for item in report.missing_info)
    return (
        "### Missing Info\n"
        "_What BugLens cannot determine from the screenshot alone:_\n\n"
        f"{items}"
    )


def regression_tests_card(report: BugReport) -> str:
    """Markdown for the Regression Tests card."""

    rows = "\n".join(f"- **{test.id}** — {test.desc}" for test in report.regression_tests)
    return f"### Regression Tests\n\n{rows}"


def edge_cases_card(report: BugReport) -> str:
    """Markdown for the Edge Cases card."""

    rows = "\n".join(f"- {item}" for item in report.edge_cases)
    return f"### Edge Cases\n\n{rows}"
