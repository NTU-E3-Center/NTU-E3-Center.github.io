# Per-Member Content Restructure — Design

**Date:** 2026-05-13
**Status:** Draft (awaiting user approval)
**Branch (recommended for implementation):** `feat/member-content-restructure` from `source`

---

## 1. Motivation

Today every member's data is spread across **five locations** in `contents/`:

| Location | Holds |
|---|---|
| `contents/member-info.xlsx` (one row, 22 columns) | Everything — admin fields + content fields conflated |
| `contents/structures/members/{webId}.json` | Auto-generated per-member structured data (links, sections) |
| `contents/articles/members-about/{webId}.md` | Long bio prose with `**bold**` / `*italic*` |
| `contents/articles/members-position/{webId}.md` | Short position descriptor |
| `contents/articles/members-interest/{webId}.md` | Research interests as `/Topic` slash lines |
| `contents/images/members/{webId}.{jpg,png}` | Headshot |

Two pain points:

1. **Members can't update their own content.** Excel is unfriendly for collaborative bio editing — no markdown formatting, no diffs, no easy way for a member to "send their update". The maintainer has to manually re-key emails into Excel cells.
2. **Per-member data is fragmented.** Modifying one member touches 5 files in 4 directories.

This spec restructures `contents/` so each member is a **single self-contained folder**, with the Excel sheet trimmed to the admin half (roster fields the maintainer controls). The build script reads from both sources and merges.

---

## 2. Decisions made during brainstorming

| Decision | Choice |
|---|---|
| Excel role | Hybrid: Excel stays for admin-controlled fields; per-member folder for member-supplied content |
| Folder layout | `contents/members/{webId}/{member.json, about.md, photo.{ext}}` |
| Photo location | Inside the per-member folder (moved out of `contents/images/members/`) |
| Two emails | `email.ntu` + `email.preferred`, both optional |
| Template approach | **Direct edit** — members fill in their own `member.json` + `about.md`. No slash-template translation step. Build validates JSON at build time. |
| `member.json` shape | All keys present, even when empty — so a member always sees the full schema in their own file |
| Excel files post-migration | Both at `contents/` root: `member-info.xlsx` (new, 11 cols) + `member-info.legacy.xlsx` (old, 22 cols, kept as read-only reference) |
| Stale dirs | `contents/articles/members-{about,position,interest}/`, `contents/structures/members/`, `contents/images/members/` all deleted post-migration |

---

## 3. Target directory layout

```
contents/
├── member-info.xlsx                   ← NEW: 11 admin columns only
├── member-info.legacy.xlsx            ← OLD: 22-column file, reference only
├── MEMBER_TEMPLATE/                   ← skeleton for new members
│   ├── member.json                    ← all keys, all values ""
│   ├── about.md                       ← "write your bio here" placeholder
│   └── README.md                      ← 1-page member instructions
├── members/                           ← one folder per member, keyed by webId
│   ├── iyunlisahsieh/
│   │   ├── member.json                ← content fields, all keys present
│   │   ├── about.md                   ← bio prose with markdown
│   │   └── photo.jpg                  ← headshot (jpg/png/jpeg accepted)
│   ├── junweiding/
│   │   ├── member.json
│   │   ├── about.md
│   │   └── photo.jpg
│   └── …                              ← one folder per row in member-info.xlsx
├── structures/                        ← still holds publications.json, news.json, etc.
│                                      ←   members/{webId}.json subfolder DELETED
├── articles/                          ← still holds about.md, contact.md, news/
│                                      ←   members-{about,position,interest}/ DELETED
├── images/                            ← still holds research/, group-life/, news/
│                                      ←   members/ DELETED
└── videos/                            ← unchanged
```

The `webId` slug used as the folder name is identical to the slug used today (lowercase, no spaces). The Excel row's `WebID` column is the join key between the row and the folder.

---

## 4. `contents/member-info.xlsx` (slim, post-migration)

Eleven admin-controlled columns kept. Eleven content-controlled columns removed.

### Columns kept

| Column | Used for |
|---|---|
| `WebID` | Folder name; join key |
| `Full Name` | `pubName` (publication-author matching) |
| `Nickname` | Drives display name (`chiNameEng = full_name [(nickname)]`) |
| `Chinese Name` | Bilingual display + SEO meta |
| `Website Section` | PI / Full Time / Ph.D. / Master / Alumni — controls listing grouping |
| `Admission Year` | Sort + grouping within sections |
| `Graduated` | Boolean — admin verifies, not member-submitted |
| `Also in Alumni` | Cross-section listing toggle |
| `Alumni Admission Year` | Used when "also in alumni" is true |
| `Current Position` | Drives the role icon on the listing card |
| `Batch` | Drives the role icon on the listing card |

### Columns moved to `members/{webId}/member.json`

| Old column | New JSON path |
|---|---|
| `Preferred Email` | `email.preferred` |
| `NTU Email` | `email.ntu` |
| `Position / Education` | `position` |
| `Research Interests` | `interests[]` (parsed from existing `/Topic` lines into an array) |
| `metaDescription` | `metaDescription` |
| `Scholar` | `links.scholar` |
| `ORCID` | `links.orcid` |
| `LinkedIn` | `links.linkedin` |
| `ResearchGate` | `links.researchgate` |
| `NTU Scholars` | `links.ntu_scholars` |
| `About` | (moved to `about.md`, not JSON) |

The legacy file `contents/member-info.legacy.xlsx` keeps all 22 columns for reference — read by nothing, never updated, never used by the build.

---

## 5. `members/{webId}/member.json` schema

Every member's file has every key present (empty strings / empty arrays when a value isn't supplied). This way a member sees the full schema in their own file and only changes values.

```jsonc
{
  "position": "Associate Professor, Department of Civil Engineering, NTU",

  "email": {
    "ntu":       "iyhsieh@ntu.edu.tw",
    "preferred": "lisa.preferred@example.com"
  },

  "interests": [
    "Smart Grid Modeling",
    "Energy Management Systems",
    "Low Carbon Logistics"
  ],

  "links": {
    "scholar":      "https://scholar.google.com.tw/citations?user=tUbPb-QAAAAJ",
    "orcid":        "0000-0002-1668-4094",
    "linkedin":     "https://www.linkedin.com/in/i-yun-lisa-hsieh/",
    "researchgate": "https://www.researchgate.net/profile/I-Yun-Lisa-Hsieh",
    "ntu_scholars": "https://scholars.lib.ntu.edu.tw/entities/person/db907a6f-…",
    "office":       { "text": "CERB 601", "url": "https://maps.app.goo.gl/crYHNJhSwBzqt2VJ8" }
  },

  "metaDescription": "Dr. I-Yun Lisa Hsieh (謝依芸), Associate Professor at NTU…"
}
```

### Schema rules

| Field | Type | Required | Notes |
|---|---|---|---|
| `position` | `string` | yes (non-empty) | Multi-line OK; rendered as the position descriptor on the profile |
| `email.ntu` | `string` | optional | Empty string = not shown |
| `email.preferred` | `string` | optional | Empty string = not shown |
| `interests` | `string[]` | optional | Empty array OK; rendered as `#tag` chips on profile |
| `links.scholar` … `links.ntu_scholars` | `string` | each optional | Empty string = not shown; non-empty → link chip |
| `links.office` | `{text: string, url: string}` | optional | Both empty → not shown; text only → no link; both → linked chip |
| `metaDescription` | `string` | optional | Empty → falls through to auto-generated SEO description |

### Empty / missing field rendering

- Empty string → field is **silently hidden** on the rendered page.
- Member can clear a stale URL by setting `links.linkedin: ""` — no manual deletion of keys required.
- Build never deletes keys when an Excel column is empty; this is purely cosmetic on the profile page.

---

## 6. `members/{webId}/about.md`

Free-form Markdown. Full feature set: `**bold**`, `*italic*`, `[links](https://…)`, lists, headings, code, paragraph breaks. No frontmatter, no required structure.

Empty / missing file = the "About" section is hidden on the profile page (warning logged at build time).

---

## 7. Member workflow ("download + send" model)

The maintainer hands each member a copy of the member's own folder. The member edits their two files and sends them back. No slash template, no parser script, no special syntax.

```
1. cp -r contents/members/iyunlisahsieh /tmp/lisa-pkg/
2. cp contents/MEMBER_TEMPLATE/README.md /tmp/lisa-pkg/
3. zip -r lisa-update.zip /tmp/lisa-pkg/
4. Email lisa-update.zip to Lisa.
5. Lisa edits member.json + about.md locally, emails the zip back.
6. cp -r lisa-pkg/* contents/members/iyunlisahsieh/   # overwrites
7. git diff, review, commit, push.
```

For a new member: same flow, source is `contents/MEMBER_TEMPLATE/` (with all values empty).

### `MEMBER_TEMPLATE/README.md` outline (for members)

> ## Updating your E3 Center profile
>
> Edit **two files** and send them back:
>
> 1. **`member.json`** — your position, emails, interests, profile links.
>    - Replace the string values. Don't delete keys or rearrange.
>    - Leave any field as `""` to hide it on the website.
>    - `interests` is a list — add or remove items as you like (1–5 typical).
> 2. **`about.md`** — your biographical paragraphs. Plain Markdown:
>    - `**bold**`, `*italic*`, `[links](https://example.com)`
>    - Blank line = new paragraph
>    - `- item` for bullets
>
> Send both files back when done. Do not edit anything in `member-info.xlsx`
> — your admin info (name, batch, section) is handled separately.

---

## 8. `build.py` + `lib/excel_to_content.py` changes

The pipeline shifts from "Excel writes 4 files per member" to "Excel + per-member folder are read and merged".

### Refactored `lib/excel_to_content.py` (called at build start)

1. Load `contents/member-info.xlsx` (11 admin columns).
2. For each row's `WebID`:
   a. Load `contents/members/{webId}/member.json` and validate (see §9).
   b. Load `contents/members/{webId}/about.md` (raw text).
   c. Detect photo file: `contents/members/{webId}/photo.{jpg,jpeg,png}`.
   d. Merge admin (Excel) + content (folder) into the per-member dict.
3. Write `contents/structures/members.json` — the section-grouped listing (used by `templates/pages/members.html`). This file remains auto-generated and gitignored-from-edits.
4. Stop writing per-member JSONs and per-member Markdown files. Those are now sourced from disk.

### `build.py` order of operations (unchanged at the outer level)

```
1. lib.excel_to_content side effects run (above)
2. Load structures/articles
3. Render per-page templates
4. Render per-member pages (templates unchanged — receive merged dict)
5. Render per-news-item pages
6. Copy static assets
7. Process images (members/ now sourced from contents/members/*/photo.*)
8. Generate sitemap
```

Step 7 image processing is updated: it iterates `contents/members/*/photo.*` instead of `contents/images/members/*`. Output paths in `docs/assets/members/{webId}-{N}w.webp` are **unchanged** (image-name and srcset patterns stay the same so existing HTML templates need no change).

### `templates/pages/member/member.html` & friends

**No changes required.** The merged dict has the same shape templates see today (`chiNameEng`, `pubName`, `position`, `metaDescription`, `pageContent.links`, `pageContent.aboutSection`, `pageContent.PublicationSection`). The merger reconstructs the legacy shape from the new sources so the template layer is decoupled from the content layout.

---

## 9. Validation: `lib/validate_member.py`

A new small module. Exports:

```python
def validate_member_folder(web_id: str, folder: Path) -> list[ValidationIssue]:
    """Returns list of issues. Empty list = OK.
    ValidationIssue = (severity: 'error' | 'warn', message: str)"""
```

Called once per Excel row from `excel_to_content.py`.

### Checks

| Severity | Condition |
|---|---|
| ✗ ERROR | `member.json` is invalid JSON (with line/column from `json.JSONDecodeError`) |
| ✗ ERROR | `member.json` schema mismatch (wrong type for a known field; details which path) |
| ⚠ WARN  | Folder missing entirely for an Excel row |
| ⚠ WARN  | `member.json` missing |
| ⚠ WARN  | `about.md` missing |
| ⚠ WARN  | Photo file missing |
| ⚠ WARN  | URL field doesn't start with `http(s)://` |
| ⚠ WARN  | `email.ntu` or `email.preferred` doesn't contain `@` |
| ⚠ WARN  | `email.ntu` doesn't end with `.ntu.edu.tw` |

CI build **fails** on any `✗` error so malformed JSON never reaches production. `⚠` warnings are logged and the build proceeds (renders a stub for that member). This keeps an in-progress new member from blocking deploys.

### Schema (used by the type check)

```python
SCHEMA = {
    "position":        str,
    "email":           {"ntu": str, "preferred": str},
    "interests":       [str],
    "links": {
        "scholar":      str,
        "orcid":        str,
        "linkedin":     str,
        "researchgate": str,
        "ntu_scholars": str,
        "office":       {"text": str, "url": str},
    },
    "metaDescription": str,
}
```

No external dependency (`jsonschema`, `pydantic`) needed — a 30-line recursive type-check is enough for this tree.

### Error output format

```
✗ contents/members/iyunlisahsieh/member.json: invalid JSON
  Line 5, column 23: Expecting ',' delimiter

✗ contents/members/junweiding/member.json: schema mismatch
  At 'email.ntu': expected string, got null

⚠ contents/members/newmember/: folder missing
  Build will render a placeholder profile.
```

---

## 10. One-time migration: `lib/migrate_to_per_member_folders.py`

Run once locally; results committed to the repo. The script is **idempotent for content writes** (re-running merges in new Excel data without overwriting member edits already made) and **non-destructive** (does not delete the old directories — that's a manual `git rm` step after eyeballing the result).

### What it does

1. Read `contents/member-info.xlsx` (the current 22-column file).
2. For each member row:
   - Parse content fields (email, position, interests, links, metaDescription) → assemble `member.json` with **all keys present**, populated with current values (empty string when blank).
   - Copy `contents/articles/members-about/{webId}.md` → `contents/members/{webId}/about.md`.
   - Move `contents/images/members/{webId}.{jpg,jpeg,png}` → `contents/members/{webId}/photo.{ext}`.
   - Parse `contents/articles/members-interest/{webId}.md` (the existing `/Topic` slash lines) → `interests[]` array in `member.json`.
   - Embed `contents/articles/members-position/{webId}.md` content → `position` string in `member.json` (line breaks preserved as `\n`).
3. Write a NEW `contents/member-info.xlsx` with only the 11 admin columns.
4. Rename the original 22-column file to `contents/member-info.legacy.xlsx`.
5. Create `contents/MEMBER_TEMPLATE/` skeleton (empty `member.json`, placeholder `about.md`, README.md for members).
6. Print a summary and a list of directories the maintainer can safely `git rm` next.

### Migration safety

- Script will not run if `contents/members/` already exists with content unless invoked with `--force`. Prevents accidental overwrite of partially-migrated state.
- Script writes a one-line summary per member processed; errors are loud and abort the run.
- The legacy Excel is committed to git, so any column can be recovered later via `git checkout`.

### Migration order of operations (single PR)

```
1. python lib/migrate_to_per_member_folders.py
2. Manually inspect a few migrated folders (especially iyunlisahsieh/)
3. python build.py                    # should succeed with warnings only
4. diff -r docs.before/ docs.after/    # confirm zero rendering differences
5. git rm -r contents/articles/members-{about,position,interest}/
   git rm -r contents/structures/members/
   git rm -r contents/images/members/
6. Commit, open PR for review, merge
```

---

## 11. Out of scope (deliberate)

The following are NOT part of this restructure; flagged for follow-ups if needed:

- **Schema versioning** — `member.json` does not have a `schemaVersion` field. If the schema evolves later, prefer adding optional fields (always backwards-compatible) over versioning. Add `schemaVersion` only when a breaking change is actually proposed.
- **JSON Schema file** — no `.schema.json` published alongside; the type check in `lib/validate_member.py` is the source of truth. (Could be added later for VSCode autocomplete.)
- **GitHub-based member edits** — members do not get repo access. The "download and send" workflow is by design; reduces risk of accidental commits.
- **Auto-detection of new members in Excel** — adding a new row to Excel does not auto-create the folder. The maintainer copies `MEMBER_TEMPLATE/` to seed a new folder (manual, intentional act).
- **Photo cropping / dimension validation** — out of scope; existing image pipeline handles WebP generation at fixed widths.

---

## 12. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Members break JSON syntax (unescaped quote, trailing comma) | Build validation catches with file:line:col error; member.json shipped to member is already-valid (their own current data) so they only edit values, not structure. |
| Photo lost during move from `images/members/` to `members/{id}/` | Migration script copies first, verifies hash, then deletes. If verification fails, leaves the original in place. |
| Build pipeline regression | "Build identically before and after migration" is a hard gate: step 4 of migration is `diff -r docs.before/ docs.after/`. PR must not merge until diffs are zero or expected. |
| Member sends back broken `member.json` | Maintainer commits to a branch, opens PR — CI catches malformed JSON before merge. Maintainer pings member to fix. |
| Existing publication-author matching breaks | `pubName` stays in Excel (admin column). No change to the `pubName in authors` matching in `build.py`. |

---

## 13. Acceptance criteria

- [ ] `python lib/migrate_to_per_member_folders.py` produces one folder per Excel row (currently 26) without errors.
- [ ] `python build.py` succeeds end-to-end on the migrated tree with zero `✗` errors (warnings OK for incomplete migrations).
- [ ] `diff -r docs.before/ docs.after/` shows no unexpected rendering differences (member pages, members listing, homepage members section, publications attribution).
- [ ] All 16 existing unit tests still pass.
- [ ] Manually editing `contents/members/iyunlisahsieh/about.md` (e.g. adding a sentence) and rebuilding reflects the change on the page.
- [ ] Deleting `links.linkedin` value (setting to `""`) in `member.json` removes the LinkedIn chip on the profile page.
- [ ] Introducing a deliberate syntax error in a `member.json` makes the build fail with a precise file:line:col error.
- [ ] `contents/MEMBER_TEMPLATE/` exists with all-empty `member.json`, placeholder `about.md`, and README.md.

---

## 14. Implementation handoff

After this spec is approved, hand off to the **`writing-plans`** skill to produce a step-by-step implementation plan. The plan should cover (in order):

1. New branch `feat/member-content-restructure` from `source`.
2. Write `lib/validate_member.py` with schema + checks (TDD).
3. Write `lib/migrate_to_per_member_folders.py` (one-time, committed).
4. Run the migration on a scratch copy; produce `docs.before/` and `docs.after/`; diff.
5. Refactor `lib/excel_to_content.py` to merge from both sources instead of writing per-member files.
6. Update `build.py` step 7 (image processing) to iterate `contents/members/*/photo.*`.
7. Delete stale directories (`articles/members-*`, `structures/members/`, `images/members/`).
8. Update `STRUCTURE.md`, `CLAUDE.md`, `CONTRIBUTING.md` to reflect new layout.
9. Update tests if any reference the old paths.
10. Open PR; CI must pass; manual rendering verification on a member page + members listing.
