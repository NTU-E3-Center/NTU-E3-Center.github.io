# Concrete Page Recommendations for E3 Center

**Last updated:** 2026-05-14 (reconciled against current site state — see Status below)
**Originally written:** 2026-05-06
**Companion to:** [`../analysis/2026-05-06_12mo-insights.md`](../analysis/2026-05-06_12mo-insights.md), [`../strategy/search-intent.md`](../strategy/search-intent.md), [`../strategy/backlinks.md`](../strategy/backlinks.md).
**Audience priorities:**

1. **Primary** — researchers, industry, government seeking collaboration on **sustainable energy in Taiwan / NTU**, plus prospective **PhD / Masters applicants** in similar topics.
2. **Secondary** — visitors interested in the lab's research insights. Research subpages are still being designed; for now the lab is promoted through **publications** and **news** only.

This document is a phased, file-specific action plan. Each item names the file to edit, the change to make, and why.

---

## Status — reconciled 2026-05-14

This doc was written 2026-05-06. The site has changed materially since; this
section reconciles every item. **Legend:** ✅ done · 🟡 partial · ⬜ open · 🔮 future-by-design · 🆕 new (not in original doc).

### What changed on the site since 2026-05-06

- **Publications & member subpages were redesigned.** Publication rows now use the shared `.news-row` pattern; a member's own name is **bolded** in author lists; the Google Scholar CTA moved into the "All Publications" section header. Member subpages already carry rich SEO meta (canonical, `Person` + `BreadcrumbList` JSON-LD).
- **Member content was restructured.** Each member is now a self-contained folder: `contents/members/{webId}/{member.json, about.md, photo.{ext}}`. **The old paths `contents/articles/members-{about,position,interest}/` and `contents/structures/members/` are now gitignored *build artifacts*** — regenerated every build. Any instruction in this doc that names one of those paths must be redirected to the per-member folder (see §5, corrected).
- **`base.html` default `<meta description>` and `<meta keywords>` were rewritten** (§1.1) — the `<title>` was *not*.
- **A new `/projects/` page was added** — not covered by the original doc; see new §6.5.

### Item-by-item status

| Item | Status | Note |
|---|---|---|
| §1.1 default `<title>` | ⬜ open | still `E3 Center \| National Taiwan University` |
| §1.1 default `<meta description>` | ✅ done | rewritten, front-loads research areas |
| §1.1 default `<meta keywords>` | ✅ done | matches the suggested long list |
| §1.2 per-page `<html lang>` | ⬜ open | still hard-coded `lang="en"` in `base.html` |
| §1.3 replace `JOIN US` anchor | ✅ done (interim) | `/#contact-us` → `/contact/`; broken anchor fixed. The applicant-specific `/join/` page is still §2.1. |
| §1.4 about.md research-area headings | ⬜ open | `about.md` still flowing prose — no headings, bullets, or CTAs |
| §1.5 member trailing-slash canonical | 🟡 partial | `member.html` emits `<link rel="canonical" …/{pageLink}/>` — fix shipped; confirm GSC dupes clear |
| §2.1 `/join/` page | ⬜ open | not in `pages.json` |
| §2.2 `/collaborate/` page | ⬜ open | not in `pages.json` |
| §2.3 surface new pages in nav/footer | ⬜ open | blocked on §2.1/§2.2 |
| §3.1 topic-first news titles | ⬜ open | editorial practice — apply going forward |
| §3.2 news-body context openings | ⬜ open | editorial practice; note: `news-item.html` already auto-generates the meta description from the body |
| §3.3 `topics` field on news items | 🟡 partial | **`news-item.html` already supports `news.topics`** (feeds `<meta keywords>`) — but **0 of 28 items** in `news.json` have it populated. Template-ready, data-empty. |
| §3.4 cross-link news → members | ⬜ open | editorial practice |
| §4.1 per-publication URLs | ⬜ open | `/publications/` is still a single page |
| §4.2 `keywords` on every publication | ✅ done (mechanism) | publications carry `keywords`, rendered as chips; controlled-vocab *completeness* is an ongoing data task |
| §4.3 plain-language summary per publication | ⬜ open | no summary/abstract field yet |
| §4.4 make `/publications/` rank | 🟡 partial | page has `canonicalLink` + `CollectionPage` JSON-LD + `description`/`keywords`; the recent redesign added section grouping. "Filter by topic" UI not added. |
| §5 member-page topic emphasis | 🟡 partial | SEO meta is rich; publication section redesigned. **Path corrected below** — interests now live in `member.json`. |
| §5.1 PI page specifics | 🟡 partial | member template auto-generates title/description/JSON-LD; PI-specific copy tweaks unverified |
| §6 research subpages | 🔮 future | no `/research/` yet — still by design |
| §6.5 `/projects/` page SEO | 🆕 open | new page exists; needs the same treatment as §2 pages — see new §6.5 |

### Highest-value still-open items

In priority order, the cheap wins not yet shipped:

1. **§1.1 title rewrite** — one line in `base.html`, recovers brand-search CTR.
2. **§3.3 populate `news.topics`** — the template already renders it; this is pure data entry on `news.json`.
3. **§1.4 about.md research-area headings** — one Markdown file, big topical-signal gain.
4. **§1.2 per-page `<html lang>`** — small `base.html` change, helps the Chinese-search audience.
5. **§2.1 `/join/` page** — the strategic move; highest conversion value.

---

## 0. The strategic frame

You have two primary visitors who arrive with very different searches:

| Visitor | What they typed | What they need on landing | Your current state |
|---|---|---|---|
| **Collaboration seeker** (faculty, industry, gov) | "transportation electrification research taiwan", "NTU sustainable energy lab", "hydrogen economy researcher taiwan" | Proof of relevant expertise, recent publications in the topic, named experts, clear contact path | No topical landing exists. Homepage scrolls past everything generically. |
| **PhD / Masters applicant** | "ntu civil engineering phd sustainable energy", "i-yun hsieh phd students", "join e3 lab", "ntu energy masters" | Open positions, application process, what life in the lab is like, PI contact | "JOIN US" is a `#contact-us` anchor — invisible to Search and unspecific to applicant intent. |

Both audiences currently bounce off your homepage if they didn't already know the name. The plan below gives each audience a dedicated entry page within the existing site architecture, then strengthens news and publications as the topical content engine until research subpages ship.

---

## 1. Phase 1 — Same-day quick wins (no new pages, just edits)

These are 30–60-minute edits that immediately improve how your existing pages appear in Search results. Order matters: do them in sequence.

### 1.1 Rewrite default `<title>`, `<meta description>`, and `<meta keywords>` in `templates/base.html`

> **Status (2026-05-14): 🟡 partial.** The `<meta description>` and
> `<meta keywords>` have already been rewritten (the keywords match the
> suggestion below; the description is a shorter variant that still
> front-loads the research areas — fine, leave it). **Only the `<title>` is
> still the old short string.** The one remaining edit here is the title.

**Current** (`templates/base.html:1-4`):

```jinja
{% set defaultTitle = 'E3 Center | National Taiwan University' %}
{% set defaultDescription = 'Housed in the Department of Civil Engineering at National Taiwan University (NTU), E3 research center, directed by Professor I-Yun Lisa Hsieh (謝依芸), is dedicated to overcoming the challenges of sustainable energy transition.' %}
{% set defaultKeywords = 'E3 Center, sustainable energy transition, NTU, 台灣大學, 台大, energy research, climate policy' %}
```

**Problems:**

- Title is too short and carries no research keywords. From your GSC data, queries like `i yun` (pos 3.4, **0 clicks**) and `caece.net` (pos 8.6, **0 clicks**) prove the snippet does not signal "this is what I was looking for."
- Description is one long sentence; Google often truncates it before any research-area keyword appears.
- Keywords miss the lab's actual research areas as listed in `contents/articles/about.md` (transportation electrification, hydrogen economy, smart grid, green finance) — and miss the PI's full Chinese name `謝依芸`.

**Suggested replacement:**

```jinja
{% set defaultTitle = 'E3 Center · Sustainable Energy Research · Prof. I-Yun Lisa Hsieh (謝依芸) · NTU 台大' %}
{% set defaultDescription = 'E3 Center at National Taiwan University researches sustainable energy transition — transportation electrification, renewable energy, hydrogen economy, smart grid, carbon policy, and green finance. Directed by Prof. I-Yun Lisa Hsieh (謝依芸). Open to research collaboration and graduate applications.' %}
{% set defaultKeywords = 'E3 Center, E3 group, sustainable energy transition, transportation electrification, electric mobility, renewable energy, hydrogen economy, smart grid, carbon policy, green finance, net-zero Taiwan, NTU energy lab, NTU civil engineering, I-Yun Lisa Hsieh, 謝依芸, 台大, 國立臺灣大學, 永續能源, 淨零' %}
```

**Why this wording:**

- Title carries **brand + research positioning + PI name + institution** in both languages so any of your current navigational queries (`e3 center`, `lisa hsieh`, `謝依芸 台大`, `caece.net`, `i yun`) sees a snippet that confirms identity.
- Description front-loads the **research areas** so Google can match topical queries even if the user never lands on a topic page. The "Open to research collaboration and graduate applications" sentence is intentionally written to satisfy *both* audience 1 and audience 2 at the SERP level.
- Keywords (though Google ignores `meta keywords`, Bing and other engines still use them as a weak signal — and your team uses them internally for site search) should reflect *actual* research areas, not abstract theme words.

### 1.2 Add `lang` on per-page basis & enable bilingual signaling

**Current** (`templates/base.html:6`): `<html lang="en">` is hard-coded.

Your audience is ~90% Taiwan and a meaningful minority searches in Chinese (`謝依芸`, `謝依芸 台大`, `呂芷儀`, `蔡家妤`). Hard-coded `lang="en"` tells Google your content is English-only — it then under-serves your Chinese-search audience and over-serves Translated results (33 impressions, **zero clicks** in your data).

**Suggested:**

```jinja
<html lang="{{ pageLang if pageLang is defined else 'en' }}">
```

Then on member subpages where the bio includes Chinese text, pass `pageLang='zh-TW'` from the render block. For pages with mixed content, use `lang="en"` on the `<html>` tag and add `lang="zh-TW"` to the specific Chinese-language elements (e.g., the `chiName` span on member cards).

Future-proof by adding an `hreflang` block once a Chinese version of any page exists:

```html
<link rel="alternate" hreflang="en" href="https://e3center.caece.net/" />
<link rel="alternate" hreflang="zh-TW" href="https://e3center.caece.net/zh/" />
<link rel="alternate" hreflang="x-default" href="https://e3center.caece.net/" />
```

Skip this until you actually publish a `/zh/` variant — premature `hreflang` causes more confusion than it solves.

### 1.3 Replace the homepage `JOIN US` anchor link with a real URL

**Current** (`contents/articles/about.md:5`):

```markdown
[JOIN US](/#contact-us) on this journey...
```

**Problem:** `#contact-us` is an in-page anchor. Google cannot rank it as a separate page, and a prospective applicant who searches `join e3 lab` or `ntu sustainable energy phd` will never see this offer surface in Search results.

**Suggested:**

```markdown
[JOIN US](/join/) on this journey...
```

…and create the `/join/` page as described in §2.1. Until that page exists, leave the current anchor — don't ship a broken link.

### 1.4 Tighten the homepage About prose with research-area keywords as structured headings

**Current** (`contents/articles/about.md`): the research areas are buried in flowing prose ("electric mobility... renewable energy, smart grid management, green logistics, and hydrogen energy economics... carbon pricing and green finance").

Google reads `<h2>`/`<h3>` content with much higher weight than body prose. A collaborator searching for one specific area is currently invisible to a page where that area exists only as a comma-separated noun.

**Suggested rewrite** (still concise, still readable, but structured):

```markdown
Housed in the Department of Civil Engineering at National Taiwan University (NTU), our center, directed by Professor I-Yun Lisa Hsieh (謝依芸), is dedicated to overcoming the challenges of sustainable energy transition. We focus on reducing CO<sub>2</sub> and pollutant emissions while addressing rising energy demand, accelerating the global and local shift to net-zero emissions through innovative research and data-driven solutions.

### Our research areas

- **Transportation electrification** — electric mobility, EV adoption pathways, charging infrastructure
- **Renewable energy systems** — solar, wind, integration with the Taiwan grid
- **Smart grid management** — demand response, distributed energy resources
- **Green logistics** — low-carbon freight and supply chains
- **Hydrogen economy** — production, transport, end-use economics
- **Climate policy & green finance** — carbon pricing, net-zero pathways, just transition

[**Open to research collaboration**](/collaborate/) — academic, industry, and government partnerships welcome.
[**Apply to join the lab**](/join/) — PhD and Masters positions in sustainable energy.
```

**Why this works:**

- Each research area becomes its own paragraph-level keyword target. Even before topic subpages exist, the homepage starts ranking weakly for `transportation electrification`, `hydrogen economy`, `smart grid Taiwan` etc. — strong enough to start collecting impressions, which is the precondition for everything else.
- The two CTAs at the bottom serve your two audiences directly. They are visible to *every* visitor who reaches the about section, not just those who scroll to the contact section.
- The bullet list with bolded leads is the most-skimmed format on the open web. Both audiences appreciate it: the collaborator scans for "is my topic here?", the applicant scans for "is what I want to study here?".

### 1.5 Resolve member-page trailing-slash duplicates

From [`../analysis/2026-05-06_12mo-insights.md`](../analysis/2026-05-06_12mo-insights.md) §5.2: Google indexes both `members/yuanhsichien/` and `members/yuanhsichien` as separate URLs, splitting ranking signals. Same for `yutinghuang`.

**Fix:** pick one canonical form (the project convention is *with* trailing slash, since `pages.json` URLs and `build.py` output `docs/{path}/index.html`) and either:

- Add a `<link rel="canonical" href=".../yuanhsichien/">` on the no-slash variant, or
- Set up GitHub Pages 301 redirects from no-slash → slash form.

Until this is fixed, every backlink someone builds gets diluted across two URLs.

---

## 2. Phase 2 — Two new audience landing pages (1–2 weeks)

This is the highest-leverage content work given your current site. Each page targets one audience's intent with one URL.

### 2.1 `/join/` — for prospective PhD and Masters applicants

**Target queries:**

- `ntu civil engineering phd`
- `ntu sustainable energy phd / masters`
- `i-yun lisa hsieh phd students`
- `謝依芸 學生招募`
- `ntu energy lab application`
- `e3 center recruiting`

**File structure (matches existing convention):**

- `contents/articles/join.md` — page body content (Markdown)
- `contents/structures/pages.json` — add a new entry pointing to a new template
- `templates/pages/join.html` — new template, structured similarly to `templates/pages/news.html`

**Recommended page sections:**

1. **One-line opener** confirming who the page is for: *"Looking to pursue research in sustainable energy at NTU? E3 Center welcomes PhD and Masters applicants whose interests align with our work."*
2. **What we research** — 4–6 bullets (cross-linked to `/research/{topic}/` once those exist; for now, cross-link to representative publications/news).
3. **Who we're looking for** — student profile in plain language. Skills welcomed (Python, GIS, optimization, policy analysis, fieldwork). No "must-haves" beyond curiosity.
4. **Available positions** — current openings or "currently full" with a date stamp. Even a "currently full, applications reviewed every September for following year" line satisfies the searcher.
5. **How to apply** — explicit pointer to NTU Civil Engineering's application page + a "before applying, email Prof. Hsieh with your CV and a 1-page research statement" instruction.
6. **What life in the lab looks like** — 2–3 sentences on weekly seminars, conference travel, lab culture. Optionally, a short quote or two from current students.
7. **FAQ** — 4–6 common questions. *Do I need a Masters before PhD? Are funded positions available? Can I work in English? Can international students apply? Do you take undergraduate research assistants?*
8. **Contact** — explicit email, with a one-line "include 'PhD inquiry' or 'Masters inquiry' in your subject line" instruction.

**SEO settings for the page:**

```jinja
{% set title = 'Join the Lab · PhD & Masters Positions in Sustainable Energy · E3 Center · NTU' %}
{% set description = 'E3 Center at NTU is recruiting PhD and Masters students in sustainable energy, transportation electrification, renewable energy, hydrogen economy, and climate policy. Application process, positions, and contact for Prof. I-Yun Lisa Hsieh (謝依芸).' %}
{% set canonicalLink = 'https://e3center.caece.net/join/' %}
```

**Why this works for the searcher:** A prospective applicant types `ntu sustainable energy phd` — they see a SERP snippet that confirms the lab exists, names the PI, lists topics, and promises an application process. They click. They land on a page that gives them everything in 60 seconds. This is the textbook search-intent match for transactional intent.

### 2.2 `/collaborate/` — for research and industry collaboration

**Target queries:**

- `ntu sustainable energy research collaboration`
- `transportation electrification research partner taiwan`
- `taiwan energy policy research lab`
- `hydrogen economy research taiwan`
- `industry partnership sustainable energy ntu`
- `ntu civil engineering research center`

**File structure:** mirror `/join/`:

- `contents/articles/collaborate.md`
- `contents/structures/pages.json` entry
- `templates/pages/collaborate.html`

**Recommended page sections:**

1. **Opener** — "E3 Center collaborates with academic, industry, and government partners on sustainable energy challenges in Taiwan and the Asia-Pacific region."
2. **Research themes we partner on** — same 6 themes from §1.4, but framed as collaboration entry points: *"We partner with: utilities on smart grid integration; transit agencies on electrification pathways; ministries on net-zero scenario modeling; industry consortia on hydrogen economics."*
3. **Types of collaboration we welcome:**
    - **Academic:** joint publications, workshops, visiting scholars, exchange students.
    - **Industry:** sponsored research, MOUs, internships, tech transfer.
    - **Government / NGO:** commissioned studies, policy briefs, working groups.
4. **Past and current partners** — institution and agency logos / list. Each linked to their own site (this is also where reciprocal backlinks from sister labs and funders accumulate — see `../strategy/backlinks.md` §5).
5. **Recent collaborative output** — 4–6 publications or reports that came out of partnerships, linked.
6. **How to start a conversation** — a short form or email path with explicit guidance: *"In your message please include: your organization, the topic of interest, and the rough timeframe. Initial replies within one week."*

**SEO settings:**

```jinja
{% set title = 'Research Collaboration · Sustainable Energy Partnerships · E3 Center · NTU' %}
{% set description = 'Partner with E3 Center at National Taiwan University on transportation electrification, renewable energy, hydrogen economy, smart grid, and climate policy. Academic, industry, and government collaborations welcome.' %}
{% set canonicalLink = 'https://e3center.caece.net/collaborate/' %}
```

**Why a separate page (not combined with `/join/`):** Different intents, different searchers, different snippets needed. A prospective PhD student and a ministry official looking for a research partner will skim the SERP differently and click on different titles. One combined page tries to serve both and confuses Google about which intent it serves best — which means it ranks for neither.

> *Pragmatic exception:* if you genuinely don't have time to maintain two pages, ship `/join/` first (higher click volume historically for academic labs) and add `/collaborate/` once your team has bandwidth.

### 2.3 Update the homepage to surface both new pages

Once both pages exist:

- **Header navigation** (`templates/partials/menu.html`): add `Join` and `Collaborate` as top-level items, or nest them under a single `Get Involved` dropdown.
- **Footer** (`templates/partials/footer.html`): include both as direct links.
- **About section** (`contents/articles/about.md`): the two CTA links from §1.4 now go live.

Internal links from the homepage and footer accelerate Google's discovery and indexing of the new pages dramatically (see `../strategy/backlinks.md` §2.2).

---

## 3. Phase 3 — Make the news section your topical SEO engine (ongoing)

You said the news section and publications are the only existing channels. News, written well, is the strongest of the two because each post is a fresh, dated, indexable URL with topical content. Three changes to how news is written and structured will compound over time.

### 3.1 Rewrite news titles to lead with the topic, not the action

In `contents/structures/news.json`, the `title` field becomes the `<title>` and SERP headline. Most academic-lab news titles fail SEO because they lead with what *the lab did* rather than what the *topic is*.

| Weak | Strong |
|---|---|
| "Lab attends APEC Energy Working Group meeting" | "Transportation electrification policy: E3 Center presents Taiwan roadmap at APEC Energy Working Group" |
| "Paper accepted in *Energy Policy*" | "Carbon pricing in Taiwan: new E3 Center paper in *Energy Policy* analyzes ETS design options" |
| "Prof. Hsieh gives invited talk at NCKU" | "Hydrogen economy in Asia-Pacific: Prof. Hsieh keynote at NCKU energy symposium" |
| "Lab welcomes new students" | "E3 Center welcomes 2026 cohort: 3 new PhD students in sustainable energy" |

**Why:** The "Strong" column ranks for topical queries *and* still satisfies anyone who searches the brand or event name. The "Weak" column ranks only for queries that include "APEC", "Energy Policy", "NCKU" — extremely narrow.

Where the official event name is itself the search target (e.g. coverage of a conference where someone might search the conference name), keep the conference name in the title but lead with the topic.

### 3.2 Open every news body with 2–3 sentences of context

The news template (`templates/pages/news/news-item.html`) already auto-generates `<meta description>` from the body when `excerpt` isn't set. That generated description is what people see in the SERP. So the *first paragraph of every news article* directly determines click-through.

**Pattern to use:**

> *"[One-sentence plain-language definition of the topic.] [One sentence on why it matters in Taiwan / globally.] [One sentence introducing what this news item adds.]"*

Concrete example for a news post on a hydrogen paper:

> "The hydrogen economy refers to the production, transport, and end-use of hydrogen as an energy carrier, increasingly seen as a complement to direct electrification for hard-to-abate sectors. In Taiwan, hydrogen is a key pillar of the 2050 net-zero pathway. A new E3 Center paper, published in *International Journal of Hydrogen Energy*, models the cost trajectory of green hydrogen in Taiwan under three scenarios."

This three-sentence opener does five jobs at once: defines the topic for a non-expert, signals topical relevance to Google, generates a high-CTR meta description, gives the reader a reason to keep reading, and supplies a citation-ready summary for journalists.

### 3.3 Add a `topics` (or `keywords`) field to each news item

> **Status (2026-05-14): 🟡 partial — template done, data empty.**
> `templates/pages/news/news-item.html` *already* reads `news.topics` and
> feeds it into the page's `<meta keywords>`. But **0 of the 28 items** in
> `contents/structures/news.json` actually have a `topics` array. So the
> remaining work here is **not a template change — it's pure data entry**:
> add a `topics: [...]` array to each news item in `news.json`. Optionally
> also render the tags *visibly* on the news-item and listing pages (the
> template currently only emits them into meta).

Your `news.json` schema can carry a `topics` array per item, mirroring the `keywords` field that publications already have. Render those as visible tags on the news-item page and on the news listing page. Two benefits:

- **For SEO:** explicit topic keywords on the page reinforce Google's classification.
- **For users:** clicking a tag could one day filter the news listing to that topic — useful both for collaborators ("show me all transportation electrification news") and for the topic landing pages (when you build them, the topic page can display the matching news automatically).

Until the topic-landing pages exist, even just rendering the tags as visible labels on the page helps Search and helps users.

### 3.4 Cross-link news to members and to related news

Each news item should already, where natural, mention the member(s) involved. Wrap their names in `<a href="/members/{webId}/">` links. This both:

- Gives member subpages internal-link equity (helping their indexing — which is currently very weak).
- Lets a collaborator clicking from a news item to a member find the rest of that member's work.

A small "Related news" block at the bottom of each news item (showing 2–3 other news posts with overlapping `topics`) also dramatically improves Google's understanding of which posts cluster together topically.

---

## 4. Phase 4 — Optimize the publications page (1 week)

Publications are your second existing content channel. Your GSC data shows the publications page is **not in the top 9 indexed pages** at all — meaning Google barely sees it. That is a significant missed asset.

### 4.1 Make sure each publication has a stable, linkable URL

If `/publications/` is currently a single long page with all entries, individual publications cannot be linked from outside (or from your own news posts). Two options, in order of preference:

**Option A (preferred):** generate one URL per publication, e.g. `/publications/{year}/{slug}/`. The page contains the abstract, keywords, authors (linked to member pages), DOI link, and "related news" if any. This is the same pattern as news items.

**Option B (lower-effort):** keep one long publications page but ensure each entry has a URL fragment (`#pub-2026-foo`) and the page itself is well-structured (h2 by year, h3 by topic). Then internal pages can link to specific entries.

Option A is what most peer labs do (e.g., MIT Energy Initiative, Stanford Doerr) because individual publication pages rank well for the paper's topic and bring topical traffic that the lab homepage cannot.

### 4.2 Use the existing `keywords` field on every publication

Your publications schema already supports `keywords` (rendered in `templates/pages/publications.html`). Every publication should have 4–6 keywords drawn from a shared controlled vocabulary that matches your research themes (the same 6 themes from §1.4). This way:

- Future research-topic pages can auto-populate from publications by matching keywords.
- The publications page becomes filterable by topic.
- Each publication's page (Option A above) ranks for queries that include its keywords.

A controlled vocabulary matters more than freeform keywords: if one paper says "EV charging" and another says "electric vehicle infrastructure", they won't cluster. Pick one term per concept and apply it across all publications.

### 4.3 Add a brief summary per publication

The journal title and authors aren't enough for SEO or for human visitors. A 1–2 sentence summary in plain language, displayed on the publications listing and on each individual page, dramatically improves both. This is a one-time effort across existing publications and a small ongoing cost per new publication.

### 4.4 Make the publications page itself rank

Page-level fixes:

- `<title>`: `Publications · Sustainable Energy Research · E3 Center · NTU`
- `<meta description>`: lists 5–6 keyword themes.
- An H1 + intro paragraph describing what the lab publishes on.
- A "Filter by topic" UI (even a simple anchor-link list to within-page sections) that gives Google explicit topical sections to index.

---

## 5. Phase 5 — Member subpages as collaborator showcase

> **Status (2026-05-14): 🟡 partial.** The member subpage template now carries
> rich SEO meta (canonical, `Person` + `BreadcrumbList` JSON-LD, per-page
> description/keywords) and the publication section was redesigned (rows use
> the `.news-row` pattern; the member's own name is **bolded** in author
> lists). The remaining gap is still **content emphasis** + the corrected
> source path below.

Your member subpage template already has solid SEO meta. The remaining gap is **content emphasis**: most academic member pages emphasize bio/CV, not topics.

For collaborator-driven SEO, every member page should answer "what does this person work on?" in keyword-rich form within the first 200 words. Practical changes:

- **Research interests now live in `contents/members/{webId}/member.json`** under the `interests` array (a list of plain-text topics) — *not* in `contents/articles/members-interest/{webId}.md`, which is now a gitignored build artifact regenerated from the JSON. Edit the `interests` array directly, and lead it with research topics in plain English/Chinese, not biographical narrative.
- Likewise the bio is now `contents/members/{webId}/about.md` (was `contents/articles/members-about/{webId}.md`).
- Make sure the member page renders a "Recent publications" section (it does — `templates/pages/member/member.html`) and that publication titles + keywords appear in the body, not only as image links. *(Done — the recent redesign renders publication rows with titles, bolded authors, and keyword chips as real text.)*
- Cross-link from the member page back to the relevant `/research/{topic}/` page once those exist; until then, link to a representative news item or external review article on the topic.

The PI page (`contents/members/iyunlisahsieh/`) is the natural test case for this format.

### 5.1 The PI page is unusually high-leverage

Prof. Hsieh's individual member subpage receives traffic from queries like `i yun` (pos 3.4, **0 clicks**), `i-yun lisa hsieh`, `lisa hsieh`, `謝依芸`, `謝依芸 台大`. The aggregate is **~1,300 impressions per year** from name searches. CTR on these is well below what it should be at your average rank.

Specific fixes for `/members/iyunlisahsieh/`:

- Title: `Prof. I-Yun Lisa Hsieh (謝依芸) · E3 Center · NTU 國立臺灣大學`
- Meta description: lead with the lab name + research areas + position. *"Prof. I-Yun Lisa Hsieh (謝依芸) directs E3 Center at NTU's Department of Civil Engineering, researching sustainable energy transition, transportation electrification, hydrogen economy, and climate policy."*
- First paragraph of the visible body should mirror the description — both for the user who clicked and for Google's confirmation that the SERP snippet matched the page.
- Include both name spellings (`I-Yun`, `Iyun`, `謝依芸`) somewhere on the page so the page ranks for all variants.

This single page is the most impactful member-page change you can make.

---

## 6. Phase 6 — Future research subpages (notes for when you start designing)

You said the research subpages are still being designed. A few SEO-driven design constraints to bake in *before* implementation, so they ship well from day one:

- **One URL per topic.** `/research/transportation-electrification/`, not `/research/#transportation-electrification`. A section anchor cannot rank.
- **Slug language.** English slugs are fine; Google handles them well in Taiwan SERPs. If you want bilingual URLs (`/research/交通電動化/`), wait until you have a `/zh/` variant of the whole site — bilingual URLs in a monolingual site cause more confusion than they solve.
- **Page archetype** (from `../strategy/search-intent.md` §3.1): topic definition → what the lab does in this area → who works on it (member links) → recent publications (auto-filtered by `keywords`) → recent news (auto-filtered by `topics`) → contact / collaboration CTA.
- **JSON-LD type.** Use `Article` or `WebPage` for topic pages (not `Person` or `Organization`). Add `about` pointing to a controlled-vocabulary term where possible (e.g., a Wikidata Q-ID for "transportation electrification").
- **Word count.** Aim for 800–1500 words of substantive content per topic page. Below 500 words, ranking is much harder.
- **Internal cross-linking.** Each topic page links to: the homepage, the relevant member pages, the publications page (filtered URL if Option A from §4.1 is implemented), and 2–3 sister topic pages. This is the difference between a topic page that compounds and one that stagnates.
- **Keywords field consistency.** The same controlled vocabulary across publications, news `topics`, member `interest`, and research-page slugs. Don't invent new terms per page.

When you start designing, the structure to mirror is what big-lab sites already use. Look at, in order: **MIT Energy Initiative research pages**, **Stanford Doerr School research themes**, **Imperial College Energy Futures Lab themes**.

---

## 6.5 The `/projects/` page (added since this doc was written)

> **Status (2026-05-14): 🆕 page exists, page-level SEO already solid.**

A `/projects/` page now exists (`templates/pages/projects.html`, data in `contents/projects/projects.json`) — a funded-projects showcase grouped by funding source (NSTC, industry-academia, etc.), each item carrying bilingual titles, grant number, role, dates, funding agency, and status. It already ships with a good `description`, `keywords`, `canonicalLink`, and `ItemList` JSON-LD. Page-level SEO is in good shape — no rewrite needed.

The remaining gaps mirror the publications-page gaps (§4):

### 6.5.1 No per-project URLs

Like `/publications/`, the page is one long list — an individual project can't be linked from a news post, a member page, or a funder's site. **Same fix as §4.1, Option A:** generate `/projects/{slug}/` (slug from `grantNumber` or an English-title slug). Each project page: bilingual title, abstract/summary, funding agency (linked), partners (linked), dates, members involved (linked to `/members/{webId}/`), and related publications/news. This is what makes a project rank for *its own topic* — "green finance net-zero Taiwan India", "green power wheeling storage dispatch optimization" — queries the lab homepage can't win.

### 6.5.2 No `topics` / `keywords` per project

`projects.json` items have no topical field. Add a `topics` array per project drawn from the **same controlled vocabulary** as publications `keywords` and news `topics` (the 6 themes from §1.4). This is the join key that lets a future `/research/{topic}/` page auto-populate "projects in this area" — exactly as it will for publications and news.

### 6.5.3 No cross-linking

Each project should link to:
- the **member(s)** involved (`/members/{webId}/`) — gives member pages internal-link equity;
- the **publications** that came out of the grant (once per-publication URLs exist, §4.1);
- the **funding agency** — and conversely, NSTC / industry-partner project registries often link *back* to the grantee's project page. That reciprocal link is high-quality and free (see `../strategy/backlinks.md` §5). A project page with the grant number on it is the natural landing target for those links.

### 6.5.4 Add `/projects/` to nav/footer and the homepage

Same as §2.3 — once it's a real page, surface it in `templates/partials/menu.html` and `footer.html`. For the **collaboration-seeker audience** (audience 1), a projects list is strong proof-of-relevant-expertise: it shows funded, current, named work. Consider linking to it from the eventual `/collaborate/` page (§2.2) as evidence.

**Priority:** page-level SEO is done, so this is not urgent. Do 6.5.4 (nav/footer) cheaply now; fold 6.5.1–6.5.3 into the same effort as the §4 publications work, since they share the per-entry-URL and controlled-vocabulary patterns.

---

## 7. Phase 7 — Tracking & validation

Add to your monthly review (in addition to the metrics in `../strategy/search-intent.md` §6 and `../strategy/backlinks.md` §10):

- **Click-through rate on the rewritten homepage and PI subpage** (Phase 1). Target: `i yun` query CTR moves from 0% to 3%+ within 6 weeks.
- **Indexing of `/join/` and `/collaborate/`** (Phase 2). Verify in GSC > URL Inspection within 2 weeks of publishing.
- **Impressions on news items individually** (Phase 3). Currently your news items don't surface; if even 3–5 news items begin to rank for topical queries within 3 months, the rewrite pattern is working.
- **Number of publications appearing in Search** (Phase 4). Target: at least 5 distinct publication URLs (or anchor URLs) receiving impressions within 6 months of Phase-4 changes.
- **Search Console coverage report.** Track *Discovered but not indexed* count — it should drop as internal linking improves and topical content lands.

---

## 8. Recommended execution order

> **Updated 2026-05-14.** Several Phase-1 items already shipped (§1.1 description+keywords, §1.3 anchor fix, §1.5 canonical). The sequence below is re-scoped around what's *left* — see the Status section at the top for the full picture.

| Week | What's left | Why |
|---|---|---|
| 1 | §1.1 **title** rewrite (one line in `base.html`) + §1.2 per-page `<html lang>`. | The last two cheap `base.html` wins. Description/keywords already done. |
| 1 | §1.4 (about.md research-area headings). | Cheap, immediate topical signal on homepage — still fully open. |
| 1 | §3.3 **populate `news.topics`** in `news.json` (data entry — template already supports it). | Near-zero effort; turns on per-news topical signals retroactively. |
| 2 | §2.1 (`/join/` page). | Highest conversion-value page given your stated audience priorities. |
| 3 | §2.2 (`/collaborate/` page) + §2.3 + §6.5.4 (nav/footer — add `/join/`, `/collaborate/`, `/projects/`). | Completes the audience-landing set; surfaces the new projects page. |
| 3–4 | §5.1 (PI page copy specifics). | The member SEO meta is already rich; this is the targeted-copy pass. |
| 4–6 | §3.1–3.2, §3.4 (news editorial patterns) — apply to new posts and retroactively to the top 5 existing items. | Builds topical content stock. |
| 5–6 | §4 (publications) + §6.5.1–6.5.3 (projects per-entry URLs + `topics` + cross-links). | Same per-entry-URL + controlled-vocabulary pattern — do them together. |
| Ongoing | §5 (member-page topic emphasis) — edit `interests` in `contents/members/{webId}/member.json`. | Apply gradually as members send updates. |
| Later | §6 (research subpages design). | Wait until the backlog above is shipped. |

You don't need to do this all at once. The remaining Phase-1 items (title, `lang`, about.md headings, `news.topics` data) are a single afternoon and will still move metrics within a month. §2 is the strategic move — it gives both stated audiences a real entry point. Everything after that compounds.

---

## 9. The shortest possible summary

You currently rank for *who you are* and not *what you do*, and you still have no dedicated entry pages for either of your stated primary audiences. The plan in two sentences:

1. **Finish the title/meta + on-page-signal work.** The default `<meta description>` and `<meta keywords>` are already rewritten; what's left is the `<title>`, per-page `<html lang>`, the about.md research-area headings, and populating `news.topics` (the template already renders it). All small, all still open.
2. **Ship `/join/` and `/collaborate/` pages** so prospective applicants and prospective collaborators have a real URL to land on, then strengthen the news, publications, and (new) projects channels you already have until topic subpages are ready.

The rest is supporting infrastructure. As of 2026-05-14 the member and publications subpages have had a real SEO/UX redesign and the per-member content is now in `contents/members/{webId}/` — see the Status section at the top for what that changed.
