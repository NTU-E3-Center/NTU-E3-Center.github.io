# Typography

Part of [DESIGN_RULES/](./README.md). Covers font families, weight scale, the type scale, and line-height / letter-spacing conventions.

---

## Font Families

| Stack | Use | Where loaded |
|---|---|---|
| `'Outfit', 'Noto Sans TC', sans-serif` | All text, every element | `templates/base.html:54–57` (Google Fonts), `general.css:128–130` (applied via `*`) |

- **Outfit** carries Latin glyphs; **Noto Sans TC** carries Traditional Chinese glyphs. They are visually paired (geometric, even x-height).
- The universal selector forces this stack on every node — do not override per-component.

## Font Weight Scale (`--fw-*` in `general.css :root`)

Consolidated three-rung ladder (v3). The old `--fw-h1/h2/h3` names survive as
aliases of `--fw-display`.

| Token | Value | Use |
|---|---|---|
| `--fw-light` | `400` | De-emphasised text: Zh subtitles, DOI mono, "sub" labels |
| `--fw-body` | `450` | Default running text |
| `--fw-display` | `500` | h1 / h2 / h3 — size carries the hierarchy, weight only whispers |
| `--fw-heading` (= `--fw-bold`) | `600` | Eyebrows, badges, button labels, `<strong>` — small UI text needs the weight to read |

**Loaded from Google Fonts:** `Outfit:wght@400..600` and `Noto+Sans+TC:wght@400..600`. Nothing lighter than 400 is used anywhere, so the 300 range is no longer requested.

---

## The Type Scale

All values are in `rem` (relative to the root font size — see [`responsive.md`](./responsive.md)). Where a cell shows two values separated by `→`, the first applies via the explicit per-component override, the second via root scaling alone.

### Document-level Headings (`general.css:65–84`)

| Element | Desktop | Tablet | Mobile | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|---|---|
| `h1` (base) | **3.5 rem / 56 px** | 3.5 rem / 56 px | 3.5 rem / **49 px** (via root) | 600 | 1.10 | −0.03em |
| `h2` (base) | **2.25 rem / 36 px** | 2.25 rem | 2.25 rem / 31.5 px | 550 | 1.15 | −0.025em |
| `h3` (base) | **1.75 rem / 28 px** | **1.25 rem** (style.css:2200) | **1.125 rem** (style.css:2387) | 500 | 1.20 | −0.02em |

> No `h4`/`h5`/`h6` base rule exists. They appear only inside the news article body (see [`components.md`](./components.md) § News Article Page).

### Visual Type Scale (v3 tokens — the single authoritative ladder)

Nine tokens in three groups, defined in `general.css :root`. New CSS must use
the tokens, never raw rem. The older 17-tier names (Display-XL … Caption-S)
survive only as deprecated aliases mapped onto these tokens.

| Group | Token | rem | px | Use |
|---|---|---|---|---|
| HEADING | `--fs-h1` | 3.00 | 48 | Page h1, hero |
| HEADING | `--fs-h2` | 2.25 | 36 | Section h2 |
| HEADING | `--fs-h3` | 1.75 | 28 | Sub-section h3, news year rail label |
| CONTENT | `--fs-lede` | 1.375 | 22 | Ledes, news-row year, breadcrumb current |
| CONTENT | `--fs-body` | 1.125 | 18 | Article prose (via `--fs-prose`), row titles |
| CONTENT | `--fs-body-base` | 1.00 | 16 | Default paragraph, phone article prose |
| CONTENT | `--fs-secondary` | 0.875 | 14 | Meta lines, filter tabs, jump links |
| LABEL | `--fs-eyebrow` | 0.6875 | 11 | Group/category eyebrows |
| LABEL | `--fs-badge` | 0.625 | 10 | Category/status badge pills |

Hierarchy invariant: at every breakpoint, the smallest HEADING size stays
larger than the largest CONTENT size. On phones (≤37.5rem) the `:root`
re-declares the ladder (h1 2rem … body 1.125rem) and **bumps** the LABEL
group (eyebrow 0.8125, badge 0.75) so labels clear the WCAG floor at the
87.5% root — never shrink a label below its token on mobile.

## Line-Height & Letter-Spacing Conventions

| Context | Line-height | Letter-spacing |
|---|---|---|
| Display & headings | 1.10 – 1.20 | −0.025em to −0.03em |
| Item titles / row titles | 1.15 – 1.50 | −0.01em to −0.025em |
| Body paragraph | 1.55 | −0.01em (body global) |
| News article body | **1.70** | inherited |
| Caption / small meta | 1.30 – 1.45 | 0 |
| Uppercase eyebrow | 1.6 | **+0.14em** (or 0.16em for contact) |
| Uppercase badge | 1.6 | **+0.10em** |

> **Rule:** Negative tracking on display text, positive (and dramatic) tracking on uppercase. Never apply uppercase to sentence-case text without also widening tracking.
