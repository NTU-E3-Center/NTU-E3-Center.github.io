# Projects

Research project data for the E3 Center. The listing (`projects.json`) drives the
`/projects/` page and the homepage Projects section. Flagship projects can also
get a rich individual detail page at `/projects/<slug>/` — see
[Detail pages](#detail-pages) below.

## `projects.json`

An array of section objects, following the same shape as other files in
`contents/structures/`:

```jsonc
[
  { "sectionTitle": "...", "items": [ /* project entries */ ] }
]
```

Two sections:

1. **臺灣國科會 (Taiwan NSTC)** — government grants from the National Science and
   Technology Council.
2. **其他計畫 (Other Projects)** — industry and other-agency commissioned projects.

### Entry fields

| Field             | Sections | Notes                                                      |
|-------------------|----------|------------------------------------------------------------|
| `titleZh`         | both     | Chinese project name (NSTC: grant number stripped out).    |
| `titleEn`         | both     | English project name.                                      |
| `grantNumber`     | NSTC     | NSTC grant code, e.g. `114-2628-E-002-009-MY3`.            |
| `role`            | both     | `主持人` (PI) or `共同主持人` (Co-PI).                       |
| `startDate`       | both     | ISO `YYYY-MM-DD`, from the source `起訖年月`.               |
| `endDate`         | both     | ISO `YYYY-MM-DD`, from the source `起訖年月`.               |
| `fundingAgency`   | both     | Funding / commissioning organization (`補助或委託機構`).     |
| `fundingAgencyEn` | both     | English name of the funding / commissioning organization.  |
| `status`          | both     | `執行中` (ongoing) or `已結案` (completed).                  |
| `slug`            | both     | Opt-in detail-page switch. Empty = plain row. Non-empty + a matching `contents/projects/<slug>/` folder = a detail page at `/projects/<slug>/`. Keep `""` on every entry for uniform keys. |

## Detail pages

A project gets a rich detail page at `/projects/<slug>/` when **both** are true:

1. its entry in `projects.json` has a non-empty `"slug"`, and
2. a folder `contents/projects/<slug>/` exists with a `project.json`.

Projects without a slug stay as plain listing rows (default). Core metadata
(`titleEn`, `titleZh`, `grantNumber`, `role`, dates, funder, `status`) lives only
in `projects.json` — do **not** repeat it in `project.json`. `build.py`
(`render_project_pages`) merges the two by slug.

### Folder contents

```
contents/projects/<slug>/
  project.json     # rich fields (below)
  about.md         # English narrative (markdown)
  about.zh.md      # Chinese narrative (optional)
  images/          # photos referenced by gallery[].file (optional)
```

### `project.json` fields

```jsonc
{
  "shortTitle": "",       // optional concise title for the <title> tag + social cards
                          // (keeps very long official names within the ~60-char SEO budget);
                          // the full titleEn stays the visible heading. Omit if titleEn is short.

  "summary":   "",        // one-line EN teaser (used for meta description fallback)
  "summaryZh": "",

  "keyFindings": [        // headline results/outcomes; omit while a project is early
    { "text": "", "textZh": "" }
  ],

  "partners": [           // external collaboration orgs
    { "name": "", "nameZh": "", "url": "", "logo": "", "role": "" }
    //  logo = filename in images/ (e.g. "partner-foo.png") or "" (optional)
  ],

  "team": [               // internal people; ALWAYS fill name; webId adds a link
    { "webId": "", "name": "", "role": "" }
    //  webId must match a folder under contents/members/<webId>/ to link
  ],

  "relatedPublications": [  // by citationId from publications.json (published only)
    { "citationId": "" }
  ],

  "outputs": [            // outputs beyond journal papers
    { "type": "", "title": "", "titleZh": "", "url": "", "note": "" }
    //  type e.g. tool | dataset | report | software | patent | dashboard
  ],

  "gallery": [            // ORDERED list of photos to show; entries not on disk are skipped
    { "file": "", "caption": "", "captionZh": "" }
    //  file = filename in images/ (e.g. "1.jpg")
  ],

  "metaDescription": ""   // SEO; falls back to summary
}
```

**Uniform keys inside arrays:** every object in an array shares the same key set —
use empty strings for blanks, don't omit keys. Leave a whole array `[]` when a
section doesn't apply; the page omits empty sections.

See `contents/projects/2026-green-finance-taiwan-india/` for a worked example.
