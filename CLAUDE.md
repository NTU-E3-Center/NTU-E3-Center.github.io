# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **custom Python-based static site generator** for the E3 Center research website at National Taiwan University (directed by Prof. I-Yun Lisa Hsieh). Live site: https://e3center.caece.net

## Build & Development Commands

Use the `E3website` conda environment (Python 3.9):

```bash
conda activate E3website
```

**Build the site:**
```bash
conda activate E3website
python build.py
```

**Preview locally:**
```bash
cd docs && python -m http.server 8000
# Open http://localhost:8000
```

> `docs/` is the generated output — never edit files there directly; they are fully overwritten on every build.

## Architecture

Data flows from source files → `build.py` → `docs/` (deployed via GitHub Pages):

```
contents/member-info.xlsx    ← member source of truth (Excel)
        ↓
excel_to_content.py          ← auto-generates members JSON + Markdown
        ↓
contents/structures/*.json   ← page data, members, publications, etc.
contents/articles/*.md       ← text content (about, member bios)
templates/*.html             ← Jinja2 templates
static/                      ← CSS, JS, assets (copied unchanged)
contents/images/             ← source images (auto-converted to WebP)
        ↓
    build.py
        ↓
    docs/                    ← generated static site (GitHub Pages)
```

**`build.py` performs these steps in order:**
1. **Run `excel_to_content.py`** — reads `contents/member-info.xlsx` and generates `members.json`, per-member JSON files, and member Markdown files
2. **Load data** — reads all `.json` from `contents/structures/` and `.md` from `contents/articles/` (converted to HTML via `markdown` library)
3. **Render pages** — iterates `pages.json`, renders each Jinja2 template with the full `structures` dict, writes to `docs/{path}/index.html`
4. **Render member pages** — for each member in `members.json`, loads `contents/structures/members/{memberId}.json`, auto-populates their publications by matching `pubName` against `authors` in `publications.json`
5. **Copy static assets** — copies `static/` → `docs/`
6. **Process images** — converts `contents/images/` to WebP at multiple responsive widths (members: 200–800w; group-life: 200–2000w), generates 20w lazy-load placeholders

## Content Structure

All content changes are data-driven — no Python or HTML edits required:

| What to change | Where |
|---|---|
| Members (add/update/remove) | `contents/member-info.xlsx` — source of truth |
| Publications | `contents/structures/publications.json` |
| News items | `contents/structures/news.json` |
| Research topics | `contents/structures/research.json` |
| Group photos | `contents/structures/group-life.json` |
| Page navigation | `contents/structures/pages.json` |
| About / Contact text | `contents/articles/about.md`, `contents/articles/contact.md` |

**Adding a new member:**
1. Add a row to `contents/member-info.xlsx`
2. Run `python build.py` — `excel_to_content.py` auto-generates:
   - `contents/structures/members.json`
   - `contents/structures/members/{webId}.json`
   - `contents/articles/members-{about,position,interest}/{webId}.md`
3. Add photo at `contents/images/members/{webId}.(jpg|png)`

> Do **not** manually edit `members.json` or per-member JSON/Markdown files — they are fully overwritten on every build.

Publications are **automatically linked** to member profiles via `pubName` matching against the `authors` field in `publications.json`. For a publication to appear on the homepage it needs `"E3": true`.

## Templates

- `templates/base.html` — master layout (head, header, footer, analytics)
- `templates/home/` — section sub-templates (about, members, publications, etc.)
- `templates/partials/` — reusable fragments (footer, menu, modal, etc.)
- `templates/member.html` — individual member profile pages

## Deployment

Push to the `source` branch triggers GitHub Actions (`.github/workflows/deploy.yml`), which runs `python build.py` and deploys `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`.
