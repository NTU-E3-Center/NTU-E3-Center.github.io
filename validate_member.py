"""Per-member folder validation for the build pipeline.

Used by excel_to_content.py to verify contents/members/{webId}/ folders
before the build proceeds. Errors fail the build; warnings log but
allow the build to continue (so a half-onboarded new member does not
block deploys)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ValidationIssue:
    severity: str   # "error" | "warn"
    message: str

    def __post_init__(self) -> None:
        if self.severity not in ("error", "warn"):
            raise ValueError(f"severity must be 'error' or 'warn', got {self.severity!r}")


def validate_member_folder(web_id: str, folder: Path) -> list[ValidationIssue]:
    """Inspect a per-member content folder and return any issues found.

    Empty list = OK. See severities in the dataclass docstring above."""
    issues: list[ValidationIssue] = []

    if not folder.is_dir():
        issues.append(ValidationIssue(
            "warn",
            f"{folder}: folder missing — build will render a placeholder profile.",
        ))
        return issues

    member_json = folder / "member.json"
    if not member_json.exists():
        issues.append(ValidationIssue(
            "warn",
            f"{member_json}: member.json missing — profile will render with defaults.",
        ))
    else:
        try:
            with member_json.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                "error",
                f"{member_json}: invalid JSON — line {e.lineno}, column {e.colno}: {e.msg}",
            ))
            data = None
        # data is now either a parsed dict or None; schema check uses it in Task 5.

    return issues
