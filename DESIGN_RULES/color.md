# Color & Emphasis

Part of [DESIGN_RULES/](./README.md). Covers brand color tokens, the text-emphasis ladder (opacity-based), and accent color rules.

---

## Brand Color Tokens (defined in `general.css:132–164`)

| Token | Value | Role |
|---|---|---|
| `--main-color` | `#0a557e` | All text. Default for every node via `* { color: var(--main-color) }`. |
| `--main-shadow-color` | `#0a557ebb` | Hard offset block-shadow color on every skewed-block (≈73%-alpha teal). See [`layout.md`](./layout.md) § Shadows. |
| `--main-color-2` | `#4caedd` | Accent for sub-headings, secondary titles (e.g., member position). |
| `--main-color-3` | `#badcea` | Soft accent (icons, backgrounds). |
| `--secondary-color` | `#c4c691` | Olive accent — under-titles, h3 underline bar, "3E" dot. |
| `--main-bg-color` | `#ffffff` | Page surfaces. |
| `--page-bg-color` | `#f7fafb` | Subtle off-white for subpages. |
| `--r-{red,orange,yellow,green,blue,indigo,purple}` | rainbow | Status badges, category badges (news, publications). |
| `--link-color` | `#1a6489` | Inline prose links — 6.2:1 on `--page-bg-color` (the accent `--main-color-2` fails AA inline). |
| `--line-soft` | `color-mix(main 12%)` | The single hairline-divider token (news rows, footer rule, chip outlines). Don't hand-roll new 10–16% mixes. |
| `--cat-{faculty,student,media,events,outreach}` | per category | News category hues (badge tier). See § News Category Tokens. |
| `--cat-*-text` | per category | Category hues deepened toward `--main-color` for bare uppercase text. |
| `--selection-color` | `#0a557edd` | Text selection background. |

> **Rule:** All text defaults to `--main-color`. Hierarchy is expressed through **opacity** (0.4 → 0.55 → 0.7 → 1.0), not through different greys. Accent colors only for badges, decorative bars, and brand marks.

---

## Text Emphasis Ladder

Apply by changing **opacity** on the same `var(--main-color)`, not by switching colors.

| Level | Opacity | Use |
|---|---|---|
| Primary | `1.0` | All headings, titles, primary body |
| Secondary | `0.7` | Sub-name on member profile, news-item date mm |
| Muted | `0.55` | Publication authors, member secondary position |
| Subtle | `0.45–0.5` | Breadcrumb current, mem-row-zh, news-row mm |
| Eyebrow | `0.4` | Group/category eyebrow titles |
| Decorative | `0.25–0.35` | Breadcrumb separator, placeholder text |

> **Rule:** Never invent a new grey. If you need a dimmer text, lower opacity on `--main-color`. The single exception is colored status/category badges, which use the `--r-*` palette at full opacity.

> **Accessibility floor:** Body-size text below opacity 0.6 risks failing WCAG AA contrast. See [`semantics-a11y.md`](./semantics-a11y.md).

---

## Accent Color Use

| Color | Use only for |
|---|---|
| `--main-color-2` (#4caedd) | Member-row primary position line (`.mem-row-position p:first-child`) |
| `--secondary-color` (#c4c691) | h3 decorative underline bar, homepage "3E" dot, section-subtitle icons |
| `--r-green` etc. | Status badges (publications) and as the base hues behind `--cat-*` |
| `--cat-*` / `--cat-*-text` | News category coding — see below |

---

## News Category Tokens

The five news categories each own one hue, defined once in `general.css :root`
and consumed by `.news-row-badge` (subpage.css) and `.news-item-category`
(news-item.css). **Never restate a category color per-file — change the token.**

| Category | Badge tier `--cat-*` | Text tier `--cat-*-text` |
|---|---|---|
| Faculty Honors | olive (secondary 70% + #4a4a00) | secondary 45% + main |
| Student Awards | `--r-green` | green 55% + main |
| In the Media | `--r-indigo` | indigo 55% + main |
| Events and Exchanges | `--main-color-2` | accent 50% + main |
| Education and Outreach | `--r-orange` 85% + #000 | orange 50% + main |

Two tiers, one rule:

- **Badge tier** — the raw hue. Use it only for the pill's *tint background*
  (13–22% mix over transparent). Pill **text** uses the text tier.
- **Text tier** — the hue mixed toward `--main-color` (navy). Use it whenever
  category-colored text sits on the page background with no tint behind it:
  the detail-page category eyebrow, and the phone listing label (where the
  pill demotes to a bare label). This is the *only* sanctioned way to derive
  a new text color from an accent hue — mix toward `--main-color`, never
  toward black or an arbitrary grey.
