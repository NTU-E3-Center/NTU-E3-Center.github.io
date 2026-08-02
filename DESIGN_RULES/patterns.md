# Reusable Pattern Rules

Part of [DESIGN_RULES/](./README.md). Recipes used across multiple components — define them once here, reuse everywhere.

---

## Eyebrow Label

A category/group label that sits above a row. Uniform shape:

```
font-size: 0.6875rem
font-weight: 600
text-transform: uppercase
letter-spacing: 0.14em (use 0.16em only for contact info)
color: var(--main-color)
opacity: 0.4
```

Used by `.mem-group-title`, `.news-cat-title`, `.publi-group-title`, `.news-item-category`, `.news-jump-label`. **New label-style text must adopt this exact recipe** — see finding [E-1] in [`README.md`](./README.md) for the one place it once drifted.

**Category-colored variant:** on the news detail page, `.news-item-category[data-cat]` swaps `opacity 0.4` for full-opacity `var(--cat-*-text)` so the category is legible at a glance. Same geometry, color instead of dimming — see `color.md` § News Category Tokens.

---

## Status / Category Badge

```
font-size: var(--fs-badge)
font-weight: var(--fw-heading)
text-transform: uppercase
letter-spacing: 0.1em
padding: 0.15rem 0.55rem
line-height: var(--lh-badge)
color: var(--cat-*-text)  (news categories)  |  var(--status-*-text)  (publication status)
background: 13–22% tint of the raw category hue (--cat-*)
```

Used by `.publi-status-badge` and `.news-row-badge`. Never restate the size in
rem — the ≤37.5rem `:root` bumps `--fs-badge` to the mobile floor automatically.

**Phone demotion:** at ≤37.5rem the news badge drops its pill background and
renders as a bare `--cat-*-text` label (`subpage.css`, news phone block) — the
capsule reads as loud as the shrunken row title, and the color alone carries
the coding. Publication status badges keep their pill at all sizes.

---

## Date / Number Marker

For year-as-anchor (publication year, news year, member-row year):

```
font-size: var(--fs-lede)      /* the year is the anchor */
font-weight: var(--fw-h1) (600)
letter-spacing: -0.025em
color: var(--main-color)       /* full opacity */
```

The accompanying month sits at `--fs-secondary`, weight 600, opacity 0.45–0.7.
Never restate marker sizes in rem — the tier re-declarations scale the tokens.

---

## List Item Title (rows in News, Publications, Members)

Item-level "titles" are **not** semantic `<h*>` tags — they live inside rows. Treat them as a tier between Body-L and Heading-S:

| List type | Title token (desktop → tablet → phone) | Class |
|---|---|---|
| News / project row | `--fs-body` → `--fs-body-base` → `--fs-secondary` | `.news-row-title` |
| Publication row | `--fs-lede` → `--fs-body` → `--fs-body-base` | `.publi-title` (via `--_font-size-l`) |
| Member row (name) | 2.25 rem | `.mem-row-en` |

Publications sit exactly **one tier above** news/project rows at every
breakpoint (finding [I-2] research-output emphasis); meta lines (authors,
journal, project funder) sit at `--fs-secondary`, dropping to `--fs-eyebrow`
on phones. The larger member-row spread is intentional — member rows are
page-defining, news rows are dense.

---

## Section Title with View-all Link

Always render as `<h2>` wrapped in `.section-title-link`. The hover state animates the trailing underline; do not introduce a separate "View all" pill — reuse `.section-cta-btn` (1.125 rem desktop / 1 rem on small) at the bottom of the section.
