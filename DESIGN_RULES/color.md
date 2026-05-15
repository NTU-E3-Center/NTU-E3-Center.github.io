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
| `--secondary-color` (#c4c691) | h3 decorative underline bar (`general.css:498–512`), homepage "3E" dot, section-subtitle icons |
| `--r-green` etc. | Status / category badges only |
