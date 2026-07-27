# Design Rules — E3 Center

The canonical reference for typography, color, spacing, and responsive scaling across the E3 Center website. Rules are derived by auditing every CSS file (`general.css`, `style.css`, `subpage.css`, `member.css`, `news-item.css`) and cross-checking the templates.

When the rules and the current CSS disagree, treat these docs as the spec and the CSS drift as a bug. Document deliberate exceptions here rather than silently diverging.

## Index

| File | Covers |
|---|---|
| [`typography.md`](./typography.md) | Font families, weight scale, the 16-tier type scale, line-height and letter-spacing conventions. |
| [`color.md`](./color.md) | Brand color tokens, text emphasis ladder (opacity-based), accent color rules. |
| [`responsive.md`](./responsive.md) | Root font size, breakpoints, the three viewports (desktop / tablet / mobile), scaling strategy. |
| [`layout.md`](./layout.md) | Spacing tokens, the skewed-block motif (cards, buttons, images), shadows / borders / radii, motion, iconography, casing / bilingual pairing. |
| [`components.md`](./components.md) | Per-component rules: homepage hero, section titles, subpage header, publications, members, news, contact, group-life, footer, menu. |
| [`patterns.md`](./patterns.md) | Reusable recipes: eyebrow label, status badge, date marker, list-item title, section title with view-all link. |
| [`semantics-a11y.md`](./semantics-a11y.md) | Heading hierarchy (one h1 per page rule), accessibility floor (contrast, minimum sizes, tap targets). |

## How to use these docs

1. **Designing a new component?** Start with the [quick checklist](#quick-checklist) below. Then walk through `typography.md` → `color.md` → `layout.md` to pick the right tokens.
2. **Changing CSS?** Find the affected component in `components.md` and the underlying pattern (if any) in `patterns.md`. If your change requires breaking a rule, document the exception in the relevant file rather than letting the drift become invisible.
3. **Auditing a page?** Use the [Findings](#findings) section below to see which drifts are known and which have been resolved.

## Quick checklist for new components

When introducing a new piece of UI:

1. **Pick a tier** from the type scale (`typography.md`) — don't invent a new size.
2. **Default color** to `var(--main-color)` and adjust emphasis with opacity from the emphasis ladder (`color.md`).
3. **Pick line-height & letter-spacing** from the conventions table (`typography.md`) based on context (display / body / uppercase).
4. **Add tablet/mobile overrides** only if the auto-scale (root 87.5%) leaves the size outside the intended tier on that viewport. See `responsive.md`.
5. **Semantics**: if it's a page title, make it `<h1>`. If it's a section, `<h2>`. If it's a row's title, leave it as a `<p>`/`<div>` styled to a tier — do not use `<h4>`–`<h6>` for repeating list items. See `semantics-a11y.md`.
6. **Check at 1440 / 900 / 375 px**. If any size lands below 0.75 rem at 375 px, redesign.
7. **Is it a surface?** Cards, buttons, images, chips, and inputs must be `.skewed-block`s — −3° skew, hard offset shadow, counter-skewed children, radius-doubling hover. See `layout.md` § Skewed-Block Motif. Never add a flat or soft-shadowed surface.

---

## Findings

Severity: **[H]** high · **[M]** medium · **[L]** low. Status: **✅** resolved · **🟡** intentional/documented · **⏳** open.

### Semantic / Structure

- **[S-1] [H] ✅** Subpages now carry a semantic h1 via `partials/subpage-header.html` (sr-only on `/members/`, `/publications/`, `/news/`, `/group-life/`; visible on `/contact/`). Templates that render their own visible h1 (member profile, news article, contact) pass `suppressSrH1 = True`. `.sr-only` utility added to `general.css`.
- **[S-2] [M] ✅** `.contact-lead` is now `<h1>` (`templates/pages/contact.html:41`). Visual unchanged — `.contact-lead` already styled to Display-S.
- **[S-3] [M] ✅** `.news-cat-title` is now visually hidden via `.sr-only` recipe (`subpage.css:581`). Semantic h2 preserved for outline; no longer duplicates the active tab label.
- **[S-4] [L] ✅** `.section-title h2` shrunk from 4 rem → **3.25 rem** (`general.css:441`) and accompanying SVG from 3.75 rem → 3 rem so the homepage h1 (3 rem) is no longer dwarfed. The ladder's Display-XL tier is now 3.25 rem.

### Eyebrow / Label Consistency

- **[E-1] [L] ✅** `.news-item-hero-placeholder span` (`news-item.css:69-76`) normalized to eyebrow recipe (0.6875 rem / 0.14em / opacity 0.3).

### Weights / Fonts

- **[W-1] [M] ✅** Google Fonts URL extended to `wght@300..600` for both families (`templates/base.html:56-57`), so weights 300 (`.breadcrumb-sep`) and 400 (`.contact-info-sub`) now load instead of being synthesized.
- **[W-2] [L] 🟡** News-article body forces every heading (h2–h6) to `var(--fw-h1)`. Intentional editorial gravitas — documented in `components.md` § News Article Page.

### Colors

- **[C-1] [M] ✅** Opacity floor raised to **0.6** on body-size secondary text:
  - `.mem-row-zh`: 0.45 → 0.6 (`subpage.css:285`)
  - `.mem-row-position p:not(:first-child)`: 0.55 → 0.6 (`subpage.css:305`)
  - `.publi-row-authors` (subpage): 0.55 → 0.6 (`subpage.css:1049`)
  - `.publi-row-journal, .publi-row-authors` (homepage): 0.5 → 0.6 (`style.css:1793`)

### Sizing on Mobile

- **[A-1] [M] ✅** `.news-row-badge` mobile size 0.5625 rem → 0.6875 rem (~9.6 px at 14 px root) with compensating padding (`subpage.css:911`).
- **[A-2] [L] ✅** `.news-row-mm` mobile size 0.625 rem → 0.75 rem (`subpage.css:898`).

### Inconsistencies in Item Titles

- **[I-1] [L] ✅** False positive — no `text-transform: capitalize` exists anywhere in the codebase (the audit confused `.pub-title` for `.publi-title`). No change needed.
- **[I-2] [L] 🟡** `.publi-title` (1.5 rem) and `.news-row-title` (1.125 rem) differ by 33%. Intentional emphasis on research output — documented in `patterns.md` § List Item Title.

### Scaling Strategy

- **[R-1] [L] 🟡** Only `.news-item-title` uses `clamp()`. Rule for new components: prefer `clamp(min, vw, max)` over three breakpoint overrides for hero-tier text. Captured in `responsive.md`.
- **[R-2] [L] 🟡** Tablet (`@64rem`) does not scale the root. Verify each new component at 900 px width. Captured in `responsive.md`.

### 2026-07 News-Redesign Audit

- **[N-1] [M] ✅** News category colors tokenized: `--cat-*` (badge hue) + `--cat-*-text` (hue deepened toward `--main-color` for bare text) in `general.css :root`, consumed by `subpage.css` and `news-item.css`. Rule: category colors change at the token, never per-file. See `color.md` § News Category Tokens.
- **[N-2] [M] ✅** Badge pill text switched from raw `--r-*` hues (≈2.1–2.7:1 on the tint) to the `--cat-*-text` tier — same hue family, WCAG-safe. Pill tints keep the raw hue so the colorful identity is unchanged.
- **[N-3] [L] 🟡** News-listing thumbnails and inline article images render flat (0.375rem radius) — documented skew-motif exception in `layout.md`.
- **[N-4] [L] ✅** News hairlines migrated to `var(--line-soft)`; `.news-jump-label` aligned to the eyebrow recipe (0.14em); `.news-jump-link` opacity raised to the 0.6 interactive floor.
- **[N-5] [L] ✅** Doc refresh: weight ladder, v3 type-scale tokens, Google Fonts range (400..600), `--header-h` values, and the mobile LABEL-group bump now match `general.css`; stale per-rem tables replaced with token references.

### 2026-07 Brand Refinement

- **[B-1] [H] ✅** Four of five `--cat-*-text` tokens failed WCAG AA against their own badge tint (faculty 3.52:1, student 3.96:1, events 3.82:1, outreach 4.22:1; only media passed, at 5.16:1). Hue proportions were retuned until each cleared 4.5:1; student and events needed a second retune once [B-6] corrected the harness's own backdrop bug. Current values (all mixed toward `--main-color`): faculty 22%, student 35%, media 55% (unchanged), events 30%, outreach 40% — contrast-derived and guarded by `validate_design_tokens.py`.
- **[B-2] [H] ✅** `--main-color-2` (2.38:1) was used for text on 12 rules and for focus rings on several more. Text moved to the new `--accent-ink` (4.93:1); focus rings moved to `--main-color` (7.66:1), which also removes an inconsistency with the rest of the site.
- **[B-3] [M] ✅** Colour documented as three layers (primitive / semantic UI / illustration). The apparent "sprawl" of 117 root tokens is three systems read as one; no token was deleted, and the primitives are load-bearing `sprite.svg` artwork.
- **[B-4] [M] ✅** The v3 type migration finished: seven deprecated `--fs-*` aliases and their 22 call sites retired, leaving one ladder.
- **[B-5] [L] ✅** `components.md` resynced — the subpage-header table described `.breadcrumb-*` classes that had been renamed and then moved out of the header entirely; `.section-title h2` said 4 rem against a 3 rem token.
- **[B-6] [H] ✅** `validate_design_tokens.py`'s category-contrast check modelled every badge tint as the hue mixed over white, but every tint in this codebase is `color-mix(in srgb, <hue> N%, transparent)` — a transparent mix that composites over whatever sits behind the element, which is `--page-bg-color` (#f7fafb), never white. Because `#f7fafb` is darker than white, the harness understated the rendered tint and overstated the contrast ratio, certifying three tokens as passing when they were really failing on screen: `--cat-student-text`, `--cat-events-text`, and `--status-ok-text`. Fixed by compositing over the real page background, and by widening the check from `--cat-*-text` only to any base/`-text` token pair, so `--status-*-text` — and any future pair — is covered automatically. All three were retuned and now clear AA against every real per-component tint percentage (12–14%) and the page background — worst case 4.64:1. The most instructive finding of Phase 1: a passing harness is not proof of a passing render if it models the wrong backdrop.
- **[B-7] [M] ✅** `--status-alert-text` mixed `--r-red` 40% toward `--main-color` (navy) — the same recipe as every other `-text` token — but red and navy are far enough apart in hue that the blend rotated past blue: the mix resolved to `#5e617b`, hue ≈234°, a blue-slate that no longer read as an alert. Contrast was never the failure (5.35:1 on tint, 5.77:1 on page bg); the hue was. Fixed by mixing 60% red toward a dark red anchor (`#3a0d0d`) instead of navy — `#9b4b4c`, hue 359°, unmistakably red, still 5.08:1 on tint / 5.71:1 on page bg. Lesson for any future `-text` token: mixing toward `--main-color` only stays in-hue when the source hue is close enough to navy to read as "the same colour, deeper"; red isn't, so alert is the one status/category token that's intentionally special-cased.

### House-keeping

- **[K-1] [L] ✅** `--fs-*` design tokens declared in `general.css :root` (additive — Display-XL/L/M/S, Heading-L/M/S, Body-XL/L/Body/Base/S, Caption/-S, Eyebrow, Badge). Existing CSS still uses hard-coded rem; new CSS should reach for these tokens first.
- **[K-2] [L] ✅** `.text-eyebrow` and `.text-badge` utility classes added in `general.css`. Existing classes retain their own declarations for backward compat — new label/badge UI should use the utilities.
