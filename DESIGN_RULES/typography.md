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
the tokens, never raw rem.

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
larger than the largest CONTENT size. The rem values above are the
laptop/desktop tier — the ladder **re-declares per viewport tier** (tablet,
phone, and the ≥90rem wide tier; see [`responsive.md`](./responsive.md)).
On phones (≤37.5rem) the `:root` re-declares the ladder (h1 2rem … body
1.125rem) and **bumps** the LABEL group (eyebrow 0.8125, badge 0.75) so
labels clear the WCAG floor at the 87.5% root — never shrink a label below
its token on mobile.

> The pre-v3 alias names (Display-XL … Caption-S) were fully retired on
> 2026-07-27. There is exactly one ladder; `validate_design_tokens.py` fails if
> an alias reappears.

## Content Roles — one size per role

The ladder says which sizes exist; this table says who gets them. **A content
role binds to exactly one token (or one named recipe), and the binding holds
on every page** — the same kind of content is never sized differently because
it sits in publications rather than news or projects. Per-tier variation comes
from the token re-declarations ([`responsive.md`](./responsive.md)), never
from a per-page override.

| Role | Binding | Where |
|---|---|---|
| Detail-page h1 | `clamp(var(--fs-h3), 3vw, var(--fs-h2))` — the **hero-fluid recipe** | news article, publication detail, project detail |
| Member-profile h1 | `--fs-h1` | the one sanctioned h1 exception — member pages are page-defining portraits |
| Section heading | `--fs-h2` | member-profile h2, section-scale heads on detail pages |
| Sub-heading / rail label | `--fs-h3` | news year rail, detail sub-heads |
| Lede | `--fs-lede` | `.proj-item-lede` (via clamp to `--fs-h3` — sanctioned one-tier-up), venue lines |
| **Article prose** | `--fs-prose` (= `--fs-body`) via the **unified prose recipe** (`general.css` § prose) | `.abt-text`, `#about .content`, `#interest .content`, `.proj-prose`, `.proj-prose-zh`, `.news-item-body`, `.pub-item-abstract`, `.contact-tagline` |
| Row title | `--fs-body` | news + project listing rows |
| Row title (publications) | `--fs-lede` | sanctioned one-tier-up emphasis on research output ([I-2]) |
| Default paragraph | `--fs-body-base` | non-article paragraphs, form text |
| Meta line | `--fs-secondary` | authors, journals, dates, filter tabs, jump links |
| Eyebrow | `--fs-eyebrow` | [`patterns.md`](./patterns.md) § Eyebrow Label |
| Badge | `--fs-badge` | [`patterns.md`](./patterns.md) § Status / Category Badge |

Three rules make the invariant hold:

1. **New prose surface?** Add its class to the unified prose recipe's
   `:where()` list — never write `font-size` on a prose container.
2. **A role that looks wrong on one page** is fixed by changing the binding
   here (one line + a findings entry) — never by a local override on that page.
3. **Deviations are bugs** unless listed above as sanctioned.
   `validate_design_tokens.py` backstops the mechanism: no `font-size`
   declaration may contain a raw rem length.

---

## Line-Height & Letter-Spacing Conventions

Line-heights are tokens (`--lh-*` in `general.css :root`) — pair each with its
matching `--fs-*` tier; per-tier values live in the generated
[tokens.md](./tokens.md).

| Token | Value | Pairs with |
|---|---|---|
| `--lh-h1` / `--lh-h2` / `--lh-h3` | 1.10 / 1.15 / 1.20 | the HEADING tiers |
| `--lh-lede` | 1.4 | `--fs-lede` |
| `--lh-body` | 1.7 (1.55 on phones) | article prose (`--fs-prose`) |
| `--lh-body-base` | 1.55 | default paragraphs |
| `--lh-secondary` | 1.45 | meta lines |
| `--lh-eyebrow` / `--lh-badge` | 1.6 | uppercase labels |
| `--lh-flush` | 1 | single-line UI: buttons, chips, icon containers |

Letter-spacing is deliberately **not** tokenized — apply the conventions:

| Context | Letter-spacing |
|---|---|
| Display & headings | −0.025em to −0.03em |
| Item titles / row titles | −0.01em to −0.025em |
| Body | −0.01em (body global) |
| Uppercase eyebrow | **+0.14em** (0.16em only for contact info) |
| Uppercase badge | **+0.10em** |

> **Rule:** Negative tracking on display text, positive (and dramatic) tracking on uppercase. Never apply uppercase to sentence-case text without also widening tracking.
