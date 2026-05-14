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


ADMIN_COLUMNS: list[str] = [
    "WebID",
    "Full Name",
    "Nickname",
    "Chinese Name",
    "Website Section",
    "Admission Year",
    "Graduated",
    "Also in Alumni",
    "Alumni Admission Year",
    "Current Position",
    "Batch",
]


def write_slim_excel(legacy_path: Path, slim_path: Path) -> None:
    """Read the legacy workbook; write a new workbook keeping only the 11
    ADMIN_COLUMNS (in the order defined by that constant)."""
    import openpyxl
    src_wb = openpyxl.load_workbook(legacy_path, data_only=True)
    src_ws = src_wb["Members"]
    src_headers = [c.value for c in src_ws[1]]

    keep_indices = []
    for col in ADMIN_COLUMNS:
        if col not in src_headers:
            raise ValueError(f"Legacy Excel missing required admin column: {col!r}")
        keep_indices.append(src_headers.index(col))

    out_wb = openpyxl.Workbook()
    out_ws = out_wb.active
    out_ws.title = "Members"
    out_ws.append(ADMIN_COLUMNS)
    for row in src_ws.iter_rows(min_row=2, values_only=True):
        out_ws.append([row[i] for i in keep_indices])

    out_wb.save(slim_path)


_EMPTY_MEMBER_JSON: dict = {
    "position": "",
    "email": {"ntu": "", "preferred": ""},
    "interests": [],
    "links": {
        "scholar": "",
        "orcid": "",
        "linkedin": "",
        "researchgate": "",
        "ntu_scholars": "",
        "office": {"text": "", "url": ""},
    },
    "metaDescription": "",
}

_TEMPLATE_ABOUT_MD = """# Your name here

Write your bio in this file. You can use Markdown:

- **bold** with `**bold**`
- *italics* with `*italics*`
- [links](https://example.com) with `[text](url)`

Multiple paragraphs are fine. This is the prose that appears in the "About"
section of your member page.

(Delete this placeholder text and write your bio here.)
"""

_TEMPLATE_README_MD = """# Updating your E3 Center profile

Edit **two files** and send them back to the maintainer:

1. **`member.json`** — your position, emails, interests, profile links.
   - Replace the string values. Don't delete keys or rearrange.
   - Leave any field as `""` to hide it on the website.
   - `interests` is a list — add or remove items as you like (1–5 typical).
2. **`about.md`** — your biographical paragraphs. Plain Markdown:
   - `**bold**`, `*italics*`, `[links](https://example.com)`
   - Blank line = new paragraph
   - `- item` for bullets

Send both files back when done. Do not edit anything in `member-info.xlsx`
— your admin info (name, batch, section) is handled separately.
"""


def write_member_template(dest: Path) -> None:
    """Create dest/ (typically contents/MEMBER_TEMPLATE/) with the three
    skeleton files maintainers send to new members."""
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "member.json").write_text(
        _json.dumps(_EMPTY_MEMBER_JSON, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (dest / "about.md").write_text(_TEMPLATE_ABOUT_MD, encoding="utf-8")
    (dest / "README.md").write_text(_TEMPLATE_README_MD, encoding="utf-8")
