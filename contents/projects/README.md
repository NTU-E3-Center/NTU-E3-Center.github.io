# Projects

Research project data for the E3 Center. Stored here as data only — not yet wired
into `build.py` or any template.

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
