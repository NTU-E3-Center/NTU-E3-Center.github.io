# SEO — E3 Center

Working folder for SEO research, analysis, strategy, and recommendations for **e3center.caece.net**.

## ⭐ Start here: [`seo-report.html`](seo-report.html)

The current deliverable is **[`seo-report.html`](seo-report.html)** — a single self-contained
HTML dashboard (open it by double-clicking; no server or dependencies needed). It contains the
up-to-date diagnosis, a prioritised **next-action plan**, page-by-page strategy, a GSC-vs-Google-Analytics
guide, and the answer to "what data do you need next". **It supersedes the old strategy and
recommendation markdown docs** (now archived — see below).

## Folder layout

```
SEO/
├── README.md                 ← this file
├── seo-report.html           ⭐ PRIMARY — the current SEO report & action plan (HTML dashboard)
├── RUNBOOK.md                operator runbook (GSC, indexing, build SEO warnings)
├── data/                     raw exports — GSC (gsc_*) and GA4 (ga4_*)
├── analysis/                 dated reports derived from data/ (historical baselines)
└── archive/                  superseded markdown docs, kept for reference
    ├── strategy/             ← (was SEO/strategy/) search-intent.md, backlinks.md
    └── recommendations/      ← (was SEO/recommendations/) page-recommendations.md, content-ideas.md
```

| Folder / file | What goes here | When it changes |
|---|---|---|
| `seo-report.html` | The current, readable deliverable: diagnosis, action plan, per-page strategy, analytics guide. | When a new GSC export or material site change warrants a refresh. |
| `RUNBOOK.md` | Operator how-to: verifying the URL property, submitting the sitemap, requesting indexing, interpreting build SEO warnings. | When ops procedures change. |
| `data/` | Raw GSC exports (`.xlsx` or the unzipped CSVs). Filename pattern: `gsc_{export-date}_{period}.*`. | Every new GSC export. |
| `analysis/` | Dated markdown reports interpreting a specific export. Retained as historical baselines. | Once per data export worth a written analysis. |
| `archive/` | The previous markdown strategy + recommendations docs, each with a "superseded" banner. Their prose rationale still holds; the live plan is now in the HTML report. | Rarely — reference only. |

---

## Reading order

1. **[`seo-report.html`](seo-report.html)** — everything actionable, current as of the latest export. Read this first.
2. **[`analysis/2026-05-06_12mo-insights.md`](analysis/2026-05-06_12mo-insights.md)** — the original deep
   12-month data interpretation, useful as a historical baseline of where the site started.
3. **`archive/strategy/`** and **`archive/recommendations/`** — the original conceptual write-ups
   (search intent, backlinks, page-by-page plan, content ideas). Superseded by the HTML report but still a
   good deep reference for the *why* behind each recommendation.

---

## Files in this folder

### `data/`

**GSC = Search Console (how you're found). GA4 = Analytics (what people do after the click).**

| File | Period | Source |
|---|---|---|
| [`gsc_2026-06-03_12mo/`](data/gsc_2026-06-03_12mo/) + [`.zip`](data/gsc_2026-06-03_12mo.zip) | 2025-06-02 → 2026-06-01 (last 12 months) | GSC "Performance on Search" — **latest; 12-mo zoom-out in the report** |
| [`gsc_2026-05-31_3mo/`](data/gsc_2026-05-31_3mo/) + [`.zip`](data/gsc_2026-05-31_3mo.zip) | 2026-03-01 → 2026-05-31 (last 3 months) | GSC "Performance on Search" — **primary 3-mo basis of the current report** |
| [`ga4_2026-06-02_organic-landing-pages.csv`](data/ga4_2026-06-02_organic-landing-pages.csv) | 2026-03-05 → 2026-06-02 | GA4 — organic search clicks/impr **joined with** per-page engagement (users, engaged sessions, time, events) |
| [`ga4_2026-06-02_audience-overview.csv`](data/ga4_2026-06-02_audience-overview.csv) | 2026-03-05 → 2026-06-02 | GA4 — acquisition channels, weekly users, country, OS/device/browser, organic queries |
| [`gsc_2026-05-06_12mo.xlsx`](data/gsc_2026-05-06_12mo.xlsx) | 2025-05-04 → 2026-05-03 (last 12 months) | GSC "Performance on Search" export (prior baseline) |
| [`gsc_2026-05-06_3mo.xlsx`](data/gsc_2026-05-06_3mo.xlsx) | 2026-02-04 → 2026-05-03 (last 3 months) | GSC "Performance on Search" export (prior baseline) |

### `analysis/`

| File | Covers |
|---|---|
| [`2026-05-06_12mo-insights.md`](analysis/2026-05-06_12mo-insights.md) | Full interpretation of the 12-month export — query/intent breakdown, indexing gap, geography, devices. Historical baseline. |

### `archive/` (superseded — reference only)

| File | Covers |
|---|---|
| [`archive/strategy/search-intent.md`](archive/strategy/search-intent.md) | The four intent types and how they map to E3's audiences and page archetypes. |
| [`archive/strategy/backlinks.md`](archive/strategy/backlinks.md) | How backlinks work and the venue-by-venue recovery checklist (still the reference for Action 13). |
| [`archive/recommendations/page-recommendations.md`](archive/recommendations/page-recommendations.md) | The original phased, file-by-file action plan (now reconciled into the HTML report). |
| [`archive/recommendations/content-ideas.md`](archive/recommendations/content-ideas.md) | Catalogue of content topics/formats by audience and effort. |

---

## Adding a new GSC export

When you pull a fresh Performance-on-Search report from Google Search Console:

1. Save the export into `data/` with the filename pattern `gsc_{YYYY-MM-DD}_{period}.*` — use the *export date*
   (today) and the *period covered* (e.g. `12mo`, `3mo`, `28d`). If it's a zip of CSVs (Chinese UI), keep the
   zip and also unzip into a same-named folder with English CSV names (see `gsc_2026-05-31_3mo/`).
2. Refresh **[`seo-report.html`](seo-report.html)** against the new numbers (or ask Claude to). The report's
   footer notes which export it was generated from.

   For **GA4 exports**, use the pattern `ga4_{YYYY-MM-DD}_{description}.csv` (e.g.
   `ga4_2026-06-02_audience-overview.csv`). GA4 answers what visitors *do* after the click — acquisition channels,
   engagement, conversions — which GSC can't see.
3. If the export warrants a full written deep-dive, add a dated file in `analysis/` named
   `{YYYY-MM-DD}_{period}-insights.md` — don't overwrite older ones; they're useful baselines.

---

## Conventions

- **Dates in filenames are ISO format** (`YYYY-MM-DD`) so files sort chronologically by name.
- **The HTML report is the source of truth** for the current plan. The archived markdown is reference only —
  don't edit it to reflect new data; update the HTML instead.
- **`analysis/` stays dated and append-only.** Old analyses are historical baselines, not living documents.
