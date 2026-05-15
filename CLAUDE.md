# CLAUDE.md

Project memory for Claude Code (claude.ai/code). Loaded automatically at session start.

## Project Overview

**Custom Python static site generator** for the E3 Center research website at National Taiwan University (directed by Prof. I-Yun Lisa Hsieh). Live site: https://e3center.caece.net

User-facing instructions (build commands, content workflows) live in `README.md`. This file documents what Claude needs to be productive: architecture, conventions, and pitfalls.

## Architecture

`contents/` holds 100% hand-edited source, grouped one subpage per folder. `excel_to_content.build_member_data()` returns the merged member roster in memory; `build.py` consumes it directly without writing any intermediate files. No gitignored artifacts exist under `contents/`.

```
contents/members/member-info.xlsx      ← admin roster (11 cols)
contents/members/{webId}/              ← per-member content (member.json, about.md, photo.{ext})
        ↓
lib.excel_to_content.build_member_data()  ← merges + validates → in-memory dict
        ↓
contents/{publications,projects,news,research,group-life,about,contact,videos}/
                                       ← per-subpage source (JSON + Markdown + images)
contents/pages.json                    ← site-level nav config
templates/*.html                       ← Jinja2 templates (incl. templates/partials/home.svg)
static/                                ← CSS, JS, favicons, sprites (copied unchanged)
        ↓
    build.py                 ← uses helpers from lib/ (seo_helpers, excel_to_content)
        ↓
    docs/                              ← generated static site (GitHub Pages)
```

Python helpers consumed by `build.py` live in `lib/` (`lib/seo_helpers.py`, `lib/excel_to_content.py`); install runtime deps via `pip install -r requirements.txt`.

## Build pipeline (`build.py` order)

1. **`lib.excel_to_content.build_member_data()`** — reads `contents/members/member-info.xlsx` + each `contents/members/{webId}/` folder, validates via `validate_member.py` (build **fails** on invalid JSON / schema mismatch, **warns** on missing optional files), and returns a Python dict containing the section-grouped roster, per-member detail, and pre-rendered Markdown. **No files are written.**
2. **Load subpage data** — explicit per-subpage JSON loads (`contents/publications/publications.json`, `contents/news/news.json`, …). Also loads `contents/about/about.md` and `contents/contact/contact.md` into the `articles` dict, plus every `contents/news/articles/*.md` keyed as `news/<slug>`.
3. **Render standard pages** — iterates `contents/pages.json`, renders each Jinja2 template with `structures` + `articles`, writes to `docs/{path}/index.html`.
4. **Render member pages** — for each member in `structures['members']`, looks up the in-memory detail by webId derived from `pageLink`, auto-populates publications by matching `pubName` against `authors` in `publications.json`.
5. **Render news item pages** — for each item with a `pageLink`, renders `templates/pages/news/news-item.html` using markdown from `contents/news/articles/{slug}.md`. If `contents/news/images/{slug}/0.{ext}` exists, it becomes the hero (WebP variants generated in step 9).
6. **Copy static assets** — `static/` → `docs/`.
7. **Copy videos** — `contents/videos/{video files}` → `docs/assets/videos/` (`videos.json` is skipped — it's data, not an asset).
8. **Generate `sitemap.xml`** — emits URLs for static pages, member pages (deduplicated), and news item pages. Per-URL `lastmod` reflects the source files' actual mtimes.
9. **Process images** — `compress_and_convert_images()` walks `contents/news/images/` and `contents/group-life/images/` and emits WebP variants (200–2000w) under `docs/assets/`. `compress_member_images()` converts each `contents/members/{webId}/photo.{ext}` to `docs/assets/members/{webId}-{N}w.webp` (200–800w). 20w lazy-load placeholders for all. Subfolders preserved for news (`news/{slug}/0.jpg` → `docs/assets/news/{slug}/0-Nw.webp`).

## Content Structure

| What to change | Where |
|---|---|
| Member admin fields (section, batch, graduated, names) | `contents/members/member-info.xlsx` — 11-column roster |
| Member content (position, emails, interests, links, bio, photo) | `contents/members/{webId}/` — `member.json` + `about.md` + `photo.{ext}` |
| Publications | `contents/publications/publications.json` |
| Projects | `contents/projects/projects.json` |
| News items (homepage list) | `contents/news/news.json` |
| News item article body | `contents/news/articles/{slug}.md` (slug = last segment of `pageLink`) |
| News item images | `contents/news/images/{slug}/` (file `0.{ext}` is the hero) |
| Research topics | `contents/research/research.json` |
| Group photos data | `contents/group-life/group-life.json`; images in `contents/group-life/images/` |
| Videos | `contents/videos/videos.json` + the video files in the same folder |
| Page navigation | `contents/pages.json` |
| About / Contact text | `contents/about/about.md`, `contents/contact/contact.md` |

Publications are **automatically linked** to member profiles via `pubName` matching against the `authors` field in `publications.json`. For a publication to appear on the homepage it needs `"E3": true` and `status: "published"` (items under review are excluded).

`contents/members/member-info.legacy.xlsx` is a read-only archive of the original 22-column spreadsheet — never edit it.

## Templates

- `templates/base.html` — master layout (head, header, footer, analytics)
- `templates/index.html` — homepage shell that includes everything in `templates/home/`
- `templates/home/` — homepage section sub-templates (about, members, publications, news, research, group-life, videos, contact)
- `templates/pages/` — standalone subpage templates: `members.html`, `publications.html`, `news.html`, `projects.html`, `member/member.html`, `news/news-item.html`
- `templates/partials/` — reusable fragments (footer, menu, modal, loading, background, subpage-header, to-top button, `home.svg`)

The Jinja2 loader points at `templates/` only — `contents/` is data, not a template path.

## Design Rules (authoritative)

**`DESIGN_RULES/` at the project root is the single source of truth for typography, color, spacing, and responsive behavior.** Start at `DESIGN_RULES/README.md` for the index. It defines the font stack and weight/color tokens, the 16-tier type scale, the desktop / tablet / mobile breakpoints (root scales to 87.5% on mobile via `general.css:233`), per-component rules, reusable pattern recipes, and a list of known drifts to avoid reintroducing.

When the rules and the current CSS disagree, treat `DESIGN_RULES/` as the spec and the drift as a bug. If a deliberate exception is needed, document it in the relevant file under `DESIGN_RULES/` rather than silently diverging.

## Deployment

Push to the `source` branch triggers GitHub Actions (`.github/workflows/deploy.yml`), which runs `python build.py` and deploys `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`. `docs/` is gitignored on the `source` branch — only the rendered site lives on `gh-pages`.
