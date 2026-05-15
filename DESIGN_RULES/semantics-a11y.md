# Semantics & Accessibility

Part of [DESIGN_RULES/](./README.md). Covers heading hierarchy rules and the accessibility floor (contrast, minimum sizes, tap targets).

---

## Heading Hierarchy

Every page MUST contain exactly one `<h1>`. Section groupings inside subpages should be `<h2>`; sub-groupings `<h3>`.

| Page | Has h1? | Source |
|---|---|---|
| `/` (homepage) | yes | `#home .hp-title h1` |
| `/members/` | yes (sr-only) | `partials/subpage-header.html` |
| `/publications/` | yes (sr-only) | `partials/subpage-header.html` |
| `/news/` | yes (sr-only) | `partials/subpage-header.html` |
| `/group-life/` | yes (sr-only) | `partials/subpage-header.html` |
| `/contact/` | yes | `.contact-lead` is `<h1>` (`templates/pages/contact.html:41`) |
| `/members/{id}/` | yes | `.main-name h1` |
| `/news/{slug}/` | yes | `.news-item-title` (h1) |

> **Rule:** A page must have exactly one `<h1>`. If a template renders its own visible h1 (member profile, news article, contact), the subpage partial honors `suppressSrH1 = True` to avoid duplicates. List-item titles (member-row, publication-row, news-row) are **not** `<h*>` — see [`patterns.md`](./patterns.md) § List Item Title.

---

## Accessibility Floor

- **Body text contrast:** `#0a557e` on `#ffffff` = ~7.2:1. Passes WCAG AAA.
- **Opacity floor:** text dimmed to **opacity 0.45 or below** on white drops to ~3.2:1 — **below WCAG AA 4.5:1** for body. Allowed only for *decorative* text (separators, placeholders, eyebrow labels at Body-S or smaller). Body-size secondary text uses opacity ≥ 0.6 (finding [C-1]).
- **Smallest acceptable mobile size:** **0.75 rem (10.5 px)**. Badges at 0.5625 rem violate this (finding [A-1] resolved).
- **Minimum tap target:** 44×44 px — preserved by current padding on filter tabs and CTA buttons. Do not shrink padding below `0.3rem 0.875rem` on mobile.
