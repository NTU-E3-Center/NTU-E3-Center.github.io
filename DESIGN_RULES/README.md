# Design Rules — E3 Center

The canonical reference for typography, color, spacing, and responsive scaling across the E3 Center website. Rules are derived by auditing every CSS file (`general.css`, `style.css`, `subpage.css`, `member.css`, `news-item.css`) and cross-checking the templates.

When the rules and the current CSS disagree, treat these docs as the spec and the CSS drift as a bug. Document deliberate exceptions here rather than silently diverging.

## Index

| File | Covers |
|---|---|
| [`brand.md`](./brand.md) | **The identity layer** — who E3 is, the design concept, palette meaning, voice, the protected signature list, decision principles. |
| [`typography.md`](./typography.md) | Font families, weight scale, the token ladder, **content-role bindings (one size per role, on every page)**, line-height and letter-spacing conventions. |
| [`color.md`](./color.md) | Brand color tokens, text emphasis ladder (opacity-based), accent color rules. |
| [`responsive.md`](./responsive.md) | Root font size, the **four** viewport tiers (phone / tablet / laptop / wide ≥1440px), large-screen policy, component-local breakpoints, the five testing widths. |
| [`layout.md`](./layout.md) | Spacing tokens, the skewed-block motif (cards, buttons, images), shadows / borders / radii, motion, iconography, casing / bilingual pairing. |
| [`components.md`](./components.md) | Component intent map: what each component is for, which roles/patterns it uses, sanctioned deviations. Values live in CSS, not here. |
| [`patterns.md`](./patterns.md) | Reusable recipes: eyebrow label, status badge, date marker, list-item title, section title with view-all link. |
| [`semantics-a11y.md`](./semantics-a11y.md) | Heading hierarchy (one h1 per page rule), contrast/size floor, focus, motion, forms. |
| [`extending.md`](./extending.md) | Playbooks: new subpage, new component, new category/status; the rule-change procedure; redesign policy. |
| [`tokens.md`](./tokens.md) | **Generated** inventory of every `:root` token with per-tier values. Regenerate with `make tokens` — never hand-edit. |

## How to use these docs

1. **Designing something new?** Read `brand.md` first for direction, then the [quick checklist](#quick-checklist) below, then `typography.md` → `color.md` → `layout.md` to pick roles and tokens. Adding a whole page or category? Follow the playbook in `extending.md`.
2. **Changing CSS?** Find the affected component in `components.md` and the underlying pattern (if any) in `patterns.md`. If your change requires breaking a rule, document the exception in the relevant file rather than letting the drift become invisible.
3. **Auditing a page?** Use the [Findings](#findings) section below to see which drifts are known and which have been resolved.

## Quick checklist for new components

When introducing a new piece of UI:

1. **Pick a role** from the content-role table (`typography.md` § Content Roles) — the role gives you the token. Don't invent a new size, and never write `font-size` on a prose container (add it to the unified prose recipe instead).
2. **Default color** to `var(--main-color)` and adjust emphasis with opacity from the emphasis ladder (`color.md`).
3. **Pick line-height & letter-spacing** from the conventions table (`typography.md`) based on context (display / body / uppercase).
4. **Add tablet/mobile overrides** only if the auto-scale (root 87.5%) leaves the size outside the intended tier on that viewport. See `responsive.md`.
5. **Semantics**: if it's a page title, make it `<h1>`. If it's a section, `<h2>`. If it's a row's title, leave it as a `<p>`/`<div>` styled to a tier — do not use `<h4>`–`<h6>` for repeating list items. See `semantics-a11y.md`.
6. **Check at 375 / 768 / 1024 / 1440 / 1920 px** (see `responsive.md` § Testing rule). If any size lands below 0.75 rem at 375 px, redesign.
7. **Is it a surface?** Interactive/photographic surfaces (buttons, CTAs, images, portraits) are `.skewed-block`s — −3° skew, hard offset shadow, counter-skewed children, radius-doubling hover. Dense repeating chrome (filter pills, show-more pills, thumbnails, inline images, chips, status/category badges) renders flat by design instead. See `layout.md` § Skewed-Block Motif for the exact split. Either way, never add a soft-shadowed surface.

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
- **[B-3] [M] ✅** Colour documented as three layers (primitive / semantic UI / illustration). The apparent "sprawl" is 42 colour tokens (out of 117 `:root` tokens total — the rest is spacing, type-scale, and timing tokens that this colour model doesn't explain) read as three systems as one; no token was deleted, and the primitives are load-bearing `sprite.svg` artwork.
- **[B-4] [M] ✅** The v3 type migration finished: seven deprecated `--fs-*` aliases and their 22 call sites retired, leaving one ladder.
- **[B-5] [L] ✅** `components.md` resynced — the subpage-header table described `.breadcrumb-*` classes that had been renamed and then moved out of the header entirely; `.section-title h2` said 4 rem against a 3 rem token.
- **[B-6] [H] ✅** `validate_design_tokens.py`'s category-contrast check modelled every badge tint as the hue mixed over white, but every tint in this codebase is `color-mix(in srgb, <hue> N%, transparent)` — a transparent mix that composites over whatever sits behind the element, which is `--page-bg-color` (#f7fafb), never white. Because `#f7fafb` is darker than white, the harness understated the rendered tint and overstated the contrast ratio, certifying three tokens as passing when they were really failing on screen: `--cat-student-text`, `--cat-events-text`, and `--status-ok-text`. Fixed by compositing over the real page background, and by widening the check from `--cat-*-text` only to any base/`-text` token pair, so `--status-*-text` — and any future pair — is covered automatically. All three were retuned and now clear AA against every real per-component tint percentage (12–14%) and the page background — worst case 4.64:1. The most instructive finding of Phase 1: a passing harness is not proof of a passing render if it models the wrong backdrop.
- **[B-7] [M] ✅** `--status-alert-text` mixed `--r-red` 40% toward `--main-color` (navy) — the same recipe as every other `-text` token — but red and navy are far enough apart in hue that the blend rotated past blue: the mix resolved to `#5e617b`, hue ≈234°, a blue-slate that no longer read as an alert. Contrast was never the failure (5.35:1 on tint, 5.77:1 on page bg); the hue was. Fixed by mixing 60% red toward a dark red anchor (`#3a0d0d`) instead of navy — `#9b4b4c`, hue 359°, unmistakably red, still 5.08:1 on tint / 5.71:1 on page bg. Lesson for any future `-text` token: mixing toward `--main-color` only stays in-hue when the source hue is close enough to navy to read as "the same colour, deeper"; red isn't, so alert is the one status/category token that's intentionally special-cased.
- **[B-8] [M] ✅** The motif rule claimed every card, button, image, chip and input is a skewed block, while five component types were already flat and logged as exceptions (`.news-item-body img`, `.news-row-thumb`, `.news-filter-tab`, `.publi-show-more`/`.news-show-older`) — and two more flat families existed but were never documented: keyword chips (`.pub-tag-chip`) and status/category badges (`.news-row-badge`, `.pub-status-badge`, `.proj-status-pill`, `.proj-role-badge`, `.proj-honor-badge`). Rule inverted to scope by surface kind (interactive/photographic = skewed, dense repeating chrome = flat), and the flat list was re-verified against the CSS rather than carried over from spec. Block geometry lightened: shadow 5px → 4px and hover shadow 7px → 6px (`--block-shadow-shift` / `--block-hover-shadow-shift`, shared tokens in `general.css`); border 3px → 2px, which turned out **not** to be a shared token — each block component sets it independently via `--_adjusted-border-width` (usually through a local `--_img-border-w`) across `style.css`, `subpage.css`, `news-item.css`, and `member.css`, so the change touched ten component-level declarations, not one. Two button-tier components locally borrow block-weight geometry (`.hp-about-us`'s hardcoded shadow/border; the menu drawer's border) and were deliberately left at their old values rather than silently pulled forward — flagged for a follow-up call instead.

### House-keeping

- **[K-1] [L] ✅** `--fs-*` design tokens declared in `general.css :root` (additive — Display-XL/L/M/S, Heading-L/M/S, Body-XL/L/Body/Base/S, Caption/-S, Eyebrow, Badge). Existing CSS still uses hard-coded rem; new CSS should reach for these tokens first.
- **[K-2] [L] ✅** `.text-eyebrow` and `.text-badge` utility classes added in `general.css`. Existing classes retain their own declarations for backward compat — new label/badge UI should use the utilities.

### 2026-08 System Restructure

- **[D-1] [M] ✅** `components.md` converted from per-element rem tables — stale copies of the CSS, the exact drift class behind [B-5]/[N-5], and by then doubly wrong because the CSS had finished migrating to tokens — into a component **intent map**: purpose, role/pattern usage, and sanctioned deviations only. Values live solely in the CSS and the role bindings. Projects and the publication/project detail pages, previously missing entirely, are now covered.
- **[D-2] [M] ✅** `responsive.md` now documents all **four** tiers — the ≥90rem wide tier in `general.css` was previously invisible to the docs — plus the large-screen content-cap policy (content ≈1120px on any display ≥1440px; type scales, measure doesn't), the component-local breakpoint registry (56rem, 48rem, 64.0625rem), and a five-width testing rule (375/768/1024/1440/1920, spot-check 2560). Also fixed its stale desktop `--header-h: 7.25rem` claim — CSS and `layout.md` both say 5.5rem; duplicated facts drift, which is why the restructure de-duplicated them.
- **[D-3] [M] ✅** `semantics-a11y.md` codified practice that existed only in the CSS: the global `:focus-visible` recipe (2px `--main-color` outline; skewed blocks mirror hover on focus), the every-animation-ships-a-`prefers-reduced-motion` rule (ten reduce blocks exist), and the 16px iOS form auto-zoom floor.
- **[D-4] [M] ✅** One-size-per-role invariant documented (`typography.md` § Content Roles): every content role binds to exactly one token or named recipe on every page — a content paragraph is the same size in publications, news, and projects at each tier. The unified prose recipe (`general.css` § prose) already enforced this for eight prose surfaces; `.pub-item-title`'s hero-fluid clamp was the one drift (3.2vw vs the 3vw shared by news/project detail h1s) and was unified.
- **[D-5] [L] ✅** `validate_design_tokens.py` grew a fourth invariant: no `font-size` declaration may contain a raw rem length (comments stripped first; custom properties like `--_adjusted-font-size` excluded by lookbehind). Its first run caught three stragglers the doc-era greps had missed: two `var()` fallbacks that mapped exactly onto existing tokens (`1rem` → `--fs-body-base`, `0.875rem` → `--fs-secondary`, neither re-declared per tier, so no pixel changes) and the hand-written iOS input floor, which became the semantic device-constant token `--fs-input-floor` (1.1875rem).
- **[D-6] [L] ✅** Added `brand.md` — the identity layer (design concept, palette meaning, voice, the protected signature list, decision principles) — and `extending.md` — playbooks for new subpages/components/categories, the rule-change procedure, and the evolution-over-revolution redesign policy.
- **[A-3] [M] ✅** Resolved by a global reduced-motion kill-switch in `general.css` (placed after the smooth-scroll rule so its `auto` override wins in source order): every `animation` collapses to a single instant frame, smooth scroll snaps to `auto`, and `@view-transition` navigation turns off under `prefers-reduced-motion: reduce`. The audit had found the entire hero sprite world (~20 infinite loops in `style.css`) and the body-bg pan unguarded. Targeted per-component blocks remain for transition-based states — the kill-switch covers `animation` only.

### 2026-08 System Hardening

- **[D-7] [M] ✅** Documented the last undocumented systems: the 19-step `--space-*` spacing ladder and the four-band z-layer registry (`layout.md`), and the `--lh-*` line-height tokens (`typography.md`, which also now records that letter-spacing is deliberately un-tokenized).
- **[D-8] [M] ✅** Validator invariant 5: no raw colour literal (hex or `rgb()`/`hsl()`) outside `:root` or `@media print`. Its first run caught four sites the doc-era audits missed, all fixed pixel-identically: the scrollbar track (→ `--scrollbar-track`), the hero plane-banner fill `#06334b` (→ `--main-dark`), `.pub-keyword-chip` hand-writing `--main-color`'s literal value twice (→ `var(--main-color)` + an 8% `color-mix`), and `.pub-status-badge`'s hand-rolled ink (→ `--status-progress-ink`; see [P-1]). Mask-alpha `#000` in `member.css` was normalized to the `black` keyword — mask colours are alpha, not palette.
- **[D-9] [L] ✅** `tokens.md` is now **generated** from `general.css :root` by `generate_token_reference.py` — a per-tier inventory of all 121 tokens that cannot drift, replacing the class of hand-copied tables retired in [D-1]. `make tokens` runs the validator then regenerates it.
### 2026-08 Navigation IA

- **[IA-1] [M] ✅** Header nav restructured from seven flat links into five items with three dropdowns — About · People ▾ (All Members / Faculty & Staff / Students / Alumni anchors) · Research ▾ (Publications / Projects) · News & Life ▾ (News / Group Life) · Contact. Decisions and their whys: "Media" was rejected as a group name (collides with the "In the Media" news category); member groups use **anchor links** into `/members/` (`scroll-margin-top` compensated) rather than subpages — revisit if the alumni list outgrows one page; About stays in the nav (logo keeps its universal go-home meaning); Contact stays top-level (conversion target). Grouping is data-driven via `navGroup` / `subnav` fields in `contents/pages.json`; the drawer mirrors groups as eyebrow labels. Dropdown spec in `components.md` § Subpage Header.

- **[P-1] [H] ✅** `.pub-status-badge`'s "In Progress" ink was a hand-rolled `color-mix` measuring ≈**2.3:1** on its 22% secondary tint — far below AA at badge size, and invisible to the harness because it was never a token. Fixed by minting the `--status-progress` / `--status-progress-text` pair: the text tier deepened from 70% to **28%** secondary toward the dark-olive anchor `#4a4a00` (`#6c6d29` — 4.68:1 on the real 22% tint, 5.19:1 on the page bg, same hue family). Because the badge's 22% tint is darker than the generic pair check's modeled 14%, the validator now also verifies this pair explicitly at 22% — the generic loop couldn't move to 22% wholesale, as the `--cat-*` pairs render at 12–14% and five of them would over-fail there (measured 4.32–4.39:1). Lesson repeated from [B-6]: check the backdrop that actually renders.
