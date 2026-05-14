"""One-time migration: extract existing per-member content from the legacy
22-column Excel + members-{about,position,interest}/*.md into the new
contents/members/{webId}/ folder structure.

Run from the repo root:
    python migrate_to_per_member_folders.py
    python migrate_to_per_member_folders.py --force      # overwrite existing folders
    python migrate_to_per_member_folders.py --dry-run

Idempotent: re-running without --force will refuse to clobber existing
content folders.
"""
from __future__ import annotations


import json as _json
import shutil
from pathlib import Path
from typing import Mapping, Any


def parse_interests_from_slash_md(md: str) -> list[str]:
    """Parse the existing /Topic A\\n/Topic B format into ['Topic A', 'Topic B']."""
    out: list[str] = []
    for line in (md or "").splitlines():
        s = line.strip()
        if s.startswith("/"):
            out.append(s.lstrip("/").strip())
    return out


def _s(value: Any) -> str:
    """Coerce Excel cell value → trimmed string, empty when None/blank."""
    if value is None:
        return ""
    return str(value).strip()


def build_member_json(row: Mapping[str, Any]) -> dict[str, Any]:
    """Build the all-keys-present member.json dict from a legacy Excel row.

    `row` is keyed by the legacy 22-column names (e.g. 'NTU Email', 'Scholar').
    Missing columns default to empty values — never raises."""
    return {
        "position": _s(row.get("Position / Education")),
        "email": {
            "ntu":       _s(row.get("NTU Email")),
            "preferred": _s(row.get("Preferred Email")),
        },
        "interests": parse_interests_from_slash_md(_s(row.get("Research Interests"))),
        "links": {
            "scholar":      _s(row.get("Scholar")),
            "orcid":        _s(row.get("ORCID")),
            "linkedin":     _s(row.get("LinkedIn")),
            "researchgate": _s(row.get("ResearchGate")),
            "ntu_scholars": _s(row.get("NTU Scholars")),
            "office": {
                "text": _s(row.get("Office")),
                "url":  _s(row.get("Office Map")),
            },
        },
        "metaDescription": _s(row.get("metaDescription")),
    }


def write_member_folder(
    *,
    dest: Path,
    member_json: dict,
    about_md_src: Path | None,
    photo_src: Path | None,
) -> None:
    """Create dest/ and write member.json (+ optionally about.md, photo.{ext}).

    Files are overwritten if they already exist (caller controls --force at
    the CLI level; at the unit level this function is unconditional)."""
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "member.json").write_text(
        _json.dumps(member_json, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if about_md_src is not None and about_md_src.exists():
        (dest / "about.md").write_text(
            about_md_src.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    if photo_src is not None and photo_src.exists():
        ext = photo_src.suffix.lower()
        shutil.copyfile(photo_src, dest / f"photo{ext}")
