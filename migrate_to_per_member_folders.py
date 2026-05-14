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


def parse_interests_from_slash_md(md: str) -> list[str]:
    """Parse the existing /Topic A\\n/Topic B format into ['Topic A', 'Topic B']."""
    out: list[str] = []
    for line in (md or "").splitlines():
        s = line.strip()
        if s.startswith("/"):
            out.append(s.lstrip("/").strip())
    return out
