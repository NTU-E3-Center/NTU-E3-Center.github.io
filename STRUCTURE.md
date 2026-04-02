# Project Structure

This repository uses a custom Python static site generator (`build.py`) to build the website. Below is the full directory layout and the role of each component.

---

## Directory Overview

```
NTU-E3-Center.github.io/
├── build.py                   # Main build script
├── contents/                  # Source data, text, and images
├── templates/                 # Jinja2 HTML templates
├── static/                    # Static assets (copied as-is to output)
├── docs/                      # Generated output — served by GitHub Pages
├── website/                   # Local Python virtual environment (not committed)
└── .github/workflows/         # GitHub Actions CI/CD
```

---

## Key Directories

### `contents/`

All source content processed by the build script.

```
contents/
├── structures/
│   ├── pages.json             # Navigation structure and page paths
│   ├── members.json           # All team members grouped by role
│   ├── publications.json      # Research publications with citation metadata
│   ├── research.json          # Research topics (researchId-keyed)
│   ├── about.json             # About section data
│   ├── contact.json           # Contact information
│   ├── news.json              # News and announcements
│   ├── group-life.json        # Group photo metadata
│   ├── videos.json            # Video references
│   └── members/               # One JSON file per member (individual page data)
├── articles/
│   ├── about.md               # About section long-form text
│   ├── contact.md             # Contact section text
│   ├── members-about/         # Per-member about blurbs ({memberId}.md)
│   ├── members-interest/      # Per-member research interests ({memberId}.md)
│   └── members-position/      # Per-member position/background ({memberId}.md)
├── images/
│   ├── members/               # Member headshots (source, auto-converted to WebP)
│   ├── research/              # Research-related images
│   └── group-life/            # Group activity photos
└── videos/                    # Video files (copied directly to docs/assets/videos/)
```

### `templates/`

Jinja2 HTML templates. Each template receives data from `structures` and `articles` dicts at build time.

```
templates/
├── base.html                  # Master layout (head, header, footer, analytics)
├── index.html                 # Home page
├── member.html                # Individual member profile pages
├── news.html                  # News listing
├── 404.html                   # 404 error page
├── home/                      # Section sub-templates included by index.html
│   ├── about.html
│   ├── members.html
│   ├── research.html
│   ├── publications.html
│   ├── news.html
│   ├── group-life.html
│   ├── videos.html
│   └── contact.html
└── partials/                  # Reusable HTML fragments (navbar, cards, etc.)
```

### `static/`

Files copied **directly and unchanged** into `docs/` on every build. Edit these for frontend changes.

```
static/
├── css/
│   ├── style.css              # Main stylesheet
│   ├── member.css             # Member profile page styles
│   └── general.css            # Utility styles
├── js/
│   ├── script.js              # Main JavaScript (filtering, interactions)
│   └── general.js             # Utility scripts
├── assets/
│   ├── favicons/
│   └── images/                # Static graphics (logos, icons)
├── editor/                    # Internal content editor tool
├── CNAME                      # Custom domain config for GitHub Pages
└── google102ff7e4d89667d9.html  # Google Search Console verification
```

### `docs/`

The compiled static site output. **Do not edit files here directly** — they are fully overwritten on every build. This directory is served by GitHub Pages.

### `website/`

Local Python virtual environment for running `build.py`. Not committed to git.

### `.github/workflows/deploy.yml`

GitHub Actions workflow that triggers on every push to the `source` branch:
1. Installs Python dependencies (`markdown`, `Pillow`, `jinja2`)
2. Runs `python build.py`
3. Deploys `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`

---

## Build Process

`build.py` runs five steps in order:

### 1. Load data
- Reads all `.json` files from `contents/structures/` into a `structures` dict (key = filename without extension)
- Reads all `.md` files from `contents/articles/` and converts them to HTML via the `markdown` library
- Filters `publications` for the home page: only items with `"E3": true`, sorted descending by date → stored as `home_publications`

### 2. Render page templates
- Iterates `pages.json` to find each page's template name and output path
- Renders `{template_name}.html` with Jinja2, passing `structures`, `articles`, `pages`, `title`, `year`, and `updated_time`
- Writes output to `docs/{path}/index.html` (SEO-friendly URLs)

### 3. Render member pages
- Iterates each member in `members.json`; loads their individual JSON from `contents/structures/members/`
- Renders Markdown from `members-interest/{memberId}.md` into `member.interest_content`
- If `pubName` is set on a member, auto-populates their **Journal Publications** section by matching `pubName` against `authors` in `publications.json`, sorted by date descending
- Outputs to `docs/{member.pageLink}/index.html`

### 4. Copy static assets
- Copies everything from `static/` into `docs/` (preserves subdirectory structure)

### 5. Process images
- Copies source images from `contents/images/` to `docs/assets/{folder}/`
- Converts each image to WebP at multiple responsive widths:
  - **members/**: 200w, 400w, 600w, 800w
  - **group-life/**: 200w, 400w, 600w, 800w, 1200w, 1600w, 2000w
  - **Lazy-load placeholder** (all folders): 20w at quality 10

---

## Data Flow

```
contents/structures/*.json  ─┐
contents/articles/*.md      ─┼─► build.py (Jinja2) ─► docs/ ─► GitHub Pages
templates/*.html            ─┘
static/                     ────────────────────────► docs/
contents/images/            ────── WebP conversion ──► docs/assets/
contents/videos/            ──────────────────────────► docs/assets/videos/
```
