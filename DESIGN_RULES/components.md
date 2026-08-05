# Component Intent Map

Part of [DESIGN_RULES/](./README.md). What each component is *for*, which roles and patterns
it uses, and which deviations are sanctioned. **Values live in the CSS, not here** — every
size is a token binding ([typography.md](./typography.md) § Content Roles), so restating rem
per component only creates stale copies (see findings [B-5], [N-5], [D-1]).

A component not listed here has no special rules — the role table, patterns, and quick
checklist fully govern it.

---

## Homepage Hero (`templates/home/home.html`, `style.css`)

The site's one signature moment ([brand.md](./brand.md)): name + the animated hand-drawn
world (`partials/home.svg`). The "3E" marker spells the brand; `.hp-about-us` is a
skewed-block CTA — it still carries its pre-refinement 3px border, a deliberate [B-8]
leftover pending a follow-up call. Nothing else on the homepage may compete with this
moment.

## Section Titles (`style.css`)

`<h2>` at `--fs-h1` (a sanctioned role exception: homepage sections are page-scale
chapters). Wrapped in `.section-title-link` with the shared hover-underline; the "view all"
affordance is that link plus `.section-cta-btn` at the bottom — never a separate pill
(see [patterns.md](./patterns.md) § Section Title with View-all Link).

## Subpage Header (`partials/subpage-header.html`, `subpage.css`)

One row at every width: brand + primary nav (drawer takes over ≤64rem; the inline nav shows
only ≥64.0625rem). Supplies the page's sr-only `<h1>` unless the template passes
`suppressSrH1 = True` ([semantics-a11y.md](./semantics-a11y.md)). The breadcrumb is **not**
in the header — detail pages render `.page-trail` as the first content element
(`.trail-parent` = eyebrow recipe; `.trail-current` = meta role).

### Nav grouping & dropdowns (finding [IA-1])

The inline nav renders `pages['index']['structure']` grouped by the optional `navGroup`
field: consecutive entries sharing a `navGroup` collapse into one **dropdown** (Research =
Publications + Projects; People = Members (`/members/`, no subnav) + Students & Alumni
(`/students/` with `subnav` anchor links: All Students & Alumni / Ph.D. Students / Master
Students / Alumni); News & Life = News + Group Life); entries without the field stay plain
links (About, Contact — Contact is the
JOIN-US conversion target and must never sit behind a dropdown). Nav order follows data
order — the same list drives homepage section order, so never reorder it for nav reasons.

The dropdown reuses the **pub-filter disclosure precedent** (`aria-haspopup` /
`aria-expanded` trigger + inline stroked chevron + panel): hover and `:focus-within` open
the panel via CSS so it works keyboard-first without JS; `general.js` adds click-toggle,
Esc-to-close (refocusing the trigger), and click-outside-close. The panel speaks the
drawer's material language — a miniature skewed block (white surface, 2px `--main-color`
border, hard offset shadow, `--block-skew` with counter-skewed items) — items at the
`.hdr-nav-a` type recipe with ≥44px hit areas. The trigger inherits `.hdr-nav-a` styling
and gets `is-current` when any child link is the active page. Below 64.0625rem the
dropdown does not exist: the drawer takes over and renders the same groups as
non-interactive eyebrow labels above their flat items.

## Publications (listing + detail, `subpage.css`, `publication-item.css`)

Research output is the loudest content on the site ([brand.md](./brand.md) § Decision
principles): row titles bind one tier above news rows (`--fs-lede` vs `--fs-body`, finding
[I-2]) — keep that spread at every breakpoint. Detail-page h1 uses the shared hero-fluid
clamp recipe. Status badges follow the badge pattern, color-coded by `data-status` via
`--status-*` tokens; reuse the same badge for any new lifecycle state. Keyword chips and
show-more pills are flat by the [B-8] surface-kind rule.

**Casing rule:** `text-transform: capitalize` on publication titles exists only on
member-profile pages (`member.css` `.pub-title`); homepage and `/publications/` preserve
original casing.

## Members (homepage cards, `/members/` listing, member profile)

Member rows are **page-defining portraits, not dense rows** — they take the widest type
spread on the site, and the PI featured row (`.mem-group--pi`) sits a step above the other
rows by design. The member-profile `<h1>` binds straight to `--fs-h1` (the sanctioned
detail-h1 exception). Portraits are skewed blocks; the alumni grid is compact and flat.
Bilingual name pairing follows [layout.md](./layout.md) § Casing & Bilingual Pairing.

## News (listing + article, `subpage.css`, `news-item.css`)

Listing: year-grouped rows under a sticky year rail (`--fs-h3` label; on phones a sticky
full-width bar), an ARIA tablist of category filter tabs, jump nav using the eyebrow
recipe, and a three-most-recent-years collapse behind `.news-show-older`. Category coding
comes exclusively from the `--cat-*` token pairs ([color.md](./color.md) § News Category
Tokens); on phones the badge demotes to a bare `--cat-*-text` label (badge pattern's phone
demotion). Thumbnails and inline article images are flat ([B-8]).

Article: h1 uses the hero-fluid clamp recipe; body is a unified-prose surface. **All
headings inside `.news-item-body` render at `--fw-h1` weight — intentional editorial
gravitas (finding [W-2]); maintain it for new content blocks.**

## Projects (listing + detail, `subpage.css`, `project-item.css`)

Project rows share the news-row density tier. Detail pages: h1 on the hero-fluid clamp,
lede one tier above prose (sanctioned Lede role), body/Chinese body as unified-prose
surfaces. Role/status/honor pills are flat badges. The two-column detail layout stacks at
its component-local 56rem breakpoint ([responsive.md](./responsive.md) § Component-local
breakpoints).

## Contact (`templates/pages/contact.html`, `subpage.css`)

The one subpage with a visible display-scale h1 (`.contact-lead`). Info labels use the
eyebrow recipe at its sanctioned 0.16em spacing variant; the form follows the 16px
auto-zoom floor ([semantics-a11y.md](./semantics-a11y.md) § Forms). Contains the site's
single all-caps CTA ("JOIN US" territory — one per page, [brand.md](./brand.md) § Voice).

## Group Life, Footer, Menu

No special rules — roles, patterns, and the motif split cover them. The menu drawer is a
skewed surface whose `border-left` keeps a pre-refinement 3px weight (the second [B-8]
leftover). The side-rail nav is a homepage-only affordance.
