# Project Detail Pages — Schema & Design

**Date:** 2026-06-01
**Status:** Design approved (pending written-spec review)
**Topic:** Individual detail pages for flagship projects

## Goal

Give selected ("flagship") projects a rich individual web page — narrative,
collaboration partners, internal team, related publications, research outputs,
and photos — without bloating the ~40-entry project listing or inventing new
build infrastructure. The page should follow the patterns the site already uses
for publication, member, and news detail pages.

## Scope decisions (from brainstorming)

- **Opt-in / flagship only.** Only projects explicitly marked get a detail page;
  the rest stay as plain listing rows. This mirrors the existing convention that
  a publication gets a detail page only when it has an `abstract`.
- **Content blocks the schema must support:** bilingual title (exists), bilingual
  narrative, collaboration partners (with links + optional logo), internal team
  (linked to member pages), related publications (linked by `citationId`),
  outputs beyond papers, key findings, and a photo gallery (site visits / group
  photos). **No cover/hero image** — gallery only.
- **Data layout:** per-flagship-project folder (Approach A), reusing the
  `members/` and `news/` folder + markdown + image conventions.
- **Out of scope (YAGNI):** press / external-links block (opted out);
  publication→project and member→project back-links (the `citationId` / `webId`
  data makes these trivial to add later, but not built now); topic/method chips
  on projects.

## How detail pages already work in this repo (pattern to follow)

Established by the `Explore` pass over `build.py` and the templates:

- Publications, members, and news each get per-item detail pages via the same
  recipe: annotate the JSON item with a `slug` + `pageLink` → a dedicated
  `render_*_pages()` function → a template at
  `templates/pages/<type>/<type>-item.html` → output to
  `docs/<type>/<slug>/index.html`.
- **Publication detail pages are opt-in**: `build.py` only generates one when the
  entry has an `abstract`. Entries without it stay as plain rows.
- **Cross-linking exists**: members link to publications by `citationId` and to
  research topics by ID; publication pages link authors to members by `webId`.
- **Image handling exists**: news auto-discovers images from
  `contents/news/images/<slug>/` and generates WebP / responsive variants.
- **Slug convention**: `pub_slug()` produces `{year}-{first-~7-title-words}`,
  lowercased and hyphenated; an explicit `slug` field overrides it.
- Projects today are listing-only: `templates/pages/projects.html` renders the
  `proj_row()` macro (`templates/partials/proj-row.html`), grouped by
  `sectionTitle` and split by status (Ongoing / Concluded). The homepage shows
  the top ongoing projects via the same macro.

## File layout (Approach A — per-project folder)

```
contents/projects/
  projects.json                 # the listing — unchanged except ONE new key
  <slug>/                       # one folder per flagship project
    project.json                # rich structured fields (below)
    about.md                    # English narrative body (markdown)
    about.zh.md                 # Chinese narrative body (optional)
    images/
      1.jpg, 2.jpg, ...         # site-visit / group photos (NO 0.jpg hero)
```

`<slug>` example: `2026-cross-national-green-finance-taiwan-india`.

## Opt-in trigger + the only change to `projects.json`

Per the repo's uniform-keys rule, **all ~40 entries** gain exactly one new key:

```jsonc
"slug": ""
```

- Empty `slug` → stays a plain listing row (today's behavior).
- Non-empty `slug` **and** a matching `contents/projects/<slug>/` folder exists →
  a detail page is generated and the listing row links to it.

Core metadata (`titleEn`, `titleZh`, `grantNumber`, `role`, `startDate`,
`endDate`, `fundingAgency`, `fundingAgencyEn`, `status`) stays **only** in
`projects.json`. `project.json` must **not** duplicate it; `build.py` merges the
two by slug so there is a single source of truth.

The slug is author-set in `projects.json` (human-readable preferred). A
`proj_slug(item)` helper provides a fallback generator parallel to `pub_slug()`
(`{startYear}-{slugified titleEn}`).

## `contents/projects/<slug>/project.json` — rich fields only

```jsonc
{
  "summary":   "",        // one-line EN teaser (card + OG/meta description)
  "summaryZh": "",

  "keyFindings": [        // "main research output" as headline results/outcomes
    { "text": "", "textZh": "" }
  ],

  "partners": [           // external collaboration orgs
    { "name": "", "nameZh": "", "url": "", "logo": "", "role": "" }
    //  logo = filename in images/ (e.g. "partner-iitd.png") or "" (optional)
    //  role e.g. "International collaborator", "Industry sponsor"
  ],

  "team": [               // internal people -> link to existing member pages
    { "webId": "", "name": "", "role": "" }
    //  webId matches contents/members/<webId>/ ; name = fallback for non-member
    //  role e.g. "Principal Investigator", "Co-PI", "Research Assistant"
  ],

  "relatedPublications": [  // link by citationId -> resolved at build time
    { "citationId": "" }    //   to title / journal / year / pageLink
  ],

  "outputs": [            // outputs beyond journal papers
    { "type": "", "title": "", "titleZh": "", "url": "", "note": "" }
    //  type in {tool, dataset, report, software, patent, dashboard} (free text allowed)
  ],

  "gallery": [            // ORDERED source of truth for which photos show, + captions
    { "file": "", "caption": "", "captionZh": "" }
    //  file = filename in images/ (e.g. "1.jpg"); images not listed here are ignored
  ],

  "metaDescription": ""   // SEO; falls back to summary
}
```

**Uniform-keys rule applies inside each array too**: every object in `partners`,
`team`, `relatedPublications`, `outputs`, and `gallery` shares its fixed key set;
use empty strings for blanks rather than omitting keys.

## Narrative & bilingual convention

- `about.md` = English narrative body (markdown, like member bios).
- `about.zh.md` = optional Chinese narrative body.
- The page renders English as the primary body; Chinese below in Noto Sans TC —
  the same bilingual treatment the publication detail page uses for `titleZh` /
  `journalZh`.

## Detail-page layout — `templates/pages/projects/project-item.html`

Reuses the publication-item two-column layout.

- **Header:** H1 `titleEn`; `titleZh` beneath; meta line (role badge,
  `startDate–endDate`, status pill).
- **Main column (left):**
  1. Narrative (`about.md` / `about.zh.md` rendered)
  2. Key Findings
  3. Outputs
  4. Related Publications — reuse publication-row styling; link to each paper's
     own detail page where one exists, else its publisher link
  5. Photo gallery — lightbox via the existing `templates/partials/media-modal.html`
- **Aside column (right):** metadata card — funder (EN/ZH), grant no., role,
  dates, status; **Partners** (optional logo + link + role); **Team**
  (member-linked names).
- New `static/css/project-item.css`; page includes `general.css` + `subpage.css`
  like every other detail page.
- Include shared partials: `subpage-header.html`, `menu.html`, `footer.html`,
  `background.html`, `to-top-btn.html`.
- Add JSON-LD (e.g. a research-project / `CreativeWork` schema) + OG/Twitter meta,
  mirroring the publication detail page.

## `build.py` changes

1. `proj_slug(item)` helper — `{startYear}-{slugified titleEn}`, parallel to
   `pub_slug()`; explicit `slug` in `projects.json` wins.
2. During data load, for each `projects.json` entry with a non-empty `slug` and an
   existing `contents/projects/<slug>/` folder: load `project.json`, render
   `about.md` / `about.zh.md`, discover `images/`, and annotate the listing entry
   with `pageLink = /projects/<slug>/`.
3. Resolve `relatedPublications[].citationId` against `structures['publications']`
   to title / journal / year / `pageLink`; resolve `team[].webId` against members
   to name / photo / `pageLink`.
4. `render_project_pages()` — parallel to `render_publication_pages()`; output
   `docs/projects/<slug>/index.html`.
5. Reuse the news WebP/responsive conversion for `images/`, but driven by the
   ordered `gallery[]` list (the source of truth for which files appear, and in
   what order) rather than auto-discovering every file in the folder.
6. The listing template (`templates/pages/projects.html` / `proj-row.html`) links
   the row to `pageLink` when present (otherwise renders as today).

## Success criteria

- A project with `slug` set + a populated folder renders a complete detail page
  at `/projects/<slug>/` with all populated sections; empty sections are omitted.
- Projects without a `slug` render exactly as they do today.
- `projects.json` gains exactly one new uniform key across all entries.
- Related publications and team members stay in sync via `citationId` / `webId`
  (edit the source record once).
- No new build infrastructure beyond a `render_project_pages()` function and one
  template + CSS file; image and markdown handling reuse existing pipelines.

## Open / future enhancements (not in this build)

- Publication→project and member→project back-links.
- Topic/method chips on projects (the publication taxonomy already exists).
- A press / external-links block (currently opted out).
