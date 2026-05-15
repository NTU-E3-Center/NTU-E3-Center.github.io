# Typography

Part of [DESIGN_RULES/](./README.md). Covers font families, weight scale, the type scale, and line-height / letter-spacing conventions.

---

## Font Families

| Stack | Use | Where loaded |
|---|---|---|
| `'Outfit', 'Noto Sans TC', sans-serif` | All text, every element | `templates/base.html:54–57` (Google Fonts), `general.css:128–130` (applied via `*`) |

- **Outfit** carries Latin glyphs; **Noto Sans TC** carries Traditional Chinese glyphs. They are visually paired (geometric, even x-height).
- The universal selector forces this stack on every node — do not override per-component.

## Font Weight Scale (`--fw-*` in `general.css:133–138`)

| Token | Value | Use |
|---|---|---|
| `--fw-h1` | `600` | h1, hero, page titles, large numeric markers (news year, breadcrumb parent) |
| `--fw-h2` | `550` | h2, contact-lead |
| `--fw-h3` | `500` | h3 |
| `--fw-body` | `500` | All body, paragraphs, default text |
| `--fw-bold` | `600` | `<b>`, `<strong>`, emphasis |

**Loaded from Google Fonts:** `Outfit:wght@300..600` and `Noto+Sans+TC:wght@300..600`. Weights 300 (`.breadcrumb-sep`) and 400 (`.contact-info-sub`) load instead of being synthesized.

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

### Visual Type Scale (single authoritative ladder)

Use this ladder when introducing new typography. Numbers below are the **desktop** size; multiply by 0.7 for tablet and 0.55–0.7 for mobile (see [`components.md`](./components.md) for exact mobile overrides).

| Tier | rem | px | Use |
|---|---|---|---|
| Display-XL | 4.00 | 64 | `.section-title h2` (homepage section titles only) |
| Display-L  | 3.50 | 56 | `h1` baseline / news-item h1 ceiling |
| Display-M  | 3.00 | 48 | Homepage hero `#home .hp-title h1` |
| Display-S  | 2.75 | 44 | Breadcrumb parent, member-profile h1, contact-lead, PI member row |
| Heading-L  | 2.25 | 36 | `h2` baseline, member-profile h2, member-row name |
| Heading-M  | 1.75 | 28 | `h3` baseline, member-leader EN name |
| Heading-S  | 1.50 | 24 | Publication title, news-item year, member-profile res-tag, cursor-text |
| Body-XL    | 1.375 | 22 | Breadcrumb current, news-row year, plane label |
| Body-L     | 1.25 | 20 | Section subtitle, slider caption, position-text, footer link, body-lg |
| Body       | 1.0625 | 17 | Publication subtitle/date, contact-info-value, member-row position |
| Body-Base  | 1.00 | 16 | Default paragraph |
| Body-S     | 0.9375 | 15 | Publication authors, mobile body, news-item-date-mm |
| Caption    | 0.875 | 14 | Filter labels, news filter tabs, show-more |
| Caption-S  | 0.8125 | 13 | Mem-tag, news-row month, secondary-meta, mobile mem-info |
| Eyebrow    | 0.6875 | 11 | Group titles (members/news/publications), contact info labels, news-item category |
| Badge      | 0.625 | 10 | `.news-row-badge`, `.publi-status-badge` |

---

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
