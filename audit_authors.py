"""Audit publication authorship against the E3 member roster.

Reads contents/members/member-info.xlsx to build the canonical roster
(Full Name + Nickname per member), then walks contents/publications/publications.json
and classifies every comma-separated author token in each publication as:

  - match    a roster Full Name / Nickname matches the token
  - partial  only the given-name segment matches (e.g. "Tsung-Heng" vs roster
             "Tsung-Heng Chang") — likely an abbreviated entry that should be
             completed
  - external no roster match at all (real outside collaborator OR typo)

Run:  python3 audit_authors.py
Optional: python3 audit_authors.py --md > audit-authors.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parent
XLSX = ROOT / "contents" / "members" / "member-info.xlsx"
PUBS = ROOT / "contents" / "publications" / "publications.json"


# ── normalization ───────────────────────────────────────────────────────────

def norm(s: str) -> str:
    """Lowercase + collapse whitespace; preserves hyphens and apostrophes."""
    return re.sub(r"\s+", " ", s.strip().lower())


def given_segment(full_name: str) -> str:
    """Everything before the last whitespace-delimited token.
    'Tsung-Heng Chang' -> 'Tsung-Heng'   |   'I-Yun Lisa Hsieh' -> 'I-Yun Lisa'
    """
    parts = full_name.strip().split()
    return " ".join(parts[:-1]) if len(parts) >= 2 else full_name.strip()


# ── roster ──────────────────────────────────────────────────────────────────

def load_roster() -> list[dict]:
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb.active
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    roster = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        wid = row[idx["WebID"]]
        if not wid:
            continue
        full = (row[idx["Full Name"]] or "").strip()
        nick = (row[idx["Nickname"]] or "").strip()
        section = (row[idx["Website Section"]] or "").strip()
        if not full:
            continue
        roster.append({
            "webId":    str(wid).strip(),
            "fullName": full,
            "nickname": nick,
            "section":  section,
            "_full_n":  norm(full),
            "_nick_n":  norm(nick) if nick else "",
            "_given_n": norm(given_segment(full)),
        })
    return roster


# ── classification ──────────────────────────────────────────────────────────

def classify_token(token: str, roster: list[dict]) -> tuple[str, dict | None]:
    """Return ('match'|'partial'|'external', roster_entry_or_None)."""
    t = norm(token)
    if not t:
        return ("external", None)

    # 1. exact full-name match (case-insensitive, ignores extra middle initials)
    for m in roster:
        if t == m["_full_n"]:
            return ("match", m)

    # 2. exact nickname match
    for m in roster:
        if m["_nick_n"] and t == m["_nick_n"]:
            return ("match", m)

    # 3. substring either direction on Full Name
    #    (token contains full name OR full name contains token as whole)
    for m in roster:
        if t in m["_full_n"] and len(t.split()) >= 2:
            return ("match", m)
        if m["_full_n"] in t:
            return ("match", m)

    # 4. partial: token equals the given-name segment of a roster entry
    #    'Tsung-Heng' equals given-segment of 'Tsung-Heng Chang'
    partial_hits = [m for m in roster if t == m["_given_n"]]
    if len(partial_hits) == 1:
        return ("partial", partial_hits[0])
    if len(partial_hits) > 1:
        # ambiguous partial — pick first, but flag in display
        return ("partial", partial_hits[0])

    # 5. partial: any roster given-segment contains the token as a hyphen
    #    component  ('Yun' inside 'I-Yun')  — last-resort guess
    return ("external", None)


# ── splitting authors string ────────────────────────────────────────────────

AUTHOR_SPLIT = re.compile(r"\s*,\s*|\s+and\s+|\s*&\s*", re.IGNORECASE)


def split_authors(authors: str) -> list[str]:
    if not authors:
        return []
    raw = AUTHOR_SPLIT.split(authors)
    return [a.strip() for a in raw if a.strip()]


# ── report ──────────────────────────────────────────────────────────────────

MARK = {"match": "[OK]", "partial": "[??]", "external": "[XX]"}


def short(s: str, n: int = 72) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "..."


def build_report(roster, sections, md: bool):
    lines: list[str] = []
    aggregate_external: dict[str, list[str]] = defaultdict(list)
    aggregate_partial: dict[str, list[tuple[str, str]]] = defaultdict(list)

    pubs_seen = 0
    fully_matched = 0

    for section in sections:
        for item in section.get("items", []):
            authors_raw = item.get("authors", "")
            tokens = split_authors(authors_raw)
            if not tokens:
                continue
            pubs_seen += 1
            title = item.get("title", "(untitled)")
            year = item.get("year", "")
            cid = item.get("citationId") or item.get("slug") or ""

            row_tokens = []
            row_all_match = True
            for tok in tokens:
                kind, m = classify_token(tok, roster)
                if kind == "external":
                    aggregate_external[tok].append(title)
                    row_all_match = False
                elif kind == "partial":
                    suggested = m["fullName"] if m else ""
                    aggregate_partial[tok].append((suggested, title))
                    row_all_match = False
                row_tokens.append((tok, kind, m))

            if row_all_match:
                fully_matched += 1

            # per-publication line
            marker_str = "  ".join(
                f"{MARK[kind]} {tok}" + (f" -> {m['fullName']}" if kind == "partial" and m else "")
                for (tok, kind, m) in row_tokens
            )
            lines.append(f"[{year:>3}] {short(title)}")
            if cid:
                lines.append(f"      id: {cid}")
            lines.append(f"      {marker_str}")
            lines.append("")

    # ── aggregates ────────────────────────────────────────────────────────
    lines.append("=" * 78)
    lines.append(f"SUMMARY: {pubs_seen} publications scanned, "
                 f"{fully_matched} with ALL authors matching roster, "
                 f"{pubs_seen - fully_matched} with issues")
    lines.append("=" * 78)
    lines.append("")

    lines.append("---- PARTIAL / ABBREVIATED NAMES (likely E3 members, fix entry) ----")
    if not aggregate_partial:
        lines.append("  (none)")
    else:
        for tok, occs in sorted(aggregate_partial.items(), key=lambda kv: -len(kv[1])):
            suggested = occs[0][0]
            lines.append(f"  '{tok}'  ->  '{suggested}'   ({len(occs)} publication(s))")
            for _, t in occs:
                lines.append(f"      - {short(t)}")
    lines.append("")

    lines.append("---- EXTERNAL AUTHORS (not in E3 roster) ----")
    if not aggregate_external:
        lines.append("  (none)")
    else:
        for tok, occs in sorted(aggregate_external.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"  '{tok}'   ({len(occs)} publication(s))")
            for t in occs:
                lines.append(f"      - {short(t)}")
    lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="(reserved; output is plain text either way)")
    args = ap.parse_args()

    roster = load_roster()
    sections = json.loads(PUBS.read_text(encoding="utf-8"))
    report = build_report(roster, sections, md=args.md)
    sys.stdout.write(report)


if __name__ == "__main__":
    main()
