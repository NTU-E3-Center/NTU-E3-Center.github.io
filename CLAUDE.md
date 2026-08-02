# Repo conventions for Claude

Quick rules to follow when editing this repo. Read once, then act accordingly.

## Publication dates — use the journal issue date, not "available online"

When populating or updating an entry in [contents/publications/publications.json](contents/publications/publications.json), the `month` and `year` fields **must reflect the journal's issue date**, not any of these other dates that frequently appear on a paper's first page:

- ❌ "Available online 20 April 2026"
- ❌ "Received / Revised / Accepted ..." dates
- ❌ "Version of Record" date
- ❌ "Early access" date
- ✅ The issue date — i.e. what the publisher lists as the **issue/volume cover date**

Examples:
- *Energy Economics* **Vol. 158, June 2026** → `"year": "'26"`, `"month": "Jun."` (even if available online April 2026)
- *Atmospheric Pollution Research* **Vol. 17, Issue 6, June 2026** → `"month": "Jun."`, `"issue": "6"` (even if available online January 2026)

**Where to find it:** On Elsevier/ScienceDirect papers, look for the cover-date line on the journal's article page (e.g. "Energy Economics · Volume 158 · June 2026 · 109355"). The PDF's "Available online" date in the footer is almost always different and is NOT what we want.

**Why this matters:** A paper available online in April but printed in the June issue is cited as a June paper. Authors' CV pages, BibTeX, and reverse-chronological sort order all rely on the issue date.

## Other quick conventions

- **`status` field:** member CV pages only render publications with `status == "published"` AND a non-empty `citationId`. Unpublished entries (`status: "working"`, etc.) are hidden from member pages by design — see [build.py:307-315](build.py#L307-L315). The public `/publications/` page also excludes `status == "working"` entries (filtered at the single funnel in [templates/pages/publications.html](templates/pages/publications.html), PR #52) — manuscripts stay tracked in `publications.json` but are not published anywhere on the site; a paper appears automatically the moment its status flips to `"published"`.
- **Uniform JSON keys per entry:** within `member.json` (and other list-of-entries schemas), all entries in a list must share the same keys. Use empty strings for blank values rather than omitting keys.
- **Chinese title support:** for Taiwan-journal papers, populate `titleZh` and `journalZh`. The detail page renders Chinese title beneath the English h1 in Noto Sans TC; no template work needed per-paper.
