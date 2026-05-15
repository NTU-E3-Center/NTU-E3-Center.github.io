# Layout, Surfaces & Motif

Part of [DESIGN_RULES/](./README.md). Covers spacing tokens, the signature skewed-block motif (cards, buttons, images), shadows / borders / radii, motion / backgrounds, iconography, and casing / bilingual pairing rules.

---

## Layout & Spacing Tokens (`general.css:226–290`)

| Token | Desktop (`>1024px`) | Tablet (`≤1024px`) | Mobile (`≤600px`) | Role |
|---|---|---|---|---|
| `--gutter-x` | `clamp(2.5rem, 6vw, 6rem)` | `clamp(2rem, 5vw, 4rem)` | `2rem` | Horizontal section gutter — the **single** source of left/right inset. |
| `--section-pad-y` | `8rem` | `6rem` | `4rem` | Vertical padding on each top-level section. |
| `--section-title-gap` | `2.5rem` | `2rem` | `1.5rem` | Gap between `.section-title` and the first content row. |
| `--header-h` | `7.25rem` | `5rem` | `2.75rem` | Fixed-header height (used to vertically center the menu button). |
| `--menu-btn-h` | `2.5rem` | `2.75rem` | `2rem` | Menu button height. |
| `--para-max-width` | `60rem` | — | — | Max measure for body paragraphs. |

- Sections that carry a `.section-title` are `width: min(100%, 80rem); margin-inline: auto` (`general.css:474–476`).

> **Rule:** No inner container adds its own `padding-inline` — `--gutter-x` governs every section edge. If you change header padding or logo height, update `--header-h` to match (the arithmetic is spelled out at `general.css:263–270`).

---

## The Skewed-Block Motif (`general.css:422–472`)

The signature brand primitive. **Every card, button, image, photo, chip, and form input is a skewed block** — the brand has no flat or soft-shadowed surfaces.

`.skewed-block` base behaviour:

- White surface (`--main-bg-color`), `--main-color` border, hard offset shadow, `transform: skewX(-3deg)`.
- Direct children are **counter-skewed** `skewX(+3deg)` (`--content-skew`) so their content reads upright.
- `overflow: hidden`, `user-select: none`, `transition: var(--hover-transition-time)` (0.15s).

### Attribute API (set on the element)

| Attribute | Effect |
|---|---|
| `b-role="btn"` | Padding `--btn-padding` (`0.375em 0.75em`), `font-size: 1rem`. Uses the **btn** geometry (2px border / 4px radius / 3px shadow). |
| `b-role="block"` | Sized via `--_block-width` / `--_block-height`; raises border to **3px** and radius to **6px** via `--_adjusted-*` overrides. For cards, images, portraits. |
| `b-hoverable` | Adds `cursor: pointer` plus the hover / active states below. |

### Geometry tokens (`general.css:228–241`)

| Token | Value | px | Applies to |
|---|---|---|---|
| `--btn-border-width` | `0.125rem` | 2 | btn border |
| `--btn-border-radius` | `0.25rem` | 4 | btn radius |
| `--btn-padding` | `0.375em 0.75em` | — | btn padding |
| `--btn-shadow-shift` | `0.1875rem` | 3 | btn resting shadow offset |
| `--btn-hover-translate` | `-0.0625rem` | −1 | btn hover nudge |
| `--btn-hover-shadow-shift` | `0.25rem` | 4 | btn hover shadow offset |
| `--block-shadow-shift` | `0.3125rem` | 5 | block resting shadow offset |
| `--block-hover-translate` | `-0.0625rem` | −1 | block hover nudge |
| `--block-hover-shadow-shift` | `0.4375rem` | 7 | block hover shadow offset |
| `--block-skew` | `-3deg` | — | the X-skew on every block |
| `--content-skew` | `+3deg` | — | counter-skew on children (`calc(-1 × --block-skew)`) |
| `--hover-transition-time` | `0.15s` | — | transition duration for all block state changes |

### State behaviour (the "pressed-button-pops-up" feel)

| State | Translate | Border-radius | Shadow offset |
|---|---|---|---|
| Resting (btn) | `0` | 4px | 3px |
| Resting (block) | `0` | 6px | 5px |
| **Hover** (`b-hoverable`) | `(-1px, -1px)` | **×2** — 8px btn / 12px block | grows — 3→4 btn, 5→7 block |
| **Active** | snaps to `0` | back to base | back to base |

> **Rule:** Any new surface — card, button, image, chip, input — is a `.skewed-block`. Never introduce a flat-bordered or soft-shadowed surface. Children must counter-skew (`+3deg`) so their content reads upright. Hover always does three things at once: nudge up-left, grow the shadow, double the radius.

---

## Shadows, Borders & Radii

- **Only hard offset shadows.** Syntax is `<shift> <shift> var(--main-shadow-color)` — no blur radius, ever. `--main-shadow-color` is `#0a557ebb` (≈73%-alpha teal), **never grey**.
- No soft / elevation / blurred `box-shadow` appears anywhere in the brand. Don't add one.
- **Borders are always `var(--main-color)`.** Width is 2px for buttons, 3px for blocks / images / portraits.
- **Radii** are 4px (btn) and 6px (block) at rest; both **double on hover** (8px / 12px). Radius growth is part of the brand's tactile feedback — don't suppress it.

---

## Backgrounds, Motion & Surfaces

- **Surfaces:** the page is `--page-bg-color` (`#f7fafb`), cards are `--main-bg-color` (`#ffffff`). **Never** gradient backgrounds, never photographic backgrounds, never a colored-left-border card.
- **Body-bg tiles** (`general.css:716–768`): a `.body-bg` layer holds three hand-drawn SVG tiles (`body-bg-1/2/3.svg` — solar panels, turbines, buildings). Each renders at `--bg-opacity: 0.05`, `--bg-size: 15rem`, `z-index: -99`, and cross-fades / pans via `body-bg-pan` over `3 × --ani-time` (3 × 30s = **90s**), staggered −30s / −60s. A faint blueprint, never foreground.
- **Hover timing:** all micro-interactions use `--hover-transition-time` (`0.15s`, linear). Keep new hover transitions at 0.15s.
- **View transitions:** `@view-transition { navigation: auto }` is enabled globally (`general.css:145`) — page-to-page navigations cross-fade. Don't disable it.
- **`::selection`** (`general.css:149`): background `--selection-color` (`#0a557edd`), text `--main-bg-color` (white).
- **Custom scrollbar** (`general.css:154–165`, WebKit): `0.625rem` (10px) wide, track `#eee`, thumb `--main-color` with a `0.3125rem` (5px) radius.
- **Hero / sprite animations** are slow, looping, and restrained (turbine spin, EV roll, rain, plane fly). They never call attention to themselves — match that restraint for any new motion.

---

## Iconography

- **One icon source:** `/assets/sprite.svg`, referenced via `<use href="/assets/sprite.svg#svg-…">`. No Lucide, no Heroicons, no Font Awesome — **no inline ad-hoc SVGs, no emoji, no unicode glyphs as icons** (typographic punctuation — em-dash, mid-dot `·`, breadcrumb `/`, the literal `#` in topic tags — is text, not an icon).
- **Color convention:** filled monochrome UI / nav glyphs are `--main-color`; arrows, the quote bubble, hash, check, and paper-plane marks are `--secondary-color` (sage = the directional / micro-interaction colour). Research-field glyphs are tinted `--r-yellow` (Energy), `--r-orange` (Economics), `--r-green` (Environment).
- Each icon needs an explicit `aspect-ratio` (or fixed width / height) — see the `svg:has(use[href*="#svg-…"])` rules in `general.css`. Leaving the size flexible causes layout shift.

---

## Casing & Bilingual Pairing

- **Sentence case** for all headings, buttons, and news titles. All-caps is reserved for (a) eyebrow labels and status badges (see [`patterns.md`](./patterns.md)), and (b) at most one high-conviction CTA per page (the canonical example is `JOIN US`). Never set prose or general headings in all-caps.
- **Bilingual names** render English first, then Traditional Chinese, space-separated — `I-Yun Lisa Hsieh 謝依芸`. The paired Chinese sits at a smaller size and lower opacity (~0.55–0.6) than its English partner (see member-row rules in [`components.md`](./components.md)). Body copy is English-only; Chinese is reserved for proper names and addresses.
- **Chemistry subscripts** stay subscripts — `CO<sub>2</sub>` renders at `0.75em` / `vertical-align: text-bottom`. Never write `CO2` inline.
