"""Validated output contracts for BugLens."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Severity(StrEnum):
    """Supported QA severity values."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class RegressionTest(BaseModel):
    """A single runnable regression test idea."""

    id: str = Field(min_length=1, examples=["TC-001"])
    desc: str = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def normalize_test_id(cls, value: str) -> str:
        """Keep test IDs compact and consistent for CSV export."""

        return value.strip().upper()


class BugReport(BaseModel):
    """The single structured artifact passed through the app."""

    title: str = Field(min_length=1)
    severity: Severity
    component: str = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    expected: str = Field(min_length=1)
    actual: str = Field(min_length=1)
    missing_info: list[str] = Field(min_length=1)
    regression_tests: list[RegressionTest] = Field(min_length=1)
    edge_cases: list[str] = Field(min_length=1)

    @field_validator("title", "component", "expected", "actual")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Normalize required text fields."""

        return value.strip()

    @field_validator("steps", "missing_info", "edge_cases")
    @classmethod
    def strip_required_list(cls, values: list[str]) -> list[str]:
        """Normalize required string lists and reject empty items."""

        cleaned = [item.strip() for item in values if item.strip()]
        if not cleaned:
            raise ValueError("list must contain at least one non-empty item")
        return cleaned
