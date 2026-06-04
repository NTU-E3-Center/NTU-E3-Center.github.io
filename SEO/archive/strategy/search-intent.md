> ⚠️ **SUPERSEDED (2026-06-03).** This document has been superseded by [`../../seo-report.html`](../../seo-report.html), the current SEO deliverable (a single self-contained HTML dashboard). It is retained here for historical reference only; its prose rationale still holds, but the up-to-date analysis, current data, and prioritized action plan now live in the HTML report.

---

# Search Intent Strategy for E3 Center

**Audience focus:** (1) researchers / industry / government looking for collaborators, (2) people interested in the field who don't yet know your lab.
**Companion to:** [`../analysis/2026-05-06_12mo-insights.md`](../analysis/2026-05-06_12mo-insights.md) (12-month GSC analysis).

---

## 1. What "search intent" actually means

When someone types a query into Google, they want one of four things. Google has gotten very good at guessing which, and it ranks pages that match the *intent* — not just pages that contain the keywords.

| Intent | What the user wants | Mental state |
|---|---|---|
| **Navigational** | A specific site they already know | "I know E3 Center exists, take me there." |
| **Informational** | To learn about a topic | "How does building-integrated PV work?" |
| **Investigative** *(a.k.a. commercial/comparative)* | To compare or evaluate options | "Who in Taiwan researches EV charging policy?" |
| **Transactional** | To do something concrete | "Apply for PhD at NTU civil engineering." |

A page that's perfect for one intent will fail at the others. A homepage that says "Welcome to E3 Center" satisfies *navigational* intent perfectly and *informational* intent not at all — which is exactly what your current GSC data shows.

### Your two stated audiences mapped to intent

| Audience | Where they are in their journey | Dominant intent | Secondary |
|---|---|---|---|
| **Collaborators** (faculty, industry, government, NGOs) | They have a problem in *their* world; want to find a lab with matching expertise. | **Investigative** ("who works on X in Taiwan?") | Informational (background reading), then navigational once they know your name. |
| **Field-interested people** (journalists, students elsewhere, policymakers, curious public) | They have a topic in mind; don't know who works on it. | **Informational** ("what is being done about X?") | Investigative (after reading, "is this lab credible?"). |

Both audiences enter via **non-brand topical queries**. Your GSC data shows you currently capture **zero** of these. Every click in the past 12 months came from someone who already knew the name "E3", a member's name, or the domain.

This is the core of the strategy: you need to start ranking for *what you study*, not just *who you are*.

---

## 2. Where you stand today (intent breakdown of last 12 months)

Categorizing your 270 ranked queries by intent:

| Intent class | Queries | Clicks | Impressions | CTR |
|---|---:|---:|---:|---:|
| Navigational — brand (`e3 center`, `e3 group`, `e3 lab`, …) | 18 | **200** | 897 | 22.3% |
| Navigational — names (PI + students) | 24 | 68 | 1,803 | 3.8% |
| Noise — bare/punctuated `e3` (gaming expo) | 7 | 14 | 34,604 | 0.04% |
| Informational / Investigative — topical | **0** | 0 | 0 | — |
| Other long-tail (typos, partial brand, conference IDs) | 221 | 1 | 363 | 0.28% |

**Reading this:** when an intent-bearing user types something like "transportation electrification research Taiwan" or "建築光電 研究", you do not appear in their results at all. The funnel above brand search is empty.

A successful 12-month state would look more like:

| Intent class | Target queries | Target impressions/yr |
|---|---|---:|
| Navigational | (already won) | maintain |
| **Informational — research topics** | "building-integrated photovoltaics taiwan", "ev grid integration", "公共運輸電動化", … | **5,000+** |
| **Investigative — collaboration discovery** | "ntu energy systems lab", "taiwan transportation research group", "energy policy researcher taiwan", … | **2,000+** |
| Transactional — recruiting | "ntu civil engineering phd", "i-yun hsieh phd application", … | **300+** |

You don't need to displace incumbents on broad terms. Long-tail topical queries (4+ words, often bilingual, often place-specific) are where academic labs win.

---

## 3. Content patterns by intent

For each intent type, there is a page archetype that ranks for it. Map these to your existing site structure.

### 3.1 Investigative intent → "Who does this?" pages

**Audience:** Collaborators trying to identify the right lab.
**Their query shape:** `[topic] + [region/institution] + [expert/lab/researcher]`

Examples:
- `transportation electrification research taiwan`
- `building energy efficiency lab ntu`
- `碳中和 研究團隊 台灣`
- `solar PV grid integration researcher asia`
- `circular economy professor taiwan`

**Page archetype that wins:** A *research areas* / *topics* hub page, plus one dedicated subpage per topic. Each topic page should answer:

1. **What is this topic, in 2–3 sentences** (informational anchor — gives Google a topical signal).
2. **What this lab specifically does in this area** — a paragraph naming methods, datasets, partnerships, locations.
3. **Who works on it** — links to the relevant member subpages with one-line descriptions of their angle.
4. **Recent publications** in this area — auto-populated from your existing publications JSON, filtered by topic tag.
5. **Recent news** in this area — auto-populated from your news JSON, filtered the same way.
6. **How to collaborate / contact** — a section addressing what a prospective collaborator should do next (email PI, attend a seminar, etc.).

This single page archetype satisfies investigative intent at the moment of decision: the user can see the topic is real, the people are credible, the work is recent, and the path to engagement is obvious.

**On your site today:** `contents/articles/about.md` and the `/research/` page structure are the natural homes for this. Each major research theme should get its own `/research/{topic-slug}/` URL, not just a section heading on a single scrolling page. **One URL per topic** is the SEO unit of currency — a section anchor (`#topic`) cannot rank independently.

### 3.2 Informational intent → "What is X?" pages

**Audience:** Field-interested visitors, students from elsewhere, journalists, policymakers preparing for meetings.
**Their query shape:** `what is [topic]`, `[topic] explained`, `[topic] in [region]`, `how does [topic] work`

Examples:
- `transportation electrification taiwan policy`
- `building integrated photovoltaics explained`
- `decarbonization pathways taiwan 2050`
- `light-duty vehicle electrification challenges`
- `太陽能板 建築一體化`

**Page archetype that wins:** Long-form explainer or annotated news/insight posts. Either:

- **News items as topic primers.** A news post titled "E3 Center contributes to Taiwan's 2050 net-zero pathway report" can rank for `taiwan net-zero pathway` if it has 600–1200 words of plain-language summary. Your `/news/` infrastructure already supports this.
- **A dedicated "Insights" or "Explainer" section.** Short, accessible articles authored by lab members on what their research means in plain language. These are also great recruiting/citation magnets.

**On your site today:** News items are the obvious vehicle. Two changes will make them rank:

1. Stop writing news bodies that assume the reader knows the context. Each news item should open with 2–3 sentences explaining the topic for someone who doesn't know what `BIPV` or `LCA` stands for.
2. Use descriptive titles. `"Lab attends APEC Energy Working Group"` is invisible to anyone who isn't already searching for "APEC Energy Working Group". `"E3 Center presents Taiwan transportation electrification roadmap at APEC Energy Working Group"` ranks for the topical query *and* the navigational query.

### 3.3 Transactional intent → "Join / apply / contact" pages

**Audience:** Prospective grad students, postdocs, undergrads seeking research projects.
**Their query shape:** `apply phd [field] [institution]`, `join [lab name]`, `[professor] phd students`

Examples:
- `ntu civil engineering phd application`
- `i-yun hsieh phd students`
- `join e3 center`
- `ntu environmental engineering postdoc`
- `e3 lab recruiting`

**Page archetype that wins:** A `/join/` or `/recruiting/` page that explicitly lists:

- Open positions (or "currently full" if not, with dates).
- What kind of student/postdoc the lab is looking for.
- Application process and contact form/email.
- FAQ for prospective applicants.

This is the single highest-leverage page for converting *navigational* traffic into actual collaborations or applications, and it ranks well even with low link equity because intent is so specific.

### 3.4 Navigational intent → titles and snippets

**Audience:** People who already know the name (met at a conference, saw a paper, were referred).
**Their query shape:** the exact name, in any of 5+ romanizations and variants.

This is the intent you already win on volume, but lose on snippet quality:

- `i yun` — pos 3.4, **0 clicks** — Google ranks you, the user doesn't recognize the snippet.
- `caece.net` — pos 8.6, **0 clicks** — domain-typed but the snippet doesn't reassure.
- `謝依芸 台大` — 95 impressions, **0 clicks** — name + institution but snippet doesn't include both.

**Fix:** rewrite `<title>` and meta description on the homepage and PI subpage so that someone glancing at the SERP for *any* of these queries instantly sees "Yes, this is the lab I was looking for." Aim for the format:

```
<title>E3 Center · Energy, Environment & Equity Group · Prof. I-Yun Lisa Hsieh · NTU 國立臺灣大學</title>
```

Verbose, yes. But it carries every navigational query variant in the SERP, including the bilingual ones.

---

## 4. Bilingual intent (the often-overlooked half)

Roughly 80% of your audience is in Taiwan, and your queries split between English and Chinese:

- **English brand:** `e3 center`, `e3 group`, `i-yun lisa hsieh`, `lisa hsieh`
- **Chinese name:** `謝依芸`, `謝依芸 台大`, `呂芷儀`, `蔡家妤`, `丁俊瑋`, `黃榆庭`, `張友睿`, `鍾安慶`
- **Chinese topical (currently absent):** what your domestic collaborators *would* search but currently can't find you for.

For each major research theme, you should target the *bilingual pair*:

| English topic query | Chinese topic query |
|---|---|
| transportation electrification taiwan | 公共運輸電動化 / 交通運輸電動化 |
| building energy efficiency | 建築節能 / 建築能源效率 |
| solar PV building integration | 建築一體化太陽能 / BIPV |
| net-zero pathways taiwan | 淨零路徑 / 2050 淨零 |
| ev grid integration | 電動車併網 |
| circular economy buildings | 循環經濟 建築 |

A research-topic page that includes both the English term and the Chinese term in its body and metadata will rank for both. **`hreflang` annotations** in your `<head>` (e.g. `hreflang="en"` and `hreflang="zh-TW"`) tell Google which version to surface to which audience, but a single page with both languages also works for academic content where readers expect bilingual material.

> Your current `templates/base.html` includes a `lang` attribute. Verify it's set per-page based on content language, not hard-coded to one value, and add `hreflang` link tags for any page with EN/中 variants.

---

## 5. The intent-aware page checklist

Before publishing a new page, ask: **what intent does this serve?** If you can't answer in one word from the table at the top, the page won't rank — because Google can't decide either.

For each new research-topic, news, or member page:

- [ ] **Intent identified.** Investigative? Informational? Transactional? Navigational?
- [ ] **Title matches intent.** A topic page titled "Our lab's work on X" loses to a competitor titled "X research at NTU" because the second matches investigative intent more cleanly.
- [ ] **First paragraph confirms the match.** Within 2–3 sentences, the user knows they're in the right place. No "Welcome to our page" preambles.
- [ ] **One primary keyword cluster.** Don't try to rank one page for 5 unrelated queries. Each page targets one intent and one keyword cluster.
- [ ] **Bilingual where the audience is bilingual.** Especially for topic pages where Taiwanese collaborators search in Chinese.
- [ ] **Internal links from related content.** A topic page linked from member subpages, publications, and news items will rank far faster than an orphan.
- [ ] **Concrete next step.** What should the user do after reading? Contact PI? Read a publication? Apply? Make it explicit.

---

## 6. Specific recommendations for E3 Center

Tied to your current site structure and the data in the GSC report:

### Quick wins (1–2 weeks)

1. **Rewrite homepage and PI page `<title>` + `<meta description>`** to include `E3 Center`, `Energy, Environment & Equity`, `Prof. I-Yun Lisa Hsieh / 謝依芸`, `NTU / 國立臺灣大學`, and 1–2 anchor research keywords. Recovers the 154+ "i yun" zero-click impressions.

2. **Pick canonical URL form for member pages** (with vs. without trailing slash). Stop splitting signal across two URLs.

3. **Audit `templates/pages/news/news-item.html` titles** — current pattern likely produces titles too generic to rank for topical queries. Update to `[Topic-keyword] — [Action] — E3 Center` format.

### Medium-term (1–2 months)

4. **Build a `/research/{topic-slug}/` page for each of your 3–5 major themes.** Each one is a hub for investigative intent (collaborators looking for "who does this?"). Use the page archetype in §3.1.

5. **Convert each news item into a topical primer.** Add 2–3 sentences of plain-language context at the top. Add the bilingual term pair somewhere in the body.

6. **Add a `/join/` page** for transactional intent. Even if you're not actively recruiting, having the page captures the intent and tells visitors when to come back.

### Ongoing

7. **For every new member,** their subpage should include their research focus stated in *both* the English and Chinese terms a collaborator might search. Currently your member pages emphasize bio/CV; for SEO they also need to emphasize *topics they work on* in plain language.

8. **For every new publication,** ensure it links to the topic page(s) it belongs to (and vice versa). A publication on building-integrated PV should appear on `/research/bipv/` automatically.

9. **Track these metrics quarterly** (re-export GSC):
    - Number of distinct queries with **non-brand intent** (target: from 0 → 50+ in 6 months).
    - Number of distinct URLs receiving impressions (target: from 9 → 40+ in 6 months).
    - Average position on a small basket of target topical queries (e.g. `building integrated photovoltaics taiwan`, `transportation electrification ntu`).

---

## 7. Why this works for academic labs specifically

A few principles that academic-lab websites underuse:

- **You don't need link-building or paid ads.** Long-tail topical queries (4+ words, region-specific) have low competition. A well-structured page with genuine substance ranks for them within weeks.
- **Your existing publications and news are a content moat.** Most lab sites bury this material; structuring it around topics multiplies its SEO value with zero new writing.
- **Bilingual is a competitive advantage.** Most international lab sites only publish in English. Bilingual EN/中 pages capture two audiences with the same content.
- **Recency signals matter less than authority signals.** Google trusts a page on `ntu.edu.tw` (or `caece.net`) on energy research more than a Medium post, *if* the page is structured to make that authority legible — clear topic, named experts, citations, institutional context.
- **The student/postdoc recruiting funnel is a free SEO benefit.** Every prospective applicant who Googles you and finds a clear `/join/` page is a soft conversion. Even if 95% don't apply, the 5% who do are higher-fit because they self-selected on real information.

---

## 8. Further reading

If you want to go deeper:

- Google's own *Search Quality Rater Guidelines* (PDF, freely available) — the definitive source on how Google evaluates intent match. Skim sections on "Needs Met" rating.
- Ahrefs / Semrush blog posts on **"informational vs. investigative vs. transactional intent"** (free articles, ignore the tool pitches).
- For academic-lab-specific examples, study the sites of **MIT Energy Initiative**, **Stanford Doerr School of Sustainability**, and **NTU's own ESS / RSEA labs** — note how they structure topic pages, member pages, and news.

Search intent is not a trick. It's the discipline of writing each page for one specific user, in one specific moment of their journey, and trusting that Google's job is to figure out which page fits which moment. Do that consistently across 20–30 pages and the topical traffic will compound on its own.
