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


# Schema describes member.json shape. Leaves (str, list[str]) are the types;
# branch dicts describe nested structures recursively.
_SCHEMA: dict[str, Any] = {
    "position": str,
    "email": {
        "ntu": str,
        "preferred": str,
    },
    "interests": [str],   # list of strings
    "links": {
        "scholar": str,
        "orcid": str,
        "linkedin": str,
        "researchgate": str,
        "ntu_scholars": str,
        "office": {
            "text": str,
            "url": str,
        },
    },
    "metaDescription": str,
}


_URL_LINK_KEYS = ("scholar", "orcid", "linkedin", "researchgate", "ntu_scholars")


def _check_soft_formats(data: dict) -> list[ValidationIssue]:
    """URL / email format warnings. These never fail the build."""
    issues: list[ValidationIssue] = []
    links = data.get("links") or {}

    for key in _URL_LINK_KEYS:
        val = links.get(key)
        if isinstance(val, str) and val and not val.startswith(("http://", "https://")):
            issues.append(ValidationIssue(
                "warn",
                f"links.{key}: '{val}' does not start with http:// or https:// — render will be unchanged but the link may not work.",
            ))

    office = links.get("office") or {}
    office_url = office.get("url")
    if isinstance(office_url, str) and office_url and not office_url.startswith(("http://", "https://")):
        issues.append(ValidationIssue(
            "warn",
            f"links.office.url: '{office_url}' does not start with http:// or https://.",
        ))

    email = data.get("email") or {}
    for key in ("ntu", "preferred"):
        val = email.get(key)
        if isinstance(val, str) and val and "@" not in val:
            issues.append(ValidationIssue(
                "warn",
                f"email.{key}: '{val}' missing '@' — does this look right?",
            ))

    return issues


def _check_schema(data: Any, schema: Any, path: str) -> list[ValidationIssue]:
    """Recursively validate `data` against `schema`. Returns flat issue list.

    Schema rules:
    - schema is `str` → data must be a `str`
    - schema is `[str]` → data must be a list, every element must be `str`
    - schema is dict → data must be dict; recurse for each key. Keys present
      in schema but absent in data are NOT errors here — empty/missing fields
      are tolerated. (The build's rendering layer hides absent fields.)
    """
    issues: list[ValidationIssue] = []

    if schema is str:
        if not isinstance(data, str):
            issues.append(ValidationIssue(
                "error",
                f"At '{path}': expected string, got {type(data).__name__}",
            ))
    elif isinstance(schema, list) and len(schema) == 1 and schema[0] is str:
        if not isinstance(data, list):
            issues.append(ValidationIssue(
                "error",
                f"At '{path}': expected list of strings, got {type(data).__name__}",
            ))
        else:
            for i, item in enumerate(data):
                if not isinstance(item, str):
                    issues.append(ValidationIssue(
                        "error",
                        f"At '{path}[{i}]': expected string, got {type(item).__name__}",
                    ))
    elif isinstance(schema, dict):
        if not isinstance(data, dict):
            issues.append(ValidationIssue(
                "error",
                f"At '{path}': expected object, got {type(data).__name__}",
            ))
        else:
            for key, subschema in schema.items():
                if key in data:
                    sub_path = f"{path}.{key}" if path else key
                    issues.extend(_check_schema(data[key], subschema, sub_path))

    return issues


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

        if data is not None:
            issues.extend(_check_schema(data, _SCHEMA, path=""))
            if isinstance(data, dict):
                issues.extend(_check_soft_formats(data))

    if not (folder / "about.md").exists():
        issues.append(ValidationIssue(
            "warn",
            f"{folder}/about.md: missing — About section will be hidden on the profile page.",
        ))

    photo_exts = (".jpg", ".jpeg", ".png")
    photos = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in photo_exts and p.stem == "photo"]
    if not photos:
        issues.append(ValidationIssue(
            "warn",
            f"{folder}: no photo.(jpg|jpeg|png) found — default silhouette will be used.",
        ))

    return issues
