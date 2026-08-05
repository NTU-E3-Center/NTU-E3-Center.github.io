# Students & Alumni split from center members

**Date:** 2026-08-05
**Status:** approved by user (design review in session)

## Problem

The PI wants her students separated from "E3 Center members": the center's
membership is the PI + staff, while Ph.D. students, Master students, and
alumni are her research group's students. Today `/members/` lists all five
roster sections, the homepage "The team" shows PI + Staff + Ph.D.
students, and the homepage Organization JSON-LD claims every person as a
center `member`.

## Decisions (confirmed with user)

- New page: **`/students/` — "Students & Alumni"** (Ph.D. + Master +
  Alumni).
- `/members/` becomes **PI + Staff only**.
- Individual profile URLs **stay at `/members/{id}/` for everyone** — no
  redirects, no broken news/search links.
- Homepage people section: **PI + Staff, with two CTAs** ("View center
  members" → `/members/`, "Meet the students" → `/students/`).
- Implementation approach: **split once in build.py** (approach B), not
  per-template filtering, so the section whitelist exists in exactly one
  place.

## Changes

### 1. Data — `build.py`

After `_member_data` loads, partition the roster:

```python
_CENTER_SECTIONS = ('Principal Investigator', 'Staff')
structures['members']  = [g for g in listing if g['sectionTitle'] in _CENTER_SECTIONS]
structures['students'] = [g for g in listing if g['sectionTitle'] not in _CENTER_SECTIONS]
```

- `members_by_id` stays whole — profile page generation, news member
  links, and `/members/{id}/` URLs are untouched.
- `lib/excel_to_content.py` is **unchanged** (SECTION_ORDER, forms,
  filters all stay as-is).
- Sitemap: add `/students/` (changefreq monthly, priority 0.8, lastmod
  from member-info.xlsx like `/members/`).
- Audit every `structures['members']` / `structures.get('members')`
  consumer during implementation (known: templates/index.html org
  JSON-LD, templates/pages/members.html + its ItemList JSON-LD,
  templates/home/members.html; re-grep for others) and point each at the
  correct list.

### 2. `/members/` — `templates/pages/members.html`

- Renders PI + Staff sections only (falls out of the data split; the
  Master/Alumni template branches can stay — they simply never match, or
  be pruned if trivial).
- Rewrite meta description (center staff focus, ≤160 chars) and keywords.
- JSON-LD ItemList now naturally lists PI + staff only.
- Add a link-card at the bottom: "Looking for Prof. Hsieh's students and
  alumni? → Students & Alumni", styled as an existing skewed-block CTA.

### 3. `/students/` — new `templates/pages/students.html`

- Modeled on members.html; iterates `structures['students']`:
  Ph.D. Students (M-form rows), Master Students (M-form rows), Alumni
  (S-form grid with the existing admission-year filter).
- Own H1 "Students & Alumni", own meta description (≤160 chars,
  mentions Prof. I-Yun Lisa Hsieh's research group), own canonical
  `https://e3center.caece.net/students/`, own JSON-LD (CollectionPage
  ItemList + BreadcrumbList Home → Students & Alumni).
- Group anchors keep the same slug scheme (`#phd-students`,
  `#master-students`, `#alumni`) for nav subnav links.
- New entry in `contents/pages.json` pages map:
  `"students-page": { "path": "students", "template": "pages/students" }`.

### 4. Homepage

- `templates/home/members.html`: iterates `structures['members']` (now
  PI + Staff only) — the existing `Master Students`/`Alumni` exclusion
  condition becomes dead and is removed. Ph.D. students disappear from
  the landing page.
- Section CTA row gets two buttons side by side: "View center members"
  → `/members/` and "Meet the students" → `/students/`. Reuse
  `.section-cta-btn skewed-block`; if two buttons need a flex tweak,
  scope it under `#members .section-cta` and bump CSS cache-bust in all
  five templates per repo convention.
- `templates/index.html` Organization JSON-LD `member` array: iterate
  `structures['members']` only → students are no longer claimed as
  center members (the PI's conceptual point, encoded in structured data).

### 5. Navigation — `contents/pages.json`

"People" nav group becomes two destinations:

- **Members** → `/members/` (no subnav — two anchor links is too thin
  to justify a dropdown)
- **Students & Alumni** → `/students/` (subnav: Ph.D. Students →
  `/students/#phd-students`, Master Students → `/students/#master-students`,
  Alumni → `/students/#alumni`)

Header, drawer menu, and footer all read pages.json, so they update
automatically. Check the desktop header dropdown and mobile drawer at
all three RWD tiers.

## Out of scope

- No changes to profile detail pages, publications/CV rendering, or the
  Excel workbook format.
- No redirects (no URLs are removed; `/members/` and all profile URLs
  persist).
- Group-life, news, projects, publications sections untouched.

## Verification

- Rebuild with the E3website env; serve `docs/` on port 8001 (8000 is
  production — never touch).
- `/members/`: PI + Staff only, students link-card present.
- `/students/`: all three sections render; alumni year filter works.
- Homepage: PI + Staff cards only, both CTAs work.
- Nav: desktop dropdown + mobile drawer show the new People structure;
  anchor links land on the right groups.
- Profile spot-check: `/members/chihyilu/` (student) and
  `/members/iyunlisahsieh/` (PI) still build at unchanged URLs.
- Sitemap contains `/students/`; build reports 0 SEO warnings.
- `validate_design_tokens.py` passes.
- All checks locally verified before push; work on a feature branch.

## Edge cases

- A future roster section added to SECTION_ORDER lands in `students`
  unless added to `_CENTER_SECTIONS` — safe default given the PI's
  framing (new hires would be deliberate).
- Empty sections (e.g. no Master students some year) already render
  nothing in the listing loop — same behavior as today.
- `/members/` inbound links that expected students (e.g. old
  `/members/#phd-students` anchors in the nav of cached pages) fall back
  to the top of the members page; the students link-card provides the
  onward path.
