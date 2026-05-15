# SEO — E3 Center

Working folder for SEO research, analysis, strategy, and implementation planning for **e3center.caece.net**.

## Folder layout

```
SEO/
├── README.md                 ← this file
├── RUNBOOK.md                operator runbook (GSC, indexing, build SEO warnings)
├── data/                     raw Google Search Console exports
├── analysis/                 dated reports derived from data/
├── strategy/                 evergreen reference material (concepts)
└── recommendations/          actionable plans for the site
```

| Folder / file | What goes here | When it changes |
|---|---|---|
| `RUNBOOK.md` | Operator-facing how-to: verifying URL property, submitting sitemap, requesting indexing for new pages, interpreting SEO build warnings, manual deindex. | When ops procedures change. |
| `data/` | Raw GSC exports (`.xlsx`). Filename pattern: `gsc_{export-date}_{period}.xlsx`. | Every new GSC export. |
| `analysis/` | Reports that interpret a specific data export. Filename pattern: `{date}_{period}-insights.md`. | Once per data export. |
| `strategy/` | Conceptual reference docs that explain *how SEO works* for an academic lab. | Rarely — only when the underlying ideas change. |
| `recommendations/` | Concrete, file-specific advice for what to ship on the site. | When site state or priorities shift materially. |

---

## Reading order

If you're new to this folder, read in this order:

1. **[`analysis/2026-05-06_12mo-insights.md`](analysis/2026-05-06_12mo-insights.md)** — what the 12-month GSC data actually says about the site's search performance.
2. **[`strategy/search-intent.md`](strategy/search-intent.md)** — the conceptual frame: what search intent is, and which intents the lab needs to win for its target audiences.
3. **[`strategy/backlinks.md`](strategy/backlinks.md)** — how backlinks work, and which links a lab like E3 should be pursuing.
4. **[`recommendations/page-recommendations.md`](recommendations/page-recommendations.md)** — the concrete, phased plan: what to edit, what to build, in what order.
5. **[`recommendations/content-ideas.md`](recommendations/content-ideas.md)** — a catalogue of content topics and formats organized by audience and effort.

The strategy docs (2, 3) are reference; the analysis (1) is the diagnosis; the recommendations (4, 5) are the prescription.

---

## Files in this folder

### `data/`

| File | Period | Source |
|---|---|---|
| [`gsc_2026-05-06_12mo.xlsx`](data/gsc_2026-05-06_12mo.xlsx) | 2025-05-04 → 2026-05-03 (last 12 months) | Google Search Console "Performance on Search" export |
| [`gsc_2026-05-06_3mo.xlsx`](data/gsc_2026-05-06_3mo.xlsx) | 2026-02-04 → 2026-05-03 (last 3 months) | Google Search Console "Performance on Search" export |

### `analysis/`

| File | Covers |
|---|---|
| [`2026-05-06_12mo-insights.md`](analysis/2026-05-06_12mo-insights.md) | Full interpretation of the 12-month GSC export — query/intent breakdown, page indexing gap, geography, devices, and prioritized recommendations. |

### `strategy/`

| File | Covers |
|---|---|
| [`search-intent.md`](strategy/search-intent.md) | The four canonical intent types (navigational, informational, investigative, transactional), how they map to E3's two primary audiences, page archetypes per intent, bilingual considerations. |
| [`backlinks.md`](strategy/backlinks.md) | What backlinks do, quality factors, the subdomain situation, where free links are sitting on the table for E3 (institutional, funder, scholarly profile, conference, press), what *not* to do. |

### `recommendations/`

| File | Covers |
|---|---|
| [`page-recommendations.md`](recommendations/page-recommendations.md) | Phased, file-by-file action plan: same-day template/title rewrites, new `/join/` and `/collaborate/` pages, news-pattern changes, publications-page activation, member-page emphasis shifts, future research-subpage design constraints. |
| [`content-ideas.md`](recommendations/content-ideas.md) | A catalogue of content topics and formats, tagged by audience (`[collab]` `[apply]` `[public]` `[brand]`), vehicle (existing vs. new template), and effort (🟢🟡🔴). Includes a 12-week pilot content plan. |

---

## Adding a new GSC export

When you pull a fresh Performance-on-Search report from Google Search Console:

1. Save the `.xlsx` into `data/` with the filename pattern `gsc_{YYYY-MM-DD}_{period}.xlsx`. Use the *export date* (today) and the *period covered* (e.g. `12mo`, `3mo`, `28d`).
2. If the new export warrants a fresh analysis, write a new file in `analysis/` named `{YYYY-MM-DD}_{period}-insights.md` — don't overwrite the older one. Old analyses are useful as historical baselines.
3. Skim the strategy and recommendations docs to see if anything in them is contradicted by the new data; update if so, otherwise leave them alone.

---

## Conventions

- **Dates in filenames are ISO format** (`YYYY-MM-DD`) so files sort chronologically by name.
- **Markdown cross-references use relative paths** (`../analysis/...`, `./other-file.md`) — they survive folder moves and render correctly on GitHub.
- **Strategy docs stay evergreen.** Resist the urge to fold concrete observations from new data into them; that belongs in `analysis/` or `recommendations/`.
- **Recommendations are versioned by being dated in the body**, not in the filename. When the plan changes substantially, update the doc and add a "Last updated" line at the top.
