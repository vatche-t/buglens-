"""Tests for the structuring call: parsing, validation, retry, and failure."""

import json

import pytest

from buglens import structure
from buglens.examples import EXAMPLES
from buglens.prompts import STRUCTURE_PROMPT
from buglens.schema import BugReport

# Field-name JSON (model_dump default) is exactly what the model is asked to emit.
VALID_JSON = json.dumps(EXAMPLES["payment"].model_dump())


def test_structure_prompt_enforces_quality_floors() -> None:
    # Guard the hardening rules so they can't silently regress.
    assert "Never claim data loss" in STRUCTURE_PROMPT
    assert 'critical" ONLY' in STRUCTURE_PROMPT
    assert "missing_info is the most important field" in STRUCTURE_PROMPT
    assert STRUCTURE_PROMPT.count("at least 3") >= 2  # regression_tests and edge_cases


def test_extract_json_strips_fences_and_prose() -> None:
    fenced = "```json\n{\"a\": 1}\n```"
    assert structure.extract_json(fenced) == '{"a": 1}'

    chatty = 'Sure! Here you go:\n{"a": 1}\nHope that helps.'
    assert structure.extract_json(chatty) == '{"a": 1}'


def test_extract_json_raises_when_absent() -> None:
    with pytest.raises(ValueError):
        structure.extract_json("no json here")


def test_parse_report_round_trips() -> None:
    report = structure.parse_report(VALID_JSON)
    assert isinstance(report, BugReport)
    assert report.app == "Checkout"


def test_fallback_report_preserves_quality_floors_without_overclaiming() -> None:
    observation = """Visible facts:
    - The screen is a checkout payment page.
    - The card number field is filled.
    - The Pay button appears disabled.

    Not visible:
    - Browser, OS, environment, API response, and affected users are not visible.
    """
    report = structure.fallback_report(
        observation,
        "Pay button stays disabled after entering a valid test card.",
    )

    assert report.severity.value == "high"
    assert report.app == "Checkout"
    assert len(report.missing_info) >= 3
    assert len(report.regression_tests) >= 3
    assert len(report.edge_cases) >= 3
    assert len(report.vision_read) >= 3
    no_overclaims = f"{report.summary} {report.severity_why}".lower()
    assert "data loss" not in no_overclaims
    assert "security" not in no_overclaims
    assert "privacy" not in no_overclaims
    assert "model json" not in f"{report.blurb} {report.summary}".lower()


def test_fallback_report_stays_medium_when_impact_is_unclear() -> None:
    report = structure.fallback_report(
        "Visible facts:\n- A settings screen shows a blank panel.",
        "",
    )

    assert report.severity.value == "medium"
    assert report.app == "Application"
    assert any(not item.known for item in report.env)


# ── fakes that return queued decode outputs ──
class _FakeTensor:
    shape = (1, 3)


class _FakeInputs(dict):
    def to(self, _device):
        return self


class _SeqProcessor:
    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.calls = 0

    def apply_chat_template(self, messages, **kwargs):
        self.last_messages = messages
        return _FakeInputs(input_ids=_FakeTensor())

    def decode(self, _ids, **kwargs):
        out = self._outputs[self.calls]
        self.calls += 1
        return out


class _FakeModel:
    device = "cpu"

    def generate(self, **kwargs):
        return [[0, 1, 2, 3]]


def test_structure_parses_on_first_try() -> None:
    processor = _SeqProcessor([VALID_JSON])
    report = structure.structure(_FakeModel(), processor, "obs", "note")
    assert report.app == "Checkout"
    assert processor.calls == 1  # no retry needed


def test_structure_retries_once_then_succeeds() -> None:
    processor = _SeqProcessor(["not json at all", VALID_JSON])
    report = structure.structure(_FakeModel(), processor, "obs")
    assert isinstance(report, BugReport)
    assert processor.calls == 2  # retried exactly once


def test_structure_raises_after_failed_retry() -> None:
    processor = _SeqProcessor(["garbage", "{bad json"])
    with pytest.raises(structure.StructureError) as exc:
        structure.structure(_FakeModel(), processor, "obs")
    assert processor.calls == 2
    assert exc.value.raw == "{bad json"  # last raw output preserved for the UI
