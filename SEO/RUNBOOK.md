# SEO Runbook — E3 Center website

Operator-facing notes for keeping the site discoverable in Google.

## One-time setup (already done — documented for future maintainers)

1. **Verify URL-prefix property** in [Google Search Console](https://search.google.com/search-console)
   for `https://e3center.caece.net/`. Verification uses the
   `<meta name="google-site-verification" content="…">` tag in `templates/base.html`.
2. **Submit the sitemap** in GSC → *Sitemaps*: `https://e3center.caece.net/sitemap.xml`.
3. **Link Google Analytics property** `G-JCJPED8JS6` to the GSC property (Admin → Associations).

## After publishing a new news item

1. Push the change. Wait for the GitHub Actions deploy to finish (~2 min).
2. Open GSC → *URL Inspection*, paste the new URL (e.g. `https://e3center.caece.net/news/2026-foo/`).
3. Click **Request Indexing**.
4. Typical lag: hours to a few days. Without this step, lag is weeks-to-never.

## After adding a new member

Same workflow as a news item, but for `https://e3center.caece.net/members/{webId}/`.

## Monthly check (optional, ~5 minutes)

1. GSC → *Performance* → filter by query (e.g. "I-Yun Lisa Hsieh"). Confirm the member subpage's
   average position is improving over time.
2. GSC → *Pages* → look for entries flagged "Discovered – currently not indexed". For each,
   open *URL Inspection* and *Request Indexing*.
3. GSC → *Sitemaps* → confirm latest sitemap fetch shows no errors.

## When the build emits SEO warnings

`python build.py` ends with `SEO check: N warnings (0 errors).` Warnings appear in the GitHub
Actions log on every push. They are non-fatal — the deploy still proceeds — but indicate
quality regressions:

| Warning | What to do |
|---|---|
| `description too short` / `too long` | Add or shorten `metaDescription` (members), `excerpt` (news.json), or `description` (pages.json) for that page. |
| `duplicate description on N pages` | Two pages have identical descriptions. Make at least one unique. |
| `thin news body (N words)` | The article markdown has < 200 words. Expand the article or accept the warning. |
| `missing canonical` / `missing <title>` | Likely a template bug — surface to a developer. |
| `JSON-LD block invalid` | A template change broke JSON syntax — surface to a developer. |
| `editor/index.html: ...` | Expected — the internal editor page is static and intentionally `noindex`. Safe to ignore. |

## Manually deindex a page

If a page that should never have been indexed shows up in Google:

1. Add `<meta name="robots" content="noindex, nofollow">` to its `<head>`.
2. Add `Disallow: /path/` to `static/robots.txt`.
3. GSC → *Removals* → submit the URL for temporary removal (~6 months).

## Authoring overrides

The SEO machinery uses sensible defaults but supports per-page overrides if a description reads awkwardly:

| Override | Where | When to use |
|---|---|---|
| `metaDescription` | `metaDescription` field in `contents/members/{webId}/member.json` | Rewrite a member's auto-generated description (e.g., the PI's). |
| `excerpt` | Optional field per item in `contents/news/news.json` | Override the article body excerpt with a custom snippet. |
| `description` | Per-listing field in `contents/pages.json` | Customise the listing pages' descriptions. |

If left empty/absent, the auto-generation kicks in — overrides are opt-in.

## Adding publication keywords (optional, improves topical SEO)

Each item in `contents/publications/publications.json` accepts an optional `keywords` array:

```json
{
  "title": "...",
  "year": "'24",
  "E3": true,
  "status": "published",
  "keywords": ["hydrogen", "life cycle assessment", "transportation"]
}
```

When present:
- Renders as visible keyword chips below the publication on `/publications/` and on each member's profile.
- Emits as `keywords` field on the publication's `ScholarlyArticle` entry in the page's `CollectionPage` JSON-LD.

Recommend populating from the keywords most journal articles publish in their first-page metadata. Initial scope: last 3 years of E3 publications. Older entries can leave `keywords` empty — they just don't get chips or JSON-LD keywords.
