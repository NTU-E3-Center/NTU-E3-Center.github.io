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

Used by `.mem-group-title`, `.news-cat-title`, `.publi-group-title`, `.news-item-category`. **New label-style text must adopt this exact recipe** — see finding [E-1] in [`README.md`](./README.md) for the one place it once drifted.

---

## Status / Category Badge

```
font-size: 0.625rem
font-weight: 600
text-transform: uppercase
letter-spacing: 0.1em
padding: 0.15rem 0.55rem
line-height: 1.6
color: status-specific (var(--r-*))
```

Used by `.publi-status-badge` and `.news-row-badge`. On mobile shrink the font to **0.5625 rem**.

---

## Date / Number Marker

For year-as-anchor (publication year, news year, member-row year):

```
font-size: 1.375rem (news/breadcrumb) | 1.5rem (news-item hero) | 1.0625rem (publication compact)
font-weight: var(--fw-h1) (600)
letter-spacing: -0.025em
color: var(--main-color)   /* full opacity */
```

The accompanying month uses ~0.6× the year's size, weight 600, opacity 0.45–0.7.

---

## List Item Title (rows in News, Publications, Members)

Item-level "titles" are **not** semantic `<h*>` tags — they live inside rows. Treat them as a tier between Body-L and Heading-S:

| List type | Title rem (desktop) | Class |
|---|---|---|
| News row | 1.125 rem | `.news-row-title` |
| Publication row | 1.5 rem | `.publi-title` |
| Member row (name) | 2.25 rem | `.mem-row-en` |

The 2× spread between news and member is intentional — member rows are page-defining, news rows are dense (finding [I-2]).

---

## Section Title with View-all Link

Always render as `<h2>` wrapped in `.section-title-link`. The hover state animates the trailing underline; do not introduce a separate "View all" pill — reuse `.section-cta-btn` (1.125 rem desktop / 1 rem on small) at the bottom of the section.
