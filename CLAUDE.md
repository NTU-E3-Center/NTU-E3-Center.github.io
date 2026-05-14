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
lib/excel_to_content.py      ← auto-generates members JSON + Markdown
        ↓
contents/structures/*.json   ← page data, members, publications, etc.
contents/articles/*.md       ← text content (about, member bios)
templates/*.html             ← Jinja2 templates
static/                      ← CSS, JS, assets (copied unchanged)
contents/images/             ← source images (auto-converted to WebP)
        ↓
    build.py                 ← uses helpers from lib/ (seo_helpers, excel_to_content)
        ↓
    docs/                    ← generated static site (GitHub Pages)
```

Python helpers consumed by `build.py` live in `lib/` (`lib/seo_helpers.py`, `lib/excel_to_content.py`); install runtime deps via `pip install -r requirements.txt`.

**`build.py` performs these steps in order:**
1. **Run `lib/excel_to_content.py`** — reads `contents/member-info.xlsx` and generates `members.json`, per-member JSON files, and member Markdown files (executed at import time)
2. **Load data** — reads all `.json` from `contents/structures/` and `.md` from `contents/articles/` (converted to HTML via `markdown` library); also builds `members_by_id` lookup and a filtered/sorted `home_publications` (only items with `"E3": true` and `status: "published"`)
3. **Render pages** — iterates `pages.json`, renders each Jinja2 template with the full `structures` dict, writes to `docs/{path}/index.html`
4. **Render member pages** — for each member in `members.json`, loads `contents/structures/members/{memberId}.json`, auto-populates their publications by matching `pubName` against `authors` in `publications.json`
5. **Render news item pages** — for each item in `news.json` with a `pageLink`, renders `templates/pages/news/news-item.html` using markdown from `contents/articles/news/{slug}.md`. If `contents/images/news/{slug}/0.{ext}` exists, it becomes the hero (rendered via the WebP variants generated in step 9)
6. **Copy static assets** — copies `static/` → `docs/`
7. **Copy videos** — copies `contents/videos/` → `docs/assets/videos/`
8. **Generate `sitemap.xml`** — emits URLs for static pages, member pages (deduplicated), and news item pages
9. **Process images** — converts `contents/images/` to WebP at multiple responsive widths (members: 200–800w; group-life and news: 200–2000w), generates 20w lazy-load placeholders. Subfolders are preserved in the output (e.g. `news/{slug}/0.jpg` → `docs/assets/news/{slug}/0-Nw.webp`). Folders without a `{folder}_img_sizes` config are skipped.

## Content Structure

All content changes are data-driven — no Python or HTML edits required:

| What to change | Where |
|---|---|
| Members (add/update/remove) | `contents/member-info.xlsx` — source of truth |
| Publications | `contents/structures/publications.json` |
| News items (homepage list) | `contents/structures/news.json` |
| News item article body | `contents/articles/news/{slug}.md` (slug = last segment of `pageLink`) |
| News item images | `contents/images/news/{slug}/` (file `0.{ext}` is the hero) |
| Research topics | `contents/structures/research.json` |
| Group photos | `contents/structures/group-life.json` |
| Videos | `contents/structures/videos.json`, video files in `contents/videos/` |
| Page navigation | `contents/structures/pages.json` |
| About / Contact text | `contents/articles/about.md`, `contents/articles/contact.md` |

**Adding a new member:**
1. Add a row to `contents/member-info.xlsx`
2. Run `python build.py` — `lib/excel_to_content.py` auto-generates:
   - `contents/structures/members.json`
   - `contents/structures/members/{webId}.json`
   - `contents/articles/members-{about,position,interest}/{webId}.md`
3. Add photo at `contents/images/members/{webId}.(jpg|png)`

> Do **not** manually edit `members.json` or per-member JSON/Markdown files — they are fully overwritten on every build.

Publications are **automatically linked** to member profiles via `pubName` matching against the `authors` field in `publications.json`. For a publication to appear on the homepage it needs `"E3": true` and `status: "published"` (items under review are excluded).

**Adding a news item:**
1. Add an entry to the relevant section in `contents/structures/news.json` with a `pageLink` like `/news/2026-foo/`
2. Create the article body at `contents/articles/news/2026-foo.md`
3. (Optional) Drop images into `contents/images/news/2026-foo/`. `0.{jpg,png,…}` becomes the hero; the rest appear in the gallery sorted numerically (`1.jpg`, `2.jpg`, …) then alphabetically.

## Templates

- `templates/base.html` — master layout (head, header, footer, analytics)
- `templates/index.html` — homepage shell that includes everything in `templates/home/`
- `templates/home/` — homepage section sub-templates (about, members, publications, news, research, group-life, videos, contact)
- `templates/pages/` — standalone subpage templates: `members.html`, `publications.html`, `news.html`, `member/member.html` (individual member profile), `news/news-item.html` (individual news article)
- `templates/partials/` — reusable fragments (footer, menu, modal, loading, background, subpage-header, to-top button)

## Design Rules (authoritative)

**`DESIGN_RULES.md` at the project root is the single source of truth for typography, color, spacing, and responsive behavior.** Read it before changing any CSS or adding new UI. It defines:

- Font stack (`Outfit` + `Noto Sans TC`), weight tokens (`--fw-h1` … `--fw-body`), and color tokens (`--main-color`, accent palette).
- The 16-tier type scale (Display-XL → Badge) with exact desktop / tablet / mobile values.
- Three responsive viewports: **desktop > 1024 px**, **tablet 601–1024 px**, **mobile ≤ 600 px** (root scales to 87.5% / 14 px on mobile via `general.css:233`).
- Per-component rules for the publication row, member cards (L/M/S), news rows, news article body, contact page, member profile, etc.
- Reusable pattern recipes: eyebrow label, status badge, date marker, list-item title.
- A list of known drifts (`[S-*]`, `[W-*]`, `[C-*]`, `[A-*]`, `[I-*]`) — when working in CSS, do not reintroduce these and prefer fixing one if it sits in code you're already touching.

When the rules and the current CSS disagree, treat `DESIGN_RULES.md` as the spec and the drift as a bug. If a deliberate exception is needed, document it in `DESIGN_RULES.md` rather than silently diverging.

## Deployment

Push to the `source` branch triggers GitHub Actions (`.github/workflows/deploy.yml`), which runs `python build.py` and deploys `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`.
