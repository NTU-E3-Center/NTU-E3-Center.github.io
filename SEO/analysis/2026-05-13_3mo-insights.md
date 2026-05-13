# Search Performance Report — e3center.caece.net (3-month update)

**Source:** [`../data/gsc_2026-05-13_3mo/`](../data/gsc_2026-05-13_3mo/) (Google Search Console export, "Web" search type — multi-CSV)
**Period:** 2026-02-11 → 2026-05-10 (89 days)
**Report generated:** 2026-05-13
**Companion data:** [`../data/ga4_2026-05-12_3mo_queries.csv`](../data/ga4_2026-05-12_3mo_queries.csv) — GA4-side Organic Search Queries export covering 2026-02-12 → 2026-05-12. Numbers track GSC closely (differ by 1–30 impressions per query depending on day-bucket caching). GSC is the canonical source; the GA4 file is kept for traceability.

This is a **delta update** on [`2026-05-06_12mo-insights.md`](2026-05-06_12mo-insights.md) (the canonical baseline) — read that first. This report focuses on what the most recent 3-month window adds, confirms, or contradicts, plus a targeted diagnosis of the 薛丞翔-vs-黃榆庭 visibility question and a meta-tag audit triggered by it.

---

## 1. Executive summary

The trajectory is **flat-to-mildly-positive on every dimension except indexing breadth, which has not moved at all** in the week since the 12mo report.

| Metric | 3mo (this report) | 12mo baseline | Δ |
|---|---:|---:|---|
| Clicks | 242 | 806 | 30% of 12mo total in 24% of the time → click rate up |
| Impressions | 10,455 | 44,983 | 23% — less "e3" noise this quarter |
| CTR | **2.31%** | 1.79% | **+29%** |
| Avg position | 8.27 | 8.73 | +0.5 |
| Distinct URLs with ≥1 impression | **9** | 9 | **0 change** |

Stripping the bare-`e3` gaming-expo noise (78% of impressions, 6 of 242 clicks), the rest of the site converts at **12.6% CTR (90 / 713)**. The audience that finds the site is well-matched; the bottleneck is the funnel above brand search.

The structural takeaways from the 12mo report all still hold:

1. **Discovery is brand-only** — no topical (energy / transportation / policy) queries have appeared.
2. **Indexing breadth is the headline problem** — same 9 URLs as 12 months ago.
3. **Trailing-slash duplicates persist** for `/members/yuanhsichien` and `/members/yutinghuang`.
4. **Brand CTR is excellent** when intent matches.

New since the 12mo report: a concrete reader-facing question (薛丞翔 vs 黃榆庭) that the data answers cleanly — see §9. The diagnosis surfaced two on-page meta-description bugs worth fixing regardless of indexing — see §10.

---

## 2. Workbook contents

| File | Rows | Purpose |
|---|---:|---|
| `Chart.csv` | 89 | Daily clicks / impressions / CTR / position |
| `Queries.csv` | 59 | Search terms users typed |
| `Pages.csv` | 9 | URLs with ≥1 impression |
| `Countries.csv` | 86 | Geographic breakdown |
| `Devices.csv` | 3 | Desktop / Mobile / Tablet |
| `Search appearance.csv` | 1 | Special features (Translated results only) |
| `Filters.csv` | 2 | Search type = Web, Date = Last 3 months |

> **Same anonymization caveat as before:** GSC suppresses rare/sensitive queries. Per-query totals (96 clicks / 8,869 impressions) account for **40% of clicks** and **85% of impressions** of the chart totals (242 / 10,455). The remaining 60% of clicks are real but unattributable to any specific query in this export.

---

## 3. Traffic over time

### Monthly trend (partial months at edges)

| Month | Days | Clicks | Impressions | CTR | Position |
|---|---:|---:|---:|---:|---:|
| 2026-02 (from 11th) | 18 | 39 | 857 | **4.55%** | 7.7 |
| 2026-03 | 31 | 100 | 6,545 | 1.53% | 8.4 |
| 2026-04 | 30 | 69 | 1,671 | **4.13%** | 7.8 |
| 2026-05 (through 10th) | 10 | 34 | 1,382 | 2.46% | 8.7 |

March's low CTR / high impressions is the recurring "e3 expo" noise spike — same pattern as Oct 2025 and Dec 2025 in the 12mo report. February and April are real-signal months: 4–5% CTR when the gaming-expo audience isn't being mis-served.

### Top single days

| Date | Clicks | Impr | CTR | Position | Note |
|---|---:|---:|---:|---:|---|
| 2026-05-05 | **17** | 227 | 7.49% | 7.9 | Recent click-rich day, possibly event-driven |
| 2026-03-12 | 11 | 292 | 3.77% | 7.5 | (Same day flagged in 12mo report) |
| 2026-03-15 | 7 | 302 | 2.32% | 7.7 | |
| 2026-04-13 | 7 | 66 | **10.61%** | 10.0 | Tiny impressions, high CTR — pure brand-search day |

2026-05-05 is the standout: 17 clicks is by far the largest single-day click total in the dataset. Worth correlating with any news/announcement/event on or near that date.

---

## 4. Query analysis

### 4.1 Comparison to 12mo baseline (top 10 queries by 3mo clicks)

| Query | 3mo C/I/CTR/Pos | 12mo C/I/CTR/Pos | Trend |
|---|---|---|---|
| e3 center | 47 / 136 / 34.6% / 2.94 | 118 / 306 / 38.6% / 3.6 | On-pace; rank improved |
| e3 group | 14 / 62 / 22.6% / 8.9 | 46 / 257 / 17.9% / 14.8 | **Rank improved 14.8 → 8.9**, CTR up |
| i-yun lisa hsieh | 7 / 78 / 9.0% / 5.12 | 28 / 285 / 9.8% / 3.5 | On-pace |
| e3 | 6 / 8,156 / 0.07% / 8.7 | 14 / 34,505 / 0.04% / 8.6 | Same noise; less of it |
| e3 lab | 6 / 43 / 14.0% / 6.07 | 25 / 93 / 26.9% / 5.9 | **CTR dropped 26.9→14.0** — investigate |
| 謝依芸 | 5 / 131 / 3.8% / 8.16 | 24 / 900 / 2.7% / 8.4 | CTR up |
| lisa hsieh | 4 / 54 / 7.4% / 4.98 | 12 / 220 / 5.5% / 4.3 | CTR up |
| 黃榆庭 | **2 / 15 / 13.3% / 10.07** | (not present in 12mo top queries) | **New name surfacing** |
| e3lab | 2 / 3 / 66.7% / 1.67 | 2 / 6 / 33.3% / 9.5 | Tiny volume, rank up |
| e3group | 2 / 2 / 100% / 1.5 | 7 / 13 / 53.8% / 7.0 | Same tiny tail |

The `e3 group` rank improvement (14.8 → 8.9) is the most concrete positive movement in the data. The `e3 lab` CTR drop deserves a closer look — same on-page content, but click-through halved.

### 4.2 Striking-distance opportunities (unchanged from 12mo)

These still rank on page 1 but earn zero or near-zero clicks. **None of the 12mo Tier-1 recommendations have shipped yet** — the same fixes still apply:

| Query | Pos | Impr | CTR | Status vs 12mo |
|---|---:|---:|---:|---|
| **i yun** | 3.14 | 56 | 0% | Unchanged — title/snippet still doesn't say "I-Yun Hsieh" |
| **謝依芸** | 8.16 | 131 | 3.8% | Slight CTR improvement; still room |
| **謝依芸 台大** | 10.65 | 17 | 0% | Unchanged — need "台大" / "NTU" co-occurrence |
| **拔萃學者** | 8.88 | 8 | 0% | Unchanged — award association weakly indexed |
| **caece.net** | 2.40 | 5 | 0% | Unchanged — domain-typed search, snippet not reassuring |

### 4.3 New name queries (this quarter)

Student-name queries that did not appear in the 12mo top-270:

| Query | Impr | Pos | Interpretation |
|---|---:|---:|---|
| 黃榆庭 | 15 | 10.07 | **Page indexed → ranks → 2 clicks.** Only student page Google indexed this quarter. |
| sean yun | 29 | 29 | Likely "Sean Shei" / "Sean Yun" conflation; site shown on page 3 only |
| 張友睿 | 4 | 8.5 | Page 1, but page not indexed → no click |
| 鍾安慶 | 4 | 10.75 | Page 1–2, page not indexed |
| 丁俊瑋 | 3 | 15 | Page 2 |
| 林宏叡 | 2 | 47 | Off page |
| chung-yun hsieh | 1 | 18 | Unusual — possibly typo for "I-Yun Hsieh" |
| 于忻 | 1 | 11 | Page 2 |
| thomas yuan | 1 | 6 | Page 1, no click |
| 陳珮慈 | 1 | 33 | Off page |

Pattern: Google has *some* awareness of the students (the homepage and members listing surface for their names), but the individual member subsubpages are not in the index, so click-through is starved.

### 4.4 Long-tail summary

Filtering out brand `e3` variants and PI/student names, the 3mo dataset contains **3 topical queries** with non-zero impressions: `renewable energy?` (1 impr, pos 2.0), `e3 economics` (1, pos 10), `national taiwan university (ntu)` (1, pos 1.0). **Combined topical-query clicks: 0.** This is identical in shape to the 12mo finding: zero topical SEO presence outside the brand bubble.

---

## 5. Page analysis

### 5.1 The 9 indexed URLs — same set, same problem

| URL | Clicks | Impr | CTR | Pos |
|---|---:|---:|---:|---:|
| `/` | **229** | 10,218 | 2.24% | 8.19 |
| `/news/` | 8 | 348 | 2.30% | 4.99 |
| `/members/yutinghuang/` | 3 | 36 | 8.33% | 11.17 |
| `/members/r11521604/` | **2** | 84 | 2.38% | 7.14 |
| `/members/yuanhsichien` (no slash) | 1 | 20 | 5.00% | 5.15 |
| `/members/yuanhsichien/` | 0 | 13 | 0% | 6.38 |
| `/members/yutinghuang` (no slash) | 0 | 8 | 0% | 6.12 |
| `/Solar-PV-on-Bus-Shelter/` | 0 | 8 | 0% | 6.75 |
| `/assets/images/e3-logo-text.svg` | 0 | 1 | 0% | 33 |

Homepage absorbs **95% of all clicks (229/242)**. After 12 months and one additional week, the indexed set is identical to the 12mo baseline. Sitemap is healthy (36 URLs in `docs/sitemap.xml`, all current members and news items included) — so submission is not the gating issue. Google has crawled and chosen not to index, or has not yet processed, 27 of 28 member pages and 4 of 5 news items.

### 5.2 Two stale URLs are siphoning real attention

Both `/members/r11521604/` (84 impr, 2 clicks) and `/Solar-PV-on-Bus-Shelter/` (8 impr) are **not present anywhere in the current site** — not in `contents/`, not in `docs/`, not in `git log`. They are 404s today. Google still has them cached and is sending users to dead pages. (Treatment deferred per discussion; flagged here for the record.)

### 5.3 Trailing-slash duplicates persist

| URL form | Impressions (3mo) | Impressions (12mo) |
|---|---:|---:|
| `/members/yuanhsichien` (no slash) | 20 | 11 |
| `/members/yuanhsichien/` (with slash) | 13 | 7 |
| `/members/yutinghuang` (no slash) | 8 | 3 |
| `/members/yutinghuang/` (with slash) | 36 | 15 |

Ranking signal is still being split across two URL forms for two members. Same fix recommended in the 12mo report.

---

## 6. Geography

| Country | Clicks | Impr | CTR | Pos |
|---|---:|---:|---:|---:|
| **Taiwan** | 196 (81%) | 9,287 (89%) | 2.11% | 8.27 |
| United States | 16 | 293 | **5.46%** | 8.57 |
| Japan | 6 | 54 | **11.11%** | 5.28 |
| Germany | 3 | 45 | 6.67% | 5.84 |
| India | 2 | 74 | 2.70% | 10.3 |
| Indonesia | 2 | 25 | 8.00% | 5.24 |
| United Kingdom | 2 | 20 | **10.00%** | 5.1 |
| Netherlands | 2 | 13 | **15.38%** | 9.31 |
| New Zealand | 2 | 8 | **25.00%** | 7.25 |
| Belgium | 2 | 5 | **40.00%** | 4.4 |

Pattern is unchanged from 12mo: Taiwan-dominant, international tail uniformly higher-CTR. New entries this quarter (Belgium, New Zealand, Czechia, Poland) all converted on tiny volumes — these are intent-matched lookups (collaboration / due-diligence) not ambient searches.

**Vietnam outlier:** 0 clicks on 61 impressions at pos 6.1. Page-1 rank, zero CTR — same snippet-quality story as the Taiwan `i yun` problem, in Vietnamese audience form.

---

## 7. Devices

| Device | Clicks | Impr | CTR | Position |
|---|---:|---:|---:|---:|
| Desktop | 159 (66%) | 5,591 (53%) | **2.84%** | 7.85 |
| Mobile | 78 (32%) | 4,280 (41%) | 1.82% | 8.55 |
| Tablet | 5 (2%) | 584 (6%) | 0.86% | 8.97 |

Desktop CTR has improved from 2.10% (12mo) to 2.84%. Mobile from 1.58% to 1.82%. Tablet from 0.24% to 0.86%. All three trending up. Desktop still converts ~55% better than mobile at near-equal positions, consistent with the academic / research-due-diligence audience.

---

## 8. Search appearance

| Type | Clicks | Impr | CTR | Pos |
|---|---:|---:|---:|---:|
| Translated results | 0 | 29 | 0% | 7.94 |

Identical pattern to 12mo: Google auto-translation surfaces the site to non-English speakers, none click. The recent BreadcrumbList + Person JSON-LD on member pages has not yet generated any rich-result appearances. Allow more time, or consider Article schema on news items to broaden eligibility.

---

## 9. The 薛丞翔 vs 黃榆庭 question (diagnosis)

The reader question — *"Why does 黃榆庭 surface in search but 薛丞翔 does not, even though both are on the site?"* — has a clean answer in the data.

### 9.1 On-page content is not the problem

Both pages are well-tagged. In fact, 薛丞翔's page is *more* heavily indexed signal-wise than 黃榆庭's:

| Signal | `/members/chenghsiangshei/` | `/members/yutinghuang/` |
|---|---|---|
| `<title>` contains Chinese name | ✅ `Cheng-Hsiang Shei (Sean) 薛丞翔 \| E3 Center, NTU` | ✅ `Yu-Ting Huang 黃榆庭 \| E3 Center, NTU` |
| `<meta description>` contains Chinese name | ✅ but truncated mid-sentence (see §10.1) | ✅ but uses weakest fallback (see §10.2) |
| Chinese name occurrences in body HTML | **19** | 14 |
| Mention on homepage | **2** | 0 |
| Mention on `/members/` listing | **4** | 2 |
| In sitemap | ✅ | ✅ |
| In Google's index (per GSC Pages report) | **❌** (0 impr in 12mo + 3mo) | ✅ (15 impr in 3mo, 18 in 12mo) |

### 9.2 It is an indexing problem, not a content problem

`/members/yutinghuang/` is one of the 9 URLs Google has indexed in 12+ months. `/members/chenghsiangshei/` is one of the 27 that are sitemapped and discoverable but not in the index. Once a page is indexed, a unique-enough name query like 黃榆庭 (which collides with very few people outside this lab) will surface it at a low rank for free; until a page is indexed, it cannot surface for any query, no matter how well-tagged.

Why this particular split:
- **黃榆庭** was added relatively recently (admission year `'25`) but Google happened to crawl + index her page, likely helped by the trailing-slash duplicate behavior (both `/yutinghuang/` and `/yutinghuang` got crawled, doubling discovery chances).
- **薛丞翔** is `graduated: true` in his JSON — graduated-member pages typically receive fewer internal links over time (e.g., they may be moved out of the "current" listings) and fewer external link signals (no recent paper bylines pointing at the lab page), making them harder for Google to justify indexing.
- The graduated/current distinction shows up in `members.json` — worth verifying whether graduated members are still linked from a primary `/members/` view or only from a "Former members" section deeper in the hierarchy.

### 9.3 Recommended action for this specific case

1. Open Search Console → URL Inspection → `https://e3center.caece.net/members/chenghsiangshei/`.
2. Read the status:
   - "URL is not on Google" + "Discovered – currently not indexed" → click **Request indexing**.
   - "Crawled – currently not indexed" → Google has seen it and rejected it. This indicates either thin content (Sean's page has a short About + truncated description) or insufficient external/internal signals. Strengthen the page first (§10), then re-request.
3. Do the same for the other 25 unindexed member pages, prioritized by relative importance (PI > active senior students > recent students > graduated members).
4. After requesting indexing, allow 1–4 weeks before re-checking.

---

## 10. Meta-tag audit (incidental findings)

While diagnosing §9, two meta-description bugs surfaced in `templates/pages/member/member.html` that affect every member page, not just 薛丞翔. Worth fixing regardless of indexing status — they are independent improvements.

### 10.1 Bug A: fallback A descriptions can truncate mid-sentence and contain doubled periods

Template construction (member.html:23–28):
```jinja2
{% set _role = member.get('position') or 'researcher at E3 Center, NTU' %}
{% set _name_prefix = _bilingual_name ~ ', ' ~ _role %}
{% set _auto_desc_a = (_name_prefix ~ '. Research interests: ' ~ _interest) if _interest else '' %}
```

Two issues:

1. **Doubled period.** When `position` already ends in `.` (e.g. `"Research Assistant, E3 Research Center, National Taiwan University."`), the template appends another `.` before `Research interests:`, producing `…University.. Research interests: …`.
2. **No length bound.** `_interest` is the stripped HTML of the entire interest article. If the interest text exceeds the SERP cap (~160 chars), the description in the rendered HTML is the full long string; Google's SERP then truncates it visually, often mid-word. For Sean it ends `…Distributional Impacts of Climate and` — clearly a hard cut, not a sentence boundary.

The actual length capping (and presumably ellipsis handling) lives in `seo_helpers.generate_meta_description`. Worth auditing that function for: (a) sentence-aware truncation, (b) punctuation cleanup before composition.

### 10.2 Bug B: fallback C is generic and likely produces duplicates

```jinja2
{% set _auto_desc_c = _bilingual_name ~ ' — member of E3 Center, National Taiwan University.' %}
```

Any member who has no `interest_content` and no `aboutSection` lands on this. 黃榆庭 is one example. So is anyone in the lab without a research-interests article yet — likely most current students. `build.py:validate_seo` already detects duplicate-description across pages and warns; this fallback shape is the most likely producer of those warnings.

Suggested fallback C improvement (one of several options to discuss):
> `{name} — {position truncated to first line} at E3 Center, NTU. {admission-year context if available}.`

This injects per-member variation from data we already have without needing new content per member.

### 10.3 Other meta-tag observations

- **`<title>` length** is fine for member pages — `"Yu-Ting Huang 黃榆庭 | E3 Center, NTU"` is 39 chars, well within the 60-char SERP cap.
- **`<meta name="author">`** is set to `member['engName']` — for some members `engName` is a nickname (e.g. `"Sean"`, `"YuTing"`) rather than the full English name. The HTML `<meta name="author">` Google does not weight heavily, but for consistency consider `chiNameEng` (which is `"Cheng-Hsiang Shei (Sean)"`).
- **Homepage title remains `E3 Center | National Taiwan University`** — does not include `I-Yun Hsieh` or `謝依芸`. The 12mo report's Tier-1 #3 recommendation to rewrite this has not shipped. This is the single highest-leverage SERP-snippet fix.

---

## 11. Recommendations (delta from 12mo)

Aligned with the 12mo Tier-1/2/3 structure. Marked **[carry-over]** if the 12mo recommendation still applies unchanged, **[new]** if surfaced by this report.

### Tier 1 — biggest impact, mostly known

1. **[carry-over]** Fix indexing breadth. Top action: URL Inspection → Request Indexing for the top ~10 member pages, starting with `/members/chenghsiangshei/` (per §9.3) and `/members/iyunlisahsieh/`. **None of the 12mo Tier-1 actions have shipped yet.**
2. **[carry-over]** Resolve trailing-slash duplicates for `yuanhsichien` and `yutinghuang`.
3. **[carry-over]** Rewrite homepage `<title>` and meta description to include `I-Yun Hsieh` / `謝依芸` / `台大` / `NTU` — this single change should move `i yun` (pos 3.14, 0% CTR) and `謝依芸` (pos 8.16, 3.8% CTR) significantly.

### Tier 2 — surfaced by this report

4. **[new]** Patch `templates/pages/member/member.html` meta-description composition:
    - Collapse doubled periods between `_role` and `Research interests:`.
    - Audit `seo_helpers.generate_meta_description` for sentence-aware truncation at the SERP cap.
    - Enrich fallback C with `position` and/or admission year so it varies per member.
5. **[new]** Audit `<meta name="author">` — consider switching from `engName` (often a nickname) to `chiNameEng` (full bilingual name) for stable per-member attribution. Low priority; cosmetic.
6. **[carry-over]** Build topical landing pages (`/research/<topic>/`) to escape brand-only ranking. Still zero topical queries in the data.

### Tier 3 — longer horizon

7. **[carry-over]** Bilingual / hreflang setup. Translated-results impressions (29) still convert at 0%. The Vietnamese audience (61 impr at pos 6.1, 0 clicks) shows the same pattern in a fourth language.
8. **[carry-over]** Article / FAQ JSON-LD on news items to widen rich-result eligibility.
9. **[new]** Investigate **2026-05-05** (17 clicks, 7.49% CTR — single-day record). If it correlates with a public-facing event or news item, document the cause; that's a replicable playbook.
10. **[new]** Investigate **`e3 lab` CTR halving** (26.9% → 14.0%, same position range). Possibly snippet drift after recent template changes; worth confirming.
11. **[carry-over]** Re-export quarterly. Next checkpoint: ~2026-08-13 (12mo) and ~2026-08-13 (3mo).

---

## 12. Reading these numbers in the future

Same interpretive rules as the 12mo report apply. One addition specific to this delta:

- **Don't expect 3mo deltas to swing wildly on the indexed-URL set.** Google's choice of which URLs to index is sticky — it changes on the scale of months-to-quarters, not weeks. The "9 URLs" headline number from 12mo will probably remain similar in the next 3mo export unless concrete actions ship (request-indexing, internal-link improvements, page-quality strengthening). If it does move significantly, that's strong evidence that whatever shipped worked.
