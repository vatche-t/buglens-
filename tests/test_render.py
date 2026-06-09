"""Tests for the deterministic BugLens renderers and exports."""

import csv
import io

import pytest

from buglens import render
from buglens.schema import BugReport


@pytest.fixture
def report() -> BugReport:
    return BugReport(
        title="Deposit button does not respond",
        severity="P1",
        component="Payments",
        steps=["Open deposit page", "Enter a valid amount", "Click Deposit"],
        expected="Deposit request is submitted or a clear error appears.",
        actual="The Deposit button appears unresponsive.",
        missing_info=[
            "Confirm browser and version; not visible in the screenshot.",
            "Confirm whether this is production or staging.",
        ],
        regression_tests=[
            {"id": "TC-001", "desc": "Verify deposit submits with valid input."},
            # A comma forces the CSV writer to quote the field.
            {"id": "TC-002", "desc": "Verify duplicate clicks, no duplicate requests."},
        ],
        edge_cases=["Double-clicking Deposit should not create duplicate requests."],
    )


def test_jira_markdown_includes_structure_and_severity(report: BugReport) -> None:
    out = render.to_jira_markdown(report)

    assert out.startswith("h2. Deposit button does not respond")
    assert "*Severity:* P1" in out
    assert "h3. Missing Info" in out
    # Steps render as Jira numbered list markers.
    assert "# Open deposit page" in out
    assert "* TC-001: Verify deposit submits with valid input." in out


def test_github_issue_uses_markdown_checkboxes_and_numbered_steps(report: BugReport) -> None:
    out = render.to_github_issue(report)

    assert out.startswith("# Deposit button does not respond")
    assert "1. Open deposit page" in out
    assert "3. Click Deposit" in out
    # Missing info renders as actionable checkboxes.
    assert "- [ ] Confirm whether this is production or staging." in out
    assert "- **TC-002**:" in out


def test_csv_has_header_and_escapes_commas(report: BugReport) -> None:
    out = render.regression_tests_to_csv(report)

    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["id", "description"]
    assert len(rows) == 3
    assert rows[1] == ["TC-001", "Verify deposit submits with valid input."]
    # The comma-containing description survives a round-trip through the parser.
    assert rows[2] == ["TC-002", "Verify duplicate clicks, no duplicate requests."]
    # Deterministic line endings.
    assert "\r" not in out


def test_renderers_are_deterministic(report: BugReport) -> None:
    assert render.to_jira_markdown(report) == render.to_jira_markdown(report)
    assert render.regression_tests_to_csv(report) == render.regression_tests_to_csv(report)


def test_cards_render_expected_headers(report: BugReport) -> None:
    assert render.bug_report_card(report).startswith("### Deposit button does not respond")
    assert "Missing Info" in render.missing_info_card(report)
    assert "cannot determine" in render.missing_info_card(report)
    assert "TC-001" in render.regression_tests_card(report)
    assert "### Edge Cases" in render.edge_cases_card(report)
