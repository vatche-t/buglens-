"""Tests for the deterministic BugLens exports."""

import csv
import io

import pytest

from buglens import render
from buglens.schema import BugReport


@pytest.fixture
def report() -> BugReport:
    return BugReport(
        app="Checkout",
        title="Pay button stays disabled with a valid card",
        blurb="Card fields filled, but Pay won't enable.",
        severity="high",
        severity_why="Blocks revenue on the final checkout step.",
        vision_read=["A greyed Pay $49.00 button."],
        summary="The Pay button stays disabled though the card fields look complete.",
        steps=["Open checkout", "Enter a valid card", "Observe Pay stays disabled"],
        expected="Pay becomes enabled with a valid card.",
        actual="Pay never enables.",
        env=[
            {"key": "Visible in screenshot", "value": "Payment step", "known": True},
            {"key": "Browser / OS", "value": "not visible — please confirm", "known": False},
        ],
        missing_info=[
            {"question": "Does the field strip spaces?", "why": "Spaces may fail length checks."}
        ],
        regression_tests=[
            {
                "id": "REG-001",
                "title": "Spaced card enables Pay",
                "given": "I am on the Payment step",
                # A comma forces the CSV writer to quote this field.
                "when": "I enter a valid card, with spaces",
                "then": "the Pay button is enabled",
            }
        ],
        edge_cases=[{"title": "Amex 15-digit", "detail": "A 16-digit rule rejects valid Amex."}],
    )


def test_jira_markdown_includes_structure_and_severity(report: BugReport) -> None:
    out = render.to_jira_markdown(report)

    assert out.startswith("h2. Pay button stays disabled with a valid card")
    assert "*Severity:* High — Blocks revenue" in out
    assert "h3. Missing Info" in out
    assert "# Open checkout" in out
    assert "REG-001 Spaced card enables Pay" in out
    # Unconfirmed env rows are flagged.
    assert "_(unconfirmed)_" in out


def test_github_issue_uses_checkboxes_and_numbered_steps(report: BugReport) -> None:
    out = render.to_github_issue(report)

    assert out.startswith("# Pay button stays disabled with a valid card")
    assert "1. Open checkout" in out
    assert "- [ ] **Does the field strip spaces?**" in out
    assert "_Given_ I am on the Payment step" in out


def test_csv_has_gherkin_header_and_escapes_commas(report: BugReport) -> None:
    out = render.regression_tests_to_csv(report)

    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["id", "title", "given", "when", "then"]
    assert len(rows) == 2
    # The comma-containing "when" survives a round-trip through the parser.
    assert rows[1] == [
        "REG-001",
        "Spaced card enables Pay",
        "I am on the Payment step",
        "I enter a valid card, with spaces",
        "the Pay button is enabled",
    ]
    assert "\r" not in out


def test_exports_are_deterministic(report: BugReport) -> None:
    assert render.to_jira_markdown(report) == render.to_jira_markdown(report)
    assert render.regression_tests_to_csv(report) == render.regression_tests_to_csv(report)
