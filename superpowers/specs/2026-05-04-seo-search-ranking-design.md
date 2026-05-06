# SEO: Make subpages outrank the homepage for entity-specific queries

**Date:** 2026-05-04
**Status:** Draft — pending user review
**Approach:** Hybrid auto-generation with build-time guardrails

## Problem

Two reproducible Google search failures motivate this work:

1. **Searching "I-Yun Lisa Hsieh"** returns the E3 Center homepage instead of her dedicated profile at `/members/iyunlisahsieh/`.
2. **Searching "NTU-UG Joint Seminar"** returns the homepage (or nothing useful) instead of `/news/2026-ntu-ug-joint-seminar/`.

These are two different underlying problems wearing the same surface symptom:

- Problem (1) — "**brand-name conflict**": the homepage `<title>` literally says *"E3 Center - Directed by I-Yun Lisa Hsieh"* and `defaultKeywords` includes "I-Yun Lisa Hsieh, 謝依芸". The homepage and the member subpage are competing for the same query, and the homepage wins on age and authority.
- Problem (2) — "**weak subpage signal**": the news item exists, has a canonical URL, and is in the sitemap, but the page itself is thin (descriptions are generated from the title verbatim, body content is short), and Google has likely either not indexed it yet or treats it as low-priority.

A strong SEO foundation already exists in this repo (per-page canonicals, Open Graph, Twitter cards, JSON-LD `Person` / `NewsArticle` / `Organization`, sitemap covering every page). This spec builds on that foundation rather than rewriting it.

## Goals

- `/members/iyunlisahsieh/` should outrank `/` for the query "I-Yun Lisa Hsieh" (and equivalently for every other E3 member's name).
- `/news/{slug}/` pages should outrank `/` for queries that match their event/title.
- New news items should be indexable within days of publication, not weeks.
- Quality regressions (missing or duplicate descriptions, thin content) should be caught at build time, not in production search results.

## Non-goals

- PageSpeed / Core Web Vitals improvements.
- Off-page SEO (backlinks, outreach).
- AMP, Bing Webmaster Tools, hreflang multilingual alternates.
- Restructuring the URL scheme or page taxonomy.

## Approach

**Hybrid auto-generation with build-time guardrails.** Each page-type-specific meta description is auto-generated from existing source data using a single shared helper. Authors can override with optional fields (`metaDescription` for members, `excerpt` for news items, `description` for the publications listing) when the auto-generated text reads awkwardly. The build script emits non-fatal warnings when descriptions are too short, too long, duplicate, or when news bodies fall below a thin-content threshold.

The structural piece — homepage de-branding plus an upgraded `Organization` JSON-LD that names every member with a URL backreference — is the single most impactful change for problem (1). The auto-generated descriptions and BreadcrumbList JSON-LD are the most impactful change for problem (2).

## Section A — Homepage as identity hub

### A1. `templates/base.html` defaults

Change two top-of-file defaults:

```jinja
{% set defaultTitle = 'E3 Center | National Taiwan University' %}
{% set defaultKeywords = 'E3 Center, sustainable energy transition, NTU, 台灣大學, 台大, energy research, climate policy' %}
```

Director's name removed from both. `defaultDescription` and `defaultCanonicalLink` remain unchanged.

### A2. `templates/home/about.html` internal linking

Wherever Prof. Hsieh's name appears in homepage prose, wrap it in `<a href="/members/iyunlisahsieh/">…</a>`. This concentrates the name's link-weight signal onto her subpage rather than letting it act as a homepage keyword.

### A3. Homepage `Organization` JSON-LD upgrade

Locate the existing `Organization` JSON-LD block (likely `templates/home/about.html` or `templates/index.html` — confirm during implementation). Replace with:

```jsonc
{
  "@context": "https://schema.org",
  "@type": "ResearchOrganization",
  "@id": "https://e3center.caece.net/#organization",
  "name": "E3 Center",
  "alternateName": "Energy, Environment, Engineering Center",
  "url": "https://e3center.caece.net/",
  "logo": "https://e3center.caece.net/assets/images/og-image-1200x630.png",
  "founder": {
    "@type": "Person",
    "@id": "https://e3center.caece.net/members/iyunlisahsieh/#person",
    "name": "I-Yun Lisa Hsieh",
    "url": "https://e3center.caece.net/members/iyunlisahsieh/"
  },
  "member": [
    /* one entry per member, generated from members.json */
    { "@type": "Person", "name": "...", "url": "https://e3center.caece.net/members/{id}/" }
  ],
  "parentOrganization": {
    "@type": "CollegeOrUniversity",
    "name": "National Taiwan University",
    "url": "https://www.ntu.edu.tw"
  }
}
```

The `member` array is rendered by Jinja from `structures.members` so it stays in sync as members are added/removed. Each member entry uses the same `@id` URL that the member subpage's `Person` JSON-LD uses (see B1) — this creates an explicit graph link between homepage Organization and member subpage Person.

## Section B — Subpage content quality

### B1. Member subpages (`templates/pages/member/member.html`)

**Meta description (auto-generated):**

```
Format: "{position}. Research interests: {first sentence of interest_content}."
Truncation: ≤160 chars at word boundary.
Fallback 1 (no interest_content): "{position} at E3 Center, NTU. {first sentence of about content}."
Fallback 2 (nothing usable): current generic boilerplate.
```

**Override:** new optional `metaDescription` column added to `contents/member-info.xlsx`. `excel_to_content.py` propagates the value into each per-member JSON file. If non-empty, used as-is.

**Meta keywords:** replace hardcoded `"E3 Group, e3, NTU, 台大, 台灣大學"` with per-member dynamic value:
```
"{engName}, {chiName}, {chiNameEng}, {position}, {top 3 entries from researchSection.bigTags}"
```

**Person JSON-LD strengthening:**
- Add `"@id": "https://e3center.caece.net{member.pageLink}/#person"`.
- Replace existing `worksFor` block with `"affiliation": { "@id": "https://e3center.caece.net/#organization" }` — `affiliation` is the more general schema.org property, and the bare `@id` reference (no inline `name`/`url`) avoids duplicating data with A3's homepage Organization JSON-LD.
- Existing fields (`name`, `alternateName`, `url`, `jobTitle`, `sameAs`) retained.

**Add BreadcrumbList JSON-LD** as a separate `<script type="application/ld+json">` block:
```jsonc
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://e3center.caece.net/" },
    { "@type": "ListItem", "position": 2, "name": "Members", "item": "https://e3center.caece.net/members/" },
    { "@type": "ListItem", "position": 3, "name": "{member.chiNameEng}" }
  ]
}
```

### B2. News item subpages (`templates/pages/news/news-item.html`)

**Meta description (auto-generated):**

```
Source: stripped-markdown of news['content'], first 160 chars at word boundary.
Markdown stripping: remove headings, bold/italic markers, link syntax (keep text), inline code,
                    image syntax (drop entirely), HTML tags. Collapse whitespace.
Fallback (body empty or "To be updated."): "{news.title} — E3 Center news, {month} 20{year}."
```

**Override:** new optional `"excerpt"` field per item in `contents/structures/news.json`. If non-empty, used as-is.

**Meta keywords:** replace `"E3 Center, e3, NTU, News, {title[:60]}"` with `"E3 Center, NTU news, {category}, 20{year}"` plus the news item's `category` field. Drop the title repeat (it's already in `<title>` and `<h1>`).

**NewsArticle JSON-LD strengthening:**
- Add `"description"` (matching the meta description).
- Add `"dateModified"` from the file mtime of `contents/articles/news/{slug}.md` (ISO 8601, second precision).
- Add `"inLanguage"` — auto-detect from body content (presence of CJK characters → `"zh-TW"`, else `"en"`); default `"en"`.
- Add `"mainEntityOfPage": { "@type": "WebPage", "@id": "{canonical_url}" }`.
- Replace inline `"publisher": { "@type": "Organization", ... }` with `"publisher": { "@id": "https://e3center.caece.net/#organization" }` so the news article's publisher resolves to the same Organization node as A3.

**Add BreadcrumbList JSON-LD:** Home → News → {short title}.

### B3. Listing pages

All three listing pages — Members, News, Publications — share a common pattern: a meta `description` defined per-listing in `pages.json`, a `CollectionPage` JSON-LD whose `mainEntity` is an `ItemList` enumerating the listing's contents, and a `BreadcrumbList` JSON-LD. Differences below.

#### B3.1 Members listing (`/members/`, `templates/pages/members.html`)

**Meta description:** new `description` field on the `members-page` entry in `contents/structures/pages.json`. Initial value:
> "Members of E3 Center, NTU — researchers, students, and alumni working on sustainable energy transition, transportation electrification, and climate policy."

If absent, falls back to the homepage default description.

**CollectionPage + ItemList JSON-LD** — one `Person` entry per member, each `@id` pointing at the corresponding `/members/{id}/#person` (matches B1's per-member `@id`):

```jsonc
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Members | E3 Center",
  "url": "https://e3center.caece.net/members/",
  "isPartOf": { "@id": "https://e3center.caece.net/#organization" },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": N,
        "item": {
          "@type": "Person",
          "@id": "https://e3center.caece.net/members/{id}/#person",
          "name": "...",
          "url": "https://e3center.caece.net/members/{id}/"
        }
      }
    ]
  }
}
```

**BreadcrumbList JSON-LD:** Home → Members.

#### B3.2 News listing (`/news/`, `templates/pages/news.html`)

**Meta description:** new `description` field on the `news` entry in `contents/structures/pages.json`. Initial value:
> "E3 Center news, awards, seminars, and announcements from National Taiwan University."

If absent, falls back to the homepage default description.

**CollectionPage + ItemList JSON-LD** — one `NewsArticle` entry per news item that has a `pageLink` (external-link-only items are omitted, since their canonical URL isn't on this site):

```jsonc
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "News | E3 Center",
  "url": "https://e3center.caece.net/news/",
  "isPartOf": { "@id": "https://e3center.caece.net/#organization" },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": N,
        "item": {
          "@type": "NewsArticle",
          "headline": "...",
          "datePublished": "YYYY-MM",
          "url": "https://e3center.caece.net{pageLink}"
        }
      }
    ]
  }
}
```

**BreadcrumbList JSON-LD:** Home → News.

#### B3.3 Publications listing (`/publications/`, `templates/pages/publications.html`)

**Meta description:** new `description` field on the `publications-page` entry in `contents/structures/pages.json`. Initial value:
> "Peer-reviewed publications from E3 Center, NTU, on sustainable energy transition, transportation electrification, and climate policy."

If absent, falls back to the homepage default description.

**Per-publication keywords (NEW data):** add optional `"keywords": ["...", "..."]` array to each entry in `contents/structures/publications.json`. Populate from the keywords most journal articles publish in their first-page metadata. Initial scope: last 3 years of `"E3": true && status: "published"` publications. Older entries can leave `keywords` empty.

**Visible keyword chips:** `templates/pages/publications.html` renders each publication's `keywords` as small chips below its metadata block (matching existing visual language). Real on-page text — far higher SEO weight than meta tags.

**Add CollectionPage + ItemList JSON-LD** below the existing page header:

```jsonc
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Publications | E3 Center",
  "url": "https://e3center.caece.net/publications/",
  "isPartOf": { "@id": "https://e3center.caece.net/#organization" },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      /* one ScholarlyArticle per E3 publication */
      {
        "@type": "ListItem",
        "position": N,
        "item": {
          "@type": "ScholarlyArticle",
          "headline": "...",
          "author": [...],
          "datePublished": "YYYY",
          "isPartOf": { "@type": "Periodical", "name": "{journal}" },
          "url": "{DOI/external link}",
          "keywords": [...]
        }
      }
    ]
  }
}
```

The same per-publication `keywords` array is also emitted on each member subpage's publication list — every place an article appears, its topical keywords reinforce the page it's on.

**BreadcrumbList JSON-LD:** Home → Publications.

### B4. Cross-cutting helper

The auto-generation + override + truncation logic lives in one place:

```python
# build.py
def generate_meta_description(
    primary: str | None,        # author override; used as-is if non-empty
    *fallback_sources: str,     # tried in order
    max_chars: int = 160,
    min_chars: int = 70,
) -> str:
    """Returns a description ≤ max_chars, truncated at word boundary.
    First non-empty source wins. Used by member, news, and publications templates
    (passed in as a Jinja2 global)."""
```

Same function used everywhere → consistent behavior, single place to evolve the truncation/markdown-stripping rules.

## Section C — Discoverability & process

### C1. `static/robots.txt`

```
User-agent: *
Allow: /
Disallow: /editor/

Sitemap: https://e3center.caece.net/sitemap.xml
```

Single new file. Picked up by the existing static-asset copy step in `build.py`. The `Disallow: /editor/` line excludes the internal editors dashboard from crawl (see C1.5).

### C1.5. Deindex internal pages

The editors dashboard at `/editor/` is an internal authoring tool with no value as a public search result. Two reinforcing fixes:

- **`static/editor/index.html`**: add `<meta name="robots" content="noindex, nofollow">` inside `<head>`. This is the primary signal — even crawlers that ignore robots.txt will respect `noindex`.
- **`static/robots.txt`**: `Disallow: /editor/` (already in C1) tells well-behaved crawlers not to fetch the page in the first place.

The two layers protect against different failure modes: `noindex` ensures the page never appears in results even if crawled, `Disallow` reduces unnecessary crawling of an internal tool. If `/editor/` is already indexed, after deploying these changes use GSC → URL Removal to expedite removal.

### C2. Sitemap improvements (`build.py:355` `generate_sitemap`)

Three tweaks to the existing generator:

| Change | Current | New |
|---|---|---|
| News `lastmod` | today (every build) | mtime of `contents/articles/news/{slug}.md` |
| Member `lastmod` | today (every build) | mtime of `contents/member-info.xlsx` |
| News `priority` | 0.5 | 0.6 |
| Member `priority` | 0.6 | 0.7 |

`lastmod` per-source-file means Google sees real freshness signals — a six-month-old news item correctly looks unchanged, a new one looks new.

### C3. Build-time validation (`build.py`, new `validate_seo()`)

Runs after page rendering, before `generate_sitemap()`. Walks the rendered `docs/` HTML files and emits warnings (printed in yellow ANSI, non-fatal). Final line: `SEO check: {N} warnings (0 errors).`

| Check | Warns when |
|---|---|
| Description length | < 70 chars or > 160 chars |
| Duplicate descriptions | Same description appears on ≥ 2 pages |
| Title length | < 30 chars or > 60 chars |
| News body word count | < 200 words (excludes hero caption, breadcrumbs) |
| Missing canonical | Rendered HTML lacks `<link rel="canonical">` |
| JSON-LD parse error | Any `<script type="application/ld+json">` block isn't valid JSON |

Implementation: parse rendered HTML via `BeautifulSoup` (already a transitively common dep — verify in `requirements.txt`; add if missing). Walk each `docs/**/index.html`, run the checks, accumulate results.

Warn-but-don't-fail rationale: a missing description on a half-drafted news item shouldn't block deployment of unrelated changes.

### C4. GSC runbook (`SEO-RUNBOOK.md` at repo root)

Operator-facing doc, not developer-facing. Sections:

1. **One-time setup** — sitemap submission in GSC, URL-prefix verification (already done; documented for future maintainers), GA property linkage.
2. **After publishing a news item** — GSC URL Inspection → paste new URL → Request Indexing. Typical lag: hours-to-days. Without this: weeks-to-never.
3. **After adding a new member** — same URL Inspection workflow for `/members/{id}/`.
4. **Monthly check (optional)** — GSC Performance tab filtered by query (e.g., "I-Yun Lisa Hsieh") to track average position trend; Pages tab to spot "Discovered – currently not indexed" stragglers.

### C5. Out of scope

PageSpeed/CWV, off-page/backlinks, AMP, Bing Webmaster Tools, hreflang. Each can be revisited independently.

## Implementation order

Recommended phasing for incremental verification:

1. **Phase 1 — Foundation** (no behavior change risk): `static/robots.txt`, editor `noindex`, sitemap improvements (C1, C1.5, C2). Push and verify in GSC that new sitemap is fetched, new robots.txt is served, and `/editor/` is excluded.
2. **Phase 2 — Helper + member subpages** (B4 + B1): the shared `generate_meta_description()` helper and member subpage upgrades. Push, request reindex of 2–3 member URLs in GSC, watch for impressions/position changes over ~2 weeks.
3. **Phase 3 — News subpages** (B2): news item upgrades. Same verify cycle.
4. **Phase 4 — Listing pages + homepage Organization** (B3.1, B3.2, B3.3 + A3): all three listing pages (members, news, publications) get descriptions and `CollectionPage` JSON-LD; homepage Organization JSON-LD upgraded. Watch member subpages — A3's graph linking should improve their rankings as well.
5. **Phase 5 — Homepage retitle** (A1, A2): the structural change. Highest risk of short-term ranking volatility on brand queries. Do last so the subpages are already well-indexed when the homepage stops claiming the director's name.
6. **Phase 6 — Build validation + runbook** (C3, C4): codify the quality bar and the operator process.

Phases 1–5 each end with a deploy and a GSC check before proceeding. Phase 6 can land alongside any earlier phase.

## Verification plan

Per-phase verification uses GSC, not just code review:

- **Phase 1:** GSC → Sitemaps shows new fetch with current `lastmod` values; `robots.txt` served at the live URL with correct content.
- **Phase 2–4:** GSC → URL Inspection on changed URLs shows updated `<title>`, `<meta name="description">`, and structured data. GSC → Performance shows the URL appearing for new queries within 1–2 weeks.
- **Phase 5:** GSC → Performance, query "I-Yun Lisa Hsieh": member subpage position should improve from baseline. Track for at least 4 weeks (Google takes time to re-rank brand queries).
- **Phase 6:** `python build.py` output ends with the SEO check summary line; warnings visible in GitHub Actions log.

## Risks & open questions

- **Risk: Phase 5 short-term volatility.** Removing the director's name from the homepage may temporarily hurt brand-query rankings before the subpage takes over. Mitigated by doing it last (Phase 5) so subpages have authority by then. If volatility is unacceptable, consider Approach B from brainstorming (compromise title) instead.
- **Risk: BeautifulSoup not in requirements.txt.** Verify and add if missing. Trivial, just a flag.
- **Open question: where the existing `Organization` JSON-LD lives.** Spec says "likely `templates/home/about.html` or `templates/index.html`" — implementation will confirm.
- **Open question: Phase 5 scope for non-Hsieh members.** All members benefit from A3's graph linking, but the brand-query problem only affects the director. No additional changes needed for other members beyond what B1 already does.
- **Open question: should we add visible breadcrumb HTML** alongside BreadcrumbList JSON-LD? Out of scope for this spec (UX decision); JSON-LD alone is enough for SEO.
