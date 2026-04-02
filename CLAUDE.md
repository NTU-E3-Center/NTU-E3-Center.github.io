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
1. **Load data** — reads all `.json` from `contents/structures/` and `.md` from `contents/articles/` (converted to HTML via `markdown` library)
2. **Render pages** — iterates `pages.json`, renders each Jinja2 template with the full `structures` dict, writes to `docs/{path}/index.html`
3. **Render member pages** — for each member in `members.json`, loads `contents/structures/members/{memberId}.json`, auto-populates their publications by matching `pubName` against `authors` in `publications.json`
4. **Copy static assets** — copies `static/` → `docs/`
5. **Process images** — copies `contents/images/` to `docs/assets/`, converts to WebP at multiple responsive widths (members: 200–800w; group-life: 200–2000w), generates 20w lazy-load placeholders

## Content Structure

All content changes are data-driven — no Python or HTML edits required:

| What to change | Where |
|---|---|
| Members list | `contents/structures/members.json` + `contents/structures/members/{id}.json` |
| Publications | `contents/structures/publications.json` |
| News items | `contents/structures/news.json` |
| Research topics | `contents/structures/research.json` |
| Group photos | `contents/structures/group-life.json` |
| Page navigation | `contents/structures/pages.json` |
| Member bio text | `contents/articles/members-about/{id}.md` |

**Adding a new member requires:**
1. Entry in `members.json` (with `memberId`, `pubName`, `pageLink`)
2. JSON file at `contents/structures/members/{memberId}.json`
3. Markdown files at `contents/articles/members-{about,position,interest}/{memberId}.md`
4. Photo at `contents/images/members/{memberId}.(jpg|png)`

Publications are **automatically linked** to member profiles via `pubName` matching against the `authors` field in `publications.json`. For a publication to appear on the homepage it needs `"E3": true`.

## Templates

- `templates/base.html` — master layout (head, header, footer, analytics)
- `templates/home/` — section sub-templates (about, members, publications, etc.)
- `templates/partials/` — reusable fragments (footer, menu, modal, etc.)
- `templates/member.html` — individual member profile pages

## Deployment

Push to the `source` branch triggers GitHub Actions (`.github/workflows/deploy.yml`), which runs `python build.py` and deploys `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`.
