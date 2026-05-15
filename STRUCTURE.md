# Project Structure

This repository uses a custom Python static site generator (`build.py`) to build the website. Below is the full directory layout and the role of each component.

---

## Directory Overview

```
NTU-E3-Center.github.io/
├── build.py                          # Main build script (CI entry point)
├── lib/                              # Python helpers consumed by build.py
│   ├── __init__.py
│   ├── excel_to_content.py           # Reads admin Excel + per-member folders → in-memory dict
│   └── seo_helpers.py                # SEO helpers exposed to Jinja2 templates
├── validate_member.py                # Validates contents/members/{webId}/ folders at build time
├── requirements.txt                  # Runtime dependencies (used by CI and locally)
├── contents/                         # ★ All hand-edited source (data + prose + images)
├── templates/                        # Jinja2 HTML templates
├── static/                           # Static assets (copied as-is to docs/)
├── SEO/                              # SEO research, strategy, and runbook
├── docs/                             # Generated output — served by GitHub Pages (gitignored)
└── .github/workflows/                # GitHub Actions CI/CD
```

---

## `contents/`

All source content. Grouped one subpage per folder. Nothing in this tree is auto-generated — `build.py` reads it, never writes to it.

```
contents/
├── pages.json                # Site-level nav: maps each route to a template + title + description
│
├── members/
│   ├── member-info.xlsx          # ★ Admin roster — 11 columns (webId, names, section,
│   │                             #   batch, graduated, …). Edit to add/remove members or
│   │                             #   change admin facts. NOT member content.
│   ├── member-info.legacy.xlsx   # Original 22-column Excel, archived read-only reference
│   ├── MEMBER_TEMPLATE/          # Skeleton sent to new members (member.json + about.md + README)
│   └── {webId}/                  # Per-member content — one folder per member
│       ├── member.json           #   position, emails, interests[], links{} — member-edited
│       ├── about.md              #   bio prose (Markdown) — member-edited
│       └── photo.{jpg,png}       #   headshot (auto-converted to WebP at build time)
│
├── publications/publications.json    # All publications with citation metadata
├── projects/projects.json            # Funded projects, grouped by funding source
│
├── news/
│   ├── news.json             # News item list with title, date, pageLink, optional topics[]
│   ├── articles/{slug}.md    # Article bodies (slug = last segment of pageLink)
│   └── images/{slug}/        # Per-article images. 0.{ext} is the hero; rest appear in gallery
│
├── research/
│   ├── research.json         # Research topics (researchId-keyed)
│   └── images/               # Topic SVGs (reference; not copied to docs/)
│
├── group-life/
│   ├── group-life.json       # Group photo metadata
│   └── images/               # Group activity photos (auto-converted to WebP)
│
├── about/
│   ├── about.json
│   └── about.md              # About section prose
│
├── contact/
│   ├── contact.json
│   └── contact.md            # Contact section prose
│
└── videos/
    ├── videos.json           # Video references
    └── {video files}         # Copied to docs/assets/videos/ (videos.json is data, skipped)
```

> **Member content lives in `contents/members/{webId}/`.** The Excel sheet holds only admin
> fields. `excel_to_content.build_member_data()` merges the two at build time and returns
> the result in memory — no files are regenerated on disk under `contents/`. To update a
> member, edit their folder (or send them their folder + `MEMBER_TEMPLATE/README.md`).

---

## `templates/`

Jinja2 HTML templates. Each template receives data from `structures` and `articles` dicts at build time. The Jinja2 loader is rooted at `templates/` only.

```
templates/
├── base.html                  # Master layout (head, header, footer, analytics)
├── index.html                 # Home page shell — includes everything in templates/home/
├── 404.html                   # 404 error page
├── home/                      # Section sub-templates included by index.html
│   ├── about.html
│   ├── members.html
│   ├── research.html
│   ├── publications.html
│   ├── news.html
│   ├── projects.html
│   ├── group-life.html
│   ├── videos.html
│   └── contact.html
├── pages/                     # Standalone subpages
│   ├── members.html
│   ├── publications.html
│   ├── projects.html
│   ├── news.html
│   ├── group-life.html
│   ├── contact.html
│   ├── member/member.html     #   individual member profile
│   └── news/news-item.html    #   individual news article
└── partials/                  # Reusable fragments (footer, menu, modal, …) — incl. home.svg
```

---

## `static/`

Copied **directly and unchanged** into `docs/` on every build. Edit these for frontend changes.

```
static/
├── css/                       # style.css, member.css, general.css, subpage.css, etc.
├── js/                        # script.js (homepage interactions), general.js
├── assets/                    # favicons, sprites (sprite.svg), background images
├── editor/                    # Internal content editor tool (intentionally noindex)
├── CNAME                      # Custom domain for GitHub Pages
└── google102ff7e4d89667d9.html  # Google Search Console verification
```

---

## `docs/`

The compiled static site output. **Do not edit files here directly** — they are fully overwritten on every build. Served by GitHub Pages from the `gh-pages` branch (not from `source`).

---

## `.github/workflows/deploy.yml`

GitHub Actions workflow triggered on every push to the `source` branch:

1. Installs Python dependencies via `pip install -r requirements.txt`
2. Runs `python build.py`
3. Deploys `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`

---

## Build Process

`build.py` runs these steps in order. **No files are written to `contents/` at any point**; the only output is `docs/`.

### 1. `build_member_data()` from `lib/excel_to_content.py`

- Reads admin fields from `contents/members/member-info.xlsx` (11-column roster)
- Reads content fields from each `contents/members/{webId}/member.json` + `about.md`
- Validates every per-member folder via `validate_member.py` — the build **fails** on invalid JSON / schema mismatch, **warns** on missing optional files
- Returns a Python dict: `{'members_listing': [...], 'members_by_id': {...}, 'members_md': {webId: {about, position, interest} (pre-rendered HTML)}}`

### 2. Load subpage data

- For each subpage with hand-edited JSON, load it explicitly: `contents/publications/publications.json`, `contents/news/news.json`, `contents/research/research.json`, `contents/group-life/group-life.json`, `contents/about/about.json`, `contents/contact/contact.json`, `contents/videos/videos.json`, `contents/projects/projects.json`
- Load `contents/about/about.md` and `contents/contact/contact.md` into the `articles` dict
- Load every `contents/news/articles/*.md` keyed as `news/<slug>`
- Inject the in-memory member markdown (`members-about/<webId>`, `members-position/<webId>`, `members-interest/<webId>`) into the same `articles` dict
- Filter `publications` for the homepage: only items with `"E3": true` and `status: "published"`, sorted descending by date → stored as `home_publications`

### 3. Render standard page templates

- Iterates `contents/pages.json` to find each page's template and output path
- Renders `templates/{template_name}.html` with Jinja2, passing `structures`, `articles`, `pages`, `title`, `description`, `canonicalLink`, `year`, `updated_time`
- Writes output to `docs/{path}/index.html` (SEO-friendly URLs)

### 4. Render member pages

- Iterates each member in `structures['members']`; looks up the in-memory detail by webId derived from `pageLink`
- Auto-populates their **Journal Publications** section by matching `pubName` against `authors` in `publications.json`, sorted by date descending
- Outputs to `docs/{member.pageLink}/index.html`

### 5. Render news item pages

- For each item in `news.json` with a `pageLink`, renders `templates/pages/news/news-item.html`
- Reads markdown from `contents/news/articles/{slug}.md` (where `slug` is the last segment of `pageLink`)
- If `contents/news/images/{slug}/0.{ext}` exists, it becomes the hero (auto-converted to WebP in step 9)

### 6. Copy static assets

- Copies everything from `static/` into `docs/` (preserves subdirectory structure)

### 7. Copy videos

- Copies video files from `contents/videos/` to `docs/assets/videos/` (`videos.json` is data, skipped)

### 8. Generate `sitemap.xml`

- Emits URLs for the static pages, member pages (deduplicated), and news items
- Per-URL `lastmod` reflects the most recent mtime of that page's source files

### 9. Process images

- `compress_and_convert_images()` walks `contents/news/images/` and `contents/group-life/images/`, emitting WebP variants at 200w through 2000w (plus a 20w lazy-load placeholder) under `docs/assets/`
- `compress_member_images()` walks each `contents/members/{webId}/photo.{ext}` and emits `docs/assets/members/{webId}-{N}w.webp` at 200/400/600/800w (+ 20w placeholder)
- Subdirectory layout is preserved for news (`news/{slug}/0.jpg` → `docs/assets/news/{slug}/0-Nw.webp`)

---

## Data Flow

```
contents/members/member-info.xlsx ──┐
contents/members/{webId}/         ──┴─ lib.excel_to_content.build_member_data() ─┐
                                                                                  ↓ (in-memory dict)
contents/{publications,projects,news,research,group-life,about,contact,videos}/*.json ─┐
contents/{about,contact}/*.md            ──────────────────────────────────────────────┤
contents/news/articles/*.md              ──────────────────────────────────────────────┤
contents/pages.json                      ──────────────────────────────────────────────┤
templates/*.html                         ──────────────────────────────────────────────┴─► build.py (Jinja2) ─► docs/
static/                                  ───────────────────────────────────────────────────────────────────► docs/
contents/news/images/, contents/group-life/images/, contents/members/{webId}/photo.{ext} ── WebP conversion ─► docs/assets/
contents/videos/{video files}            ───────────────────────────────────────────────────────────────────► docs/assets/videos/
```
