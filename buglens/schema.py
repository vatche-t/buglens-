"""Validated output contracts for BugLens.

This is the single contract every layer passes through: the model structuring
call fills it, validation guards it, the renderers export it, and the custom
frontend consumes its JSON. Field shapes mirror the `buglens-ui` prototype, and
serialization aliases emit the exact JSON keys that frontend already reads
(``severityWhy``, ``visionRead``, ``missing``/``q``/``why``, ``tests`` with
Gherkin ``given``/``when``/``then``, ``edges``/``t``/``d``, ``env``/``k``/``v``).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(StrEnum):
    """Four-level severity matching the UI severity tokens."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


def _strip(value: str) -> str:
    return value.strip()


class EnvFact(BaseModel):
    """One row of the environment table; `known` drives the confirm styling."""

    key: str = Field(min_length=1, serialization_alias="k")
    value: str = Field(min_length=1, serialization_alias="v")
    known: bool


class MissingInfo(BaseModel):
    """A thing BugLens cannot determine from the screenshot, plus why it matters."""

    question: str = Field(min_length=1, serialization_alias="q")
    why: str = Field(min_length=1)


class RegressionTest(BaseModel):
    """A runnable regression test expressed in Given/When/Then form."""

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    given: str = Field(min_length=1)
    when: str = Field(min_length=1)
    then: str = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        """Keep test IDs compact and consistent for CSV export."""

        return value.strip().upper()


class EdgeCase(BaseModel):
    """A practical risk worth checking, with a short detail."""

    title: str = Field(min_length=1, serialization_alias="t")
    detail: str = Field(min_length=1, serialization_alias="d")


class BugReport(BaseModel):
    """The full structured artifact produced from one screenshot + tester note."""

    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    app: str = Field(min_length=1)
    title: str = Field(min_length=1)
    blurb: str = Field(min_length=1)
    severity: Severity
    severity_why: str = Field(min_length=1, serialization_alias="severityWhy")
    captured: str | None = None
    vision_read: list[str] = Field(min_length=1, serialization_alias="visionRead")
    summary: str = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    expected: str = Field(min_length=1)
    actual: str = Field(min_length=1)
    env: list[EnvFact] = Field(min_length=1)
    missing_info: list[MissingInfo] = Field(min_length=1, serialization_alias="missing")
    regression_tests: list[RegressionTest] = Field(min_length=1, serialization_alias="tests")
    edge_cases: list[EdgeCase] = Field(min_length=1, serialization_alias="edges")

    @field_validator("app", "title", "blurb", "severity_why", "summary", "expected", "actual")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Normalize required free-text fields."""

        return value.strip()

    @field_validator("vision_read", "steps")
    @classmethod
    def strip_required_lines(cls, values: list[str]) -> list[str]:
        """Normalize required string lists and reject all-empty input."""

        cleaned = [item.strip() for item in values if item.strip()]
        if not cleaned:
            raise ValueError("list must contain at least one non-empty item")
        return cleaned

    def to_ui_payload(self) -> dict:
        """Serialize to the exact JSON shape the buglens-ui frontend consumes."""

        return self.model_dump(by_alias=True, exclude_none=True)
