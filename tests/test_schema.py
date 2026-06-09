"""Tests for the BugLens output schema and its UI serialization."""

import pytest
from pydantic import ValidationError

from buglens.schema import BugReport, Severity


def make_report(**overrides) -> BugReport:
    data = dict(
        app="Checkout",
        title="Pay button stays disabled with a valid card",
        blurb="Card fields filled, but Pay won't enable.",
        severity="high",
        severity_why="Blocks revenue on the final checkout step.",
        vision_read=["A checkout panel titled Payment.", "A greyed Pay $49.00 button."],
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
                "id": "reg-001",
                "title": "Spaced card enables Pay",
                "given": "I am on the Payment step",
                "when": "I enter a valid spaced card number",
                "then": "the Pay button is enabled",
            }
        ],
        edge_cases=[{"title": "Amex 15-digit", "detail": "A 16-digit rule rejects valid Amex."}],
    )
    data.update(overrides)
    return BugReport(**data)


def test_accepts_valid_payload_and_normalizes() -> None:
    report = make_report()
    assert report.severity is Severity.HIGH
    # Test IDs are upper-cased for stable CSV export.
    assert report.regression_tests[0].id == "REG-001"


def test_rejects_empty_missing_info() -> None:
    with pytest.raises(ValidationError):
        make_report(missing_info=[])


def test_rejects_invalid_severity() -> None:
    with pytest.raises(ValidationError):
        make_report(severity="P1")


def test_to_ui_payload_uses_frontend_keys() -> None:
    payload = make_report().to_ui_payload()

    # Aliases match exactly what buglens-ui reads.
    assert payload["severityWhy"]
    assert payload["visionRead"][0].startswith("A checkout panel")
    assert payload["missing"][0]["q"] == "Does the field strip spaces?"
    assert payload["missing"][0]["why"]
    assert payload["tests"][0]["given"].startswith("I am on")
    assert payload["edges"][0]["t"] == "Amex 15-digit"
    assert payload["env"][1]["known"] is False
    # exclude_none drops the unset optional id.
    assert "id" not in payload
