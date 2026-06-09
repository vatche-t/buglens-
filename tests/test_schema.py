"""Tests for the BugLens output schema."""

import pytest
from pydantic import ValidationError

from buglens.schema import BugReport, Severity


def test_bug_report_accepts_valid_payload() -> None:
    report = BugReport(
        title="Deposit button does not respond",
        severity="P1",
        component="Payments",
        steps=["Open deposit page", "Enter a valid amount", "Click Deposit"],
        expected="Deposit request is submitted or a clear error appears.",
        actual="The Deposit button appears unresponsive.",
        missing_info=["Confirm browser and version.", "Confirm production or staging."],
        regression_tests=[
            {"id": "tc-001", "desc": "Verify deposit button submits with valid input."}
        ],
        edge_cases=["Double-clicking Deposit should not create duplicate requests."],
    )

    assert report.severity is Severity.P1
    assert report.regression_tests[0].id == "TC-001"


def test_bug_report_rejects_empty_missing_info() -> None:
    with pytest.raises(ValidationError):
        BugReport(
            title="Dashboard is blank",
            severity="P3",
            component="Dashboard",
            steps=["Open dashboard"],
            expected="Dashboard shows widgets or a useful empty state.",
            actual="Dashboard is blank.",
            missing_info=[],
            regression_tests=[{"id": "TC-001", "desc": "Verify dashboard loads widgets."}],
            edge_cases=["Empty accounts should show an empty state."],
        )
