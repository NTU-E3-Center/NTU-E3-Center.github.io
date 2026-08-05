# Homepage news: flat latest-5 list

**Date:** 2026-08-05
**Status:** approved by user (option 1A — flatten news, keep members as-is)

## Problem

The homepage news section is the only section on the landing page split by
category. It renders 2 items × 5 categories = 10 rows plus 5 eyebrow
headings — triple the visual weight of the publications (5 rows) and
projects (5 rows) sections. Worse, category grouping makes the section
non-chronological: a year-old outreach post gets the same prominence as
this month's award. Recency is the landing page's signal; taxonomy already
has a proper home on `/news/` (year groups + filter tabs).

## Decision

Replace the category-grouped homepage news section with a single flat list
of the **5 newest items**, newest first, each carrying its category badge.
Members, publications, projects, group-life, hero, and section order are
all unchanged.

## Change

One file: `templates/home/news.html`.

1. **Flatten + order.** Concatenate `items` across all `structures['news']`
   sections, take the last 5, reverse. File order is oldest-first
   chronological — the same assumption `news_years` in `build.py` makes.
2. **Remove grouping.** Delete `category_order`, the per-category loop, and
   the 5 `section-eyebrow` H3s. Render one `.news-rows` list.
3. **Add category badge.** Each row gains
   `<span class="news-row-badge" data-cat="{{ item['category'] }}">` inside
   `.news-row-body` under the title — same placement as `/news/`. Reuse the
   short-label mapping from `templates/pages/news.html`
   (Faculty Honors→Faculty, Student Awards→Students, In the Media→Media,
   Events and Exchanges→Events, Education and Outreach→Outreach), declared
   as a `{% set badge_label = {...} %}` at the top of the partial.
4. **Keep everything else.** Row shapes (pageLink → internal link with
   right arrow; link → external link with top-right arrow; neither →
   static div), the "In the news" heading, and the "See all news" CTA are
   unchanged.

No `build.py` changes. No `contents/news/news.json` changes. No expected
CSS changes — `.news-row-badge` and its `data-cat` color rules live in
`subpage.css`, which loads on every page including home. If badge spacing
inside the homepage row needs a nudge, scope it under `#news .news-row`
and bump the cache-bust version in all five templates per repo convention.

## Verification

- Rebuild; preview on port 8001 (never 8000 — production backend).
- Homepage shows exactly 5 rows, newest first (top row should be
  Jul. '26 wind-to-hydrogen event as of this writing), each with the
  correct badge color.
- Check desktop, tablet, and phone widths — badge wraps correctly when
  the row stacks.
- `/news/` listing page unaffected.
- `python3 validate_design_tokens.py` passes (no token changes expected).

## Edge cases

- Items without `pageLink`/`link` render as static rows, as today.
- Same-month items: file order breaks the tie, same as the news page.
- An item with an unmapped category falls back to its raw category name
  via `badge_label.get(cat, cat)` — same fallback as `/news/`.

## Out of scope (explicitly discussed and kept)

- Members section stays at 11 blocks (PI + Staff + Ph.D. Students) —
  user chose to keep it as-is.
- Publications, projects, group-life sections unchanged.
