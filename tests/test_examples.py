"""Tests for the built-in example reports."""

from buglens.examples import EXAMPLES, get_example, list_examples
from buglens.schema import BugReport


def test_all_examples_are_valid_reports() -> None:
    # Construction happens at import; this guards the count and types.
    assert set(EXAMPLES) == {"payment", "dashboard", "signup", "settings"}
    assert all(isinstance(r, BugReport) for r in EXAMPLES.values())


def test_list_examples_exposes_gallery_metadata() -> None:
    rows = list_examples()
    assert len(rows) == 4
    payment = rows[0]
    assert payment["id"] == "payment"
    assert payment["severity"] == "high"
    assert set(payment) == {"id", "app", "title", "blurb", "severity", "captured"}


def test_get_example_known_and_unknown() -> None:
    assert get_example("payment").app == "Checkout"
    assert get_example("nope") is None


def test_example_payload_matches_frontend_keys() -> None:
    payload = get_example("payment").to_ui_payload()
    assert payload["id"] == "payment"
    assert payload["missing"][0]["q"]
    assert payload["tests"][0]["given"]
    assert payload["edges"][0]["t"]
    assert payload["env"][1]["known"] is False
