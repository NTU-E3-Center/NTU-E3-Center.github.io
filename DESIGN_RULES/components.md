# Component Rules

Part of [DESIGN_RULES/](./README.md). Per-component typography and styling. Pulls tiers from the [type scale](./typography.md) and tokens from [color.md](./color.md) / [layout.md](./layout.md).

---

## Homepage Hero (`templates/home/home.html` + `style.css:48–101`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `#home .hp-title h1` | 3 rem | 3 rem | 2.25 rem |
| `#home .hp-title span` (subtitle) | 1 rem | 1 rem | 1 rem |
| `#home .hp-3e p` ("3E" marker) | 1.5 rem | 1.5 rem | 1.25 rem |
| `.hp-plane-text` | 1.375 rem | — | — |
| `.hp-scroll-for-more`, `.hp-last-update` | 0.75 rem | — | — |

---

## Section Titles (`style.css:437–495`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.section-title h2` | `--fs-h1` (3 rem; 3.25 rem at the ≥90rem tier) | 2.5 rem | 2 rem |
| `.section-subtitle > *` | 1.25 rem | 1.25 rem | 1.25 rem |
| h3 (inside section, with secondary underline bar) | 1.75 rem | 1.25 rem | 1.125 rem |

Weight: `--fw-h1` (600). Letter-spacing: −0.03em. The hover underline animation on `.section-title-link` is shared across "View all members / publications / news / photos".

---

## Subpage Header (`partials/subpage-header.html` + `subpage.css` § Subpage header)

The header is one row at every width: brand + primary nav. The breadcrumb is not
in the header — it renders as `.page-trail`, the first element of the content
flow, and only on detail pages (listing pages are named by the active nav link).

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.hdr-nav-a` | `--fs-secondary`, `--fw-heading`, opacity 0.55 → 1 on hover | hidden (drawer takes over) | hidden |
| `.hdr-nav-a.is-current` | opacity 1 + sage underline | — | — |
| `.trail-parent` (in `.page-trail`) | `--fs-eyebrow`, uppercase, 0.14em | — | — |
| `.trail-current` | `--fs-secondary`, opacity 0.55 | — | `--fw-display` |

---

## Publications (`style.css:1689–1799`, `subpage.css:1032–1058`, `templates/pages/publications.html`)

A publication row uses a **3-column horizontal layout**: date (left), title + meta (center), keyword chips (right).

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.publi-date` (mm/yy stacked) | 1.0625 rem | 0.75 rem | — |
| `.publi-title` | **1.5 rem** (`--_font-size-l`) | 1.25 rem | 1.0625 rem |
| `.publi-subtitle` (journal name) | 1.0625 rem (`--_font-size-s`) | 0.75 rem | — |
| `.publi-row-authors` | 0.9375 rem, opacity 0.55, line-height 1.4 | — | — |
| `.publi-row-journal` | 0.8125 rem, opacity 0.5 | — | — |
| `.pub-keyword-chip` | 0.75 rem | — | — |
| `.publi-status-badge` (under-review etc.) | **0.625 rem**, weight 600, uppercase, letter-spacing 0.1em | — | — |
| `.publi-group-title` (eyebrow: "Working Papers", "Books") | 0.6875 rem, weight 600, uppercase, letter-spacing 0.14em, opacity 0.4 | — | — |
| `.publi-show-more` button | 0.875 rem, weight 600 | — | 0.75 rem |

> **Rule:** Publication titles use `text-transform: capitalize` only on member-profile pages (`member.css:343` `.pub-title`). On homepage and `/publications/`, the original casing is preserved.
> **Rule:** Status badges color-code by `data-status` and use a fixed letter-spacing of `0.1em` (uppercase). Reuse the same badge style for any new lifecycle state.

---

## Members

### Members on Homepage (`style.css:1062–1192`)

Three card sizes (Leader / Medium / Small):

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.EngName` (leader) | 1.75 rem | 1.25 rem | 1.125 rem |
| `.ChiName` (leader) | 1.25 rem | 1 rem | 0.875 rem |
| `.mem-name-en` (medium) | 1.7 rem | 1.25 rem | 1 rem |
| `.mem-name-zh` (medium) | 1 rem | 0.875 rem | 0.75 rem |
| `.mem-name` (small) | 1.5 rem | — | — |
| `.mem-name span` (small) | 1 rem | — | — |

### Members Subpage (`subpage.css:163–489`, `templates/pages/members.html`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.mem-group-title` (eyebrow) | 0.6875 rem, uppercase, 0.14em, opacity 0.4 | — | — |
| `.mem-row-en` (name) | 2.25 rem, weight 600, −0.025em | 1.75 rem | 1.25 rem |
| `.mem-row-zh` (name) | 1.25 rem, weight 500, opacity 0.45 | 1 rem | 0.875 rem |
| `.mem-row-position` first line | 1.0625 rem, weight 600, color `--accent-ink` | — | 0.875 rem |
| `.mem-row-position` other lines | 1 rem, opacity 0.55 | — | 0.8125 rem |
| `.mem-row-tag` | 0.8125 rem | — | — |
| **PI featured row** `.mem-group--pi .mem-row-en` | **2.75 rem**, −0.03em | 2 rem | 1.5 rem |
| **PI featured row** `.mem-group--pi .mem-row-zh` | 1.375 rem, opacity 0.5 | 1.125 rem | 1 rem |
| `.mem-alum-en` (alumni grid) | 1 rem, weight 600 | — | 0.875 rem |
| `.mem-alum-zh` | 0.8125 rem, opacity 0.5 | — | 0.75 rem |

### Member Profile Page (`member.css`, `templates/pages/member/member.html`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.main-name h1` | 2.75 rem | — | 1.875 rem |
| `.sub-name` (Chinese name) | 1.5 rem, opacity 0.7 | — | 1.125 rem |
| `.position-text` | 1.25 rem | — | 1 rem |
| `h2` (About / Research / Publications) | 2.25 rem, weight 550 | — | 1.625 rem |
| `#about .content p`, `li` | 1.25 rem, line-height 1.55, justify | — | 1 rem |
| `.res-tag` (research interest tag) | 1.5 rem | — | 1.125 rem |
| `.res-info-minor` | 1 rem | — | 0.875 rem |
| `.list-block .list-title` | 1.25 rem | — | 1 rem |
| Publication `--_font-size-l` (title) | 1.5 rem | — | 1 rem |
| Publication `--_font-size-s` (date, journal) | 1 rem | — | 0.8125 rem |
| `.pub-show-all-btn` | 0.9375 rem | — | 0.8125 rem |

---

## News

### News Listing (`/news/` — year-grouped; homepage rows share `.news-row`)

The subpage listing groups rows under a sticky year rail (`subpage.css`
§ Year-grouped news listing, scoped to `.news-subpage` so the shared
`.news-row` base used by publications and the homepage stays untouched).

- **Filter tabs** — six (`All` + the five categories in `color.md` § News
  Category Tokens), WAI-ARIA tablist with roving tabindex; filtering hides
  rows by `data-cat` and collapses empty year groups.
- **Year rail** — `.news-year-label` at `--fs-h3`, `--fw-display`, sticky
  below the fixed header. On phones the rail collapses and the label becomes
  a sticky full-width bar with `--page-bg-color` behind it.
- **Jump nav** — `.news-jump-label` uses the eyebrow recipe; `.news-jump-link`
  at `--fs-secondary`, opacity 0.6 ([C-1] floor for interactive text).
- **Collapse** — the three most recent years render expanded; older years sit
  behind `.news-show-older` (same flat-pill language as `.publi-show-more`).
  Category filters and jump links into the archive auto-expand it.
- **Thumbnails** — rows whose detail page has a hero show `.news-row-thumb`
  (200w WebP variant, flat with 0.375rem radius — a documented skew-motif
  exception, see `layout.md`).

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.news-row-mm` (month) | `--fs-secondary`, weight 600, opacity 0.45 | `--fs-eyebrow` | `--fs-eyebrow` (token-bumped) |
| `.news-year-label` | `--fs-h3` | `--fs-lede` | `--fs-body`, sticky bar |
| `.news-row-title` | `--fs-body`, lh 1.5 | `--fs-body-base` | `--fs-secondary` |
| `.news-row-badge` | `--fs-badge` pill, `--cat-*-text` on `--cat-*` tint | — | bare `--cat-*-text` label, no pill |
| `.news-row-thumb` | 4.5×3 rem | 4×2.75 rem | 3.5×2.5 rem |
| `.news-filter-tab` | `--fs-secondary`, weight 600 | same, tighter padding | `--fs-eyebrow` |

### News Article Page (`news-item.css`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.news-item-category` (eyebrow) | `--fs-eyebrow`, uppercase, 0.14em, full-opacity `--cat-*-text` (opacity 0.4 fallback when uncategorized) | — | `--fs-badge` |
| `.news-item-title` (h1) | `clamp(1.75rem, 4vw, 2.75rem)` | 1.625 rem | 1.375 rem |
| `.news-item-date-mm` | 0.9375 rem, opacity 0.7 | — | 0.75 rem |
| `.news-item-date-yy` | 1.5 rem, `--fw-h1`, −0.025em | — | 1.125 rem |
| `.news-item-body` (paragraph) | `--fs-body`, line-height **1.70** (unified prose recipe; the `--fs-prose` alias is legacy — override `font-size` directly) | — | `--fs-secondary` |
| `.news-item-body h2` | 1.875 rem | — | 1.375 rem |
| `.news-item-body h3` | 1.5 rem | — | 1.125 rem |
| `.news-item-body h4` | 1.25 rem | — | 1 rem |
| `.news-item-body h5` | 1.0625 rem (opacity 0.85) | — | 0.9375 rem |
| `.news-item-body h6` | 0.9375 rem, uppercase, 0.06em, opacity 0.5 | — | 0.8125 rem |
| `.news-item-placeholder` | 1.25 rem, italic, opacity 0.35 | — | 1 rem |

> **Rule:** Within `.news-item-body`, all heading levels are rendered at `var(--fw-h1)` (600) — this is intentional editorial gravitas (finding [W-2]). Maintain it for any new content blocks.

---

## Contact Page (`subpage.css:1112–1421`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.contact-lead` (the `<h2>`) | 2.75 rem, `--fw-h1` | — | 1.875 rem |
| `.contact-tagline` | 1.125 rem, line-height 1.65 | — | 1 rem |
| `.contact-info-label` | 0.6875 rem, uppercase, 0.16em, opacity 0.5 | — | — |
| `.contact-info-value` | 1.0625 rem, weight 600 | — | 0.875 rem (weight 500, no-wrap) |
| `.contact-info-sub` | 0.8125 rem, weight 400, opacity 0.6 | — | — |
| `.contact-field label` | 0.75 rem, weight 600, uppercase, 0.12em, opacity 0.55 | — | — |
| `.contact-field input/textarea` | 1.0625 rem | — | — |

---

## Group Life (`style.css:1866–1924`, `templates/pages/group-life.html`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.glf-slider-num` | 1.25 rem, centered | 1.125 rem | — |
| `.glf-slider-text` (caption) | 1.25 rem, centered | 1.125 rem | derived from grid width |

---

## Footer (`style.css:614–649`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.ftr-link` | 1.25 rem | — | 0.9375 rem |
| `.ftr-info` | inherited | — | 0.8125 rem |

---

## Menu / Navigation (`style.css:744–820`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.menu-btn` label | 1.125 rem | — | — |
| `.menu-a` (item) | 1.25 rem | — | `clamp(0.875rem, 2.2dvh, 1rem)` |
| `.nav-l a span` (side rail) | 1.25 rem (hover 1.5 rem) | — | — |
