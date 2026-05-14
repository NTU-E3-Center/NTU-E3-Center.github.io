# E3 Center — Typography & Design Rules

A single source of truth for fonts, sizes, weights, colors, and responsive scaling across the E3 Center website. Rules are derived by auditing every CSS file (`general.css`, `style.css`, `subpage.css`, `member.css`, `news-item.css`) and cross-checking the templates. Each rule is followed by what is already correct and where the current implementation drifts.

---

## 1. Foundations

### 1.1 Font Families

| Stack | Use | Where loaded |
|---|---|---|
| `'Outfit', 'Noto Sans TC', sans-serif` | All text, every element | `templates/base.html:54–57` (Google Fonts), `general.css:128–130` (applied via `*`) |

- **Outfit** carries Latin glyphs; **Noto Sans TC** carries Traditional Chinese glyphs. They are visually paired (geometric, even x-height).
- The universal selector forces this stack on every node — do not override per-component.

### 1.2 Brand Color Tokens (defined in `general.css:132–164`)

| Token | Value | Role |
|---|---|---|
| `--main-color` | `#0a557e` | All text. Default for every node via `* { color: var(--main-color) }`. |
| `--main-shadow-color` | `#0a557ebb` | Hard offset block-shadow color on every skewed-block (≈73%-alpha teal). See §1.8. |
| `--main-color-2` | `#4caedd` | Accent for sub-headings, secondary titles (e.g., member position). |
| `--main-color-3` | `#badcea` | Soft accent (icons, backgrounds). |
| `--secondary-color` | `#c4c691` | Olive accent — under-titles, h3 underline bar, "3E" dot. |
| `--main-bg-color` | `#ffffff` | Page surfaces. |
| `--page-bg-color` | `#f7fafb` | Subtle off-white for subpages. |
| `--r-{red,orange,yellow,green,blue,indigo,purple}` | rainbow | Status badges, category badges (news, publications). |
| `--selection-color` | `#0a557edd` | Text selection background. |

> **Rule:** All text defaults to `--main-color`. Hierarchy is expressed through **opacity** (0.4 → 0.55 → 0.7 → 1.0), not through different greys. Accent colors only for badges, decorative bars, and brand marks.

### 1.3 Font Weight Scale (`--fw-*` in `general.css:133–138`)

| Token | Value | Use |
|---|---|---|
| `--fw-h1` | `600` | h1, hero, page titles, large numeric markers (news year, breadcrumb parent) |
| `--fw-h2` | `550` | h2, contact-lead |
| `--fw-h3` | `500` | h3 |
| `--fw-body` | `500` | All body, paragraphs, default text |
| `--fw-bold` | `600` | `<b>`, `<strong>`, emphasis |

**Loaded from Google Fonts:** `Outfit:wght@500..600` and `Noto+Sans+TC:wght@500..600` only.
**Used in CSS but NOT loaded:** `300` (`.breadcrumb-sep`, `subpage.css:60`), `400` (`.contact-info-sub`, `subpage.css:1247`). These render via synthetic weight or system fallback — see §10 issue [W-1].

### 1.4 Root Font Size & Breakpoints

```css
html { font-size: 100%; }              /* 16px default */

@media (max-width: 64rem)  { :root { --gutter-x: clamp(2rem, 5vw, 4rem); ... } }   /* ≤1024px */
@media (max-width: 37.5rem){ html { font-size: 87.5%; } }                          /* ≤600px → 14px root */
```

Result: every `rem`-based size shrinks ~12.5% on mobile automatically. Component breakpoints layer additional explicit overrides on top of that.

### 1.5 The Three Responsive Viewports

| Tier | Range | Root size | Identity |
|---|---|---|---|
| **Desktop** | `> 1024px` (`> 64rem`) | 16 px | Full type scale, 80rem section max-width, side rail nav. |
| **Tablet** | `601 – 1024px` (`37.5–64rem`) | 16 px | Tighter section padding (`--section-pad-y: 6rem`), section titles −37%, member/pub list compacted. |
| **Mobile** | `≤ 600px` (`≤ 37.5rem`) | 14 px | All rem scales drop 12.5% **plus** explicit per-component shrinks. Hamburger menu, single-column grids. |

> **Rule:** Always design and test against these three exact widths: **1440 px**, **900 px**, **375 px**.

### 1.6 Layout & Spacing Tokens (`general.css:226–290`)

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

### 1.7 The Skewed-Block Motif (`general.css:422–472`)

The signature brand primitive. **Every card, button, image, photo, chip, and form input is a skewed block** — the brand has no flat or soft-shadowed surfaces.

`.skewed-block` base behaviour:

- White surface (`--main-bg-color`), `--main-color` border, hard offset shadow, `transform: skewX(-3deg)`.
- Direct children are **counter-skewed** `skewX(+3deg)` (`--content-skew`) so their content reads upright.
- `overflow: hidden`, `user-select: none`, `transition: var(--hover-transition-time)` (0.15s).

Attribute API (set on the element):

| Attribute | Effect |
|---|---|
| `b-role="btn"` | Padding `--btn-padding` (`0.375em 0.75em`), `font-size: 1rem`. Uses the **btn** geometry (2px border / 4px radius / 3px shadow). |
| `b-role="block"` | Sized via `--_block-width` / `--_block-height`; raises border to **3px** and radius to **6px** via `--_adjusted-*` overrides. For cards, images, portraits. |
| `b-hoverable` | Adds `cursor: pointer` plus the hover / active states below. |

Geometry tokens (`general.css:228–241`):

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

State behaviour (the "pressed-button-pops-up" feel):

| State | Translate | Border-radius | Shadow offset |
|---|---|---|---|
| Resting (btn) | `0` | 4px | 3px |
| Resting (block) | `0` | 6px | 5px |
| **Hover** (`b-hoverable`) | `(-1px, -1px)` | **×2** — 8px btn / 12px block | grows — 3→4 btn, 5→7 block |
| **Active** | snaps to `0` | back to base | back to base |

> **Rule:** Any new surface — card, button, image, chip, input — is a `.skewed-block`. Never introduce a flat-bordered or soft-shadowed surface. Children must counter-skew (`+3deg`) so their content reads upright. Hover always does three things at once: nudge up-left, grow the shadow, double the radius.

### 1.8 Shadows, Borders & Radii

- **Only hard offset shadows.** Syntax is `<shift> <shift> var(--main-shadow-color)` — no blur radius, ever. `--main-shadow-color` is `#0a557ebb` (≈73%-alpha teal), **never grey**.
- No soft / elevation / blurred `box-shadow` appears anywhere in the brand. Don't add one.
- **Borders are always `var(--main-color)`.** Width is 2px for buttons, 3px for blocks / images / portraits.
- **Radii** are 4px (btn) and 6px (block) at rest; both **double on hover** (8px / 12px). Radius growth is part of the brand's tactile feedback — don't suppress it.

### 1.9 Backgrounds, Motion & Surfaces

- **Surfaces:** the page is `--page-bg-color` (`#f7fafb`), cards are `--main-bg-color` (`#ffffff`). **Never** gradient backgrounds, never photographic backgrounds, never a colored-left-border card.
- **Body-bg tiles** (`general.css:716–768`): a `.body-bg` layer holds three hand-drawn SVG tiles (`body-bg-1/2/3.svg` — solar panels, turbines, buildings). Each renders at `--bg-opacity: 0.05`, `--bg-size: 15rem`, `z-index: -99`, and cross-fades / pans via `body-bg-pan` over `3 × --ani-time` (3 × 30s = **90s**), staggered −30s / −60s. A faint blueprint, never foreground.
- **Hover timing:** all micro-interactions use `--hover-transition-time` (`0.15s`, linear). Keep new hover transitions at 0.15s.
- **View transitions:** `@view-transition { navigation: auto }` is enabled globally (`general.css:145`) — page-to-page navigations cross-fade. Don't disable it.
- **`::selection`** (`general.css:149`): background `--selection-color` (`#0a557edd`), text `--main-bg-color` (white).
- **Custom scrollbar** (`general.css:154–165`, WebKit): `0.625rem` (10px) wide, track `#eee`, thumb `--main-color` with a `0.3125rem` (5px) radius.
- **Hero / sprite animations** are slow, looping, and restrained (turbine spin, EV roll, rain, plane fly). They never call attention to themselves — match that restraint for any new motion.

### 1.10 Iconography

- **One icon source:** `/assets/sprite.svg`, referenced via `<use href="/assets/sprite.svg#svg-…">`. No Lucide, no Heroicons, no Font Awesome — **no inline ad-hoc SVGs, no emoji, no unicode glyphs as icons** (typographic punctuation — em-dash, mid-dot `·`, breadcrumb `/`, the literal `#` in topic tags — is text, not an icon).
- **Color convention:** filled monochrome UI / nav glyphs are `--main-color`; arrows, the quote bubble, hash, check, and paper-plane marks are `--secondary-color` (sage = the directional / micro-interaction colour). Research-field glyphs are tinted `--r-yellow` (Energy), `--r-orange` (Economics), `--r-green` (Environment).
- Each icon needs an explicit `aspect-ratio` (or fixed width / height) — see the `svg:has(use[href*="#svg-…"])` rules in `general.css`. Leaving the size flexible causes layout shift.

### 1.11 Casing & Bilingual Pairing

- **Sentence case** for all headings, buttons, and news titles. All-caps is reserved for (a) eyebrow labels and status badges per §5.1–§5.2, and (b) at most one high-conviction CTA per page (the canonical example is `JOIN US`). Never set prose or general headings in all-caps.
- **Bilingual names** render English first, then Traditional Chinese, space-separated — `I-Yun Lisa Hsieh 謝依芸`. The paired Chinese sits at a smaller size and lower opacity (~0.55–0.6) than its English partner (see the member-row rules in §4.5). Body copy is English-only; Chinese is reserved for proper names and addresses.
- **Chemistry subscripts** stay subscripts — `CO<sub>2</sub>` renders at `0.75em` / `vertical-align: text-bottom`. Never write `CO2` inline.

---

## 2. The Type Scale

All values are in `rem` (relative to the root above). Where a cell shows two values separated by `→`, the first applies via the explicit per-component override, the second via root scaling alone.

### 2.1 Document-level Headings (`general.css:65–84`)

| Element | Desktop | Tablet | Mobile | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|---|---|
| `h1` (base) | **3.5 rem / 56 px** | 3.5 rem / 56 px | 3.5 rem / **49 px** (via root) | 600 | 1.10 | −0.03em |
| `h2` (base) | **2.25 rem / 36 px** | 2.25 rem | 2.25 rem / 31.5 px | 550 | 1.15 | −0.025em |
| `h3` (base) | **1.75 rem / 28 px** | **1.25 rem** (style.css:2200) | **1.125 rem** (style.css:2387) | 500 | 1.20 | −0.02em |

> Note: there is no `h4`/`h5`/`h6` base rule. They appear only inside the news article body (§4.6).

### 2.2 Visual Type Scale (a single, authoritative ladder)

Use this ladder when introducing new typography. Numbers below are the **desktop** size; multiply by 0.7 for tablet and 0.55–0.7 for mobile (see per-component tables in §4 for exact mobile overrides).

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

## 3. Color & Emphasis Rules

### 3.1 Text Emphasis Ladder

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

### 3.2 Accent Color Use

| Color | Use only for |
|---|---|
| `--main-color-2` (#4caedd) | Member-row primary position line (`.mem-row-position p:first-child`) |
| `--secondary-color` (#c4c691) | h3 decorative underline bar (`general.css:498–512`), homepage "3E" dot, section-subtitle icons |
| `--r-green` etc. | Status / category badges only |

---

## 4. Page & Component Rules

### 4.1 Homepage Hero (`templates/home/home.html` + `style.css:48–101`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `#home .hp-title h1` | 3 rem | 3 rem | 2.25 rem |
| `#home .hp-title span` (subtitle) | 1 rem | 1 rem | 1 rem |
| `#home .hp-3e p` ("3E" marker) | 1.5 rem | 1.5 rem | 1.25 rem |
| `.hp-plane-text` | 1.375 rem | — | — |
| `.hp-scroll-for-more`, `.hp-last-update` | 0.75 rem | — | — |

### 4.2 Section Titles (`style.css:437–495`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.section-title h2` | **4 rem** | 2.5 rem | 2 rem |
| `.section-subtitle > *` | 1.25 rem | 1.25 rem | 1.25 rem |
| h3 (inside section, with secondary underline bar) | 1.75 rem | 1.25 rem | 1.125 rem |

Weight: `--fw-h1` (600). Letter-spacing: −0.03em. The hover underline animation on `.section-title-link` is shared across "View all members / publications / news / photos".

### 4.3 Subpage Header (`partials/subpage-header.html` + `subpage.css:42–135`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.breadcrumb-parent` (link back) | 2.75 rem | 1.75 rem | 1.125 rem |
| `.breadcrumb-sep` (`/`) | 2.75 rem (weight 300, opacity 0.25) | 1.75 rem | 1.125 rem |
| `.breadcrumb-current` (this page) | 1.375 rem (opacity 0.5) | 1.0625 rem | 0.8125 rem |

### 4.4 Publications — Display Method (`style.css:1689–1799`, `subpage.css:1032–1058`, `templates/pages/publications.html`)

A publication row uses a **3-column horizontal layout**: date (left), title + meta (center), keyword chips (right).

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.publi-date` (mm/yy stacked) | 1.0625 rem | 0.75 rem | — |
| `.publi-title` | **1.5 rem** (`--_font-size-l`) | 1.25 rem | 1.0625 rem |
| `.publi-subtitle` (journal name) | 1.0625 rem (`--_font-size-s`) | 0.75 rem | — |
| `.publi-row-authors` | 0.9375 rem, opacity 0.55, line-height 1.4 | — | — |
| `.publi-row-journal` | 0.8125 rem, opacity 0.5 | — | — |
| `.pub-keyword-chip` | 0.75 rem | — | — |
| `.publi-status-badge` (under-review etc.) | **0.625 rem**, weight 600, uppercase, letter-spacing 0.1em | — | — |
| `.publi-group-title` (eyebrow: "Working Papers", "Books") | 0.6875 rem, weight 600, uppercase, letter-spacing 0.14em, opacity 0.4 | — | — |
| `.publi-show-more` button | 0.875 rem, weight 600 | — | 0.75 rem |

> **Rule:** Publication titles use `text-transform: capitalize` only on member-profile pages (`member.css:343` `.pub-title`). On homepage and `/publications/`, the original casing is preserved.
> **Rule:** Status badges color-code by `data-status` and use a fixed letter-spacing of `0.1em` (uppercase). Reuse the same badge style for any new lifecycle state.

### 4.5 Members

#### 4.5.1 Members on Homepage (`style.css:1062–1192`)

Three card sizes (Leader / Medium / Small):

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.EngName` (leader) | 1.75 rem | 1.25 rem | 1.125 rem |
| `.ChiName` (leader) | 1.25 rem | 1 rem | 0.875 rem |
| `.mem-name-en` (medium) | 1.7 rem | 1.25 rem | 1 rem |
| `.mem-name-zh` (medium) | 1 rem | 0.875 rem | 0.75 rem |
| `.mem-name` (small) | 1.5 rem | — | — |
| `.mem-name span` (small) | 1 rem | — | — |

#### 4.5.2 Members Subpage (`subpage.css:163–489`, `templates/pages/members.html`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.mem-group-title` (eyebrow) | 0.6875 rem, uppercase, 0.14em, opacity 0.4 | — | — |
| `.mem-row-en` (name) | 2.25 rem, weight 600, −0.025em | 1.75 rem | 1.25 rem |
| `.mem-row-zh` (name) | 1.25 rem, weight 500, opacity 0.45 | 1 rem | 0.875 rem |
| `.mem-row-position` first line | 1.0625 rem, weight 600, color `--main-color-2` | — | 0.875 rem |
| `.mem-row-position` other lines | 1 rem, opacity 0.55 | — | 0.8125 rem |
| `.mem-row-tag` | 0.8125 rem | — | — |
| **PI featured row** `.mem-group--pi .mem-row-en` | **2.75 rem**, −0.03em | 2 rem | 1.5 rem |
| **PI featured row** `.mem-group--pi .mem-row-zh` | 1.375 rem, opacity 0.5 | 1.125 rem | 1 rem |
| `.mem-alum-en` (alumni grid) | 1 rem, weight 600 | — | 0.875 rem |
| `.mem-alum-zh` | 0.8125 rem, opacity 0.5 | — | 0.75 rem |

#### 4.5.3 Member Profile Page (`member.css`, `templates/pages/member/member.html`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.main-name h1` | 2.75 rem | — | 1.875 rem |
| `.sub-name` (Chinese name) | 1.5 rem, opacity 0.7 | — | 1.125 rem |
| `.position-text` | 1.25 rem | — | 1 rem |
| `h2` (About / Research / Publications) | 2.25 rem, weight 550 | — | 1.625 rem |
| `#about .content p`, `li` | 1.25 rem, line-height 1.55, justify | — | 1 rem |
| `.res-tag` (research interest tag) | 1.5 rem | — | 1.125 rem |
| `.res-info-minor` | 1 rem | — | 0.875 rem |
| `.list-block .list-title` | 1.25 rem | — | 1 rem |
| Publication `--_font-size-l` (title) | 1.5 rem | — | 1 rem |
| Publication `--_font-size-s` (date, journal) | 1 rem | — | 0.8125 rem |
| `.pub-show-all-btn` | 0.9375 rem | — | 0.8125 rem |

### 4.6 News

#### 4.6.1 News Rows (homepage `/news/` and subpage `subpage.css:646–751`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.news-row-mm` (month) | 0.8125 rem, weight 600, opacity 0.45 | 0.75 rem | 0.625 rem |
| `.news-row-yy` (year) | 1.375 rem, `--fw-h1`, −0.025em | 1.125 rem | 0.9375 rem |
| `.news-row-title` | 1.125 rem, line-height 1.5 | 1 rem | 0.875 rem |
| `.news-row-badge` (category) | **0.625 rem**, weight 600, uppercase, 0.1em | — | **0.5625 rem** |
| `.news-cat-title` (eyebrow) | 0.6875 rem, uppercase, 0.14em, opacity 0.4 | — | — |
| `.news-filter-tab` | 0.875 rem, weight 600 | 0.8125 rem | 0.75 rem |

#### 4.6.2 News Article Page (`news-item.css`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.news-item-category` (eyebrow) | 0.6875 rem, uppercase, 0.14em, opacity 0.4 | — | 0.625 rem |
| `.news-item-title` (h1) | `clamp(1.75rem, 4vw, 2.75rem)` | 1.625 rem | 1.375 rem |
| `.news-item-date-mm` | 0.9375 rem, opacity 0.7 | — | 0.75 rem |
| `.news-item-date-yy` | 1.5 rem, `--fw-h1`, −0.025em | — | 1.125 rem |
| `.news-item-body` (paragraph) | **1.25 rem**, line-height **1.70** | — | 1 rem, line-height 1.6 |
| `.news-item-body h2` | 1.875 rem | — | 1.375 rem |
| `.news-item-body h3` | 1.5 rem | — | 1.125 rem |
| `.news-item-body h4` | 1.25 rem | — | 1 rem |
| `.news-item-body h5` | 1.0625 rem (opacity 0.85) | — | 0.9375 rem |
| `.news-item-body h6` | 0.9375 rem, uppercase, 0.06em, opacity 0.5 | — | 0.8125 rem |
| `.news-item-placeholder` | 1.25 rem, italic, opacity 0.35 | — | 1 rem |

> **Rule:** Within `.news-item-body`, all heading levels are rendered at `var(--fw-h1)` (600) — this is intentional editorial gravitas. Maintain it for any new content blocks.

### 4.7 Contact Page (`subpage.css:1112–1421`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.contact-lead` (the `<h2>`) | 2.75 rem, `--fw-h1` | — | 1.875 rem |
| `.contact-tagline` | 1.125 rem, line-height 1.65 | — | 1 rem |
| `.contact-info-label` | 0.6875 rem, uppercase, 0.16em, opacity 0.5 | — | — |
| `.contact-info-value` | 1.0625 rem, weight 600 | — | 0.875 rem (weight 500, no-wrap) |
| `.contact-info-sub` | 0.8125 rem, weight 400, opacity 0.6 | — | — |
| `.contact-field label` | 0.75 rem, weight 600, uppercase, 0.12em, opacity 0.55 | — | — |
| `.contact-field input/textarea` | 1.0625 rem | — | — |

### 4.8 Group Life (`style.css:1866–1924`, `templates/pages/group-life.html`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.glf-slider-num` | 1.25 rem, centered | 1.125 rem | — |
| `.glf-slider-text` (caption) | 1.25 rem, centered | 1.125 rem | derived from grid width |

### 4.9 Footer (`style.css:614–649`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.ftr-link` | 1.25 rem | — | 0.9375 rem |
| `.ftr-info` | inherited | — | 0.8125 rem |

### 4.10 Menu / Navigation (`style.css:744–820`)

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.menu-btn` label | 1.125 rem | — | — |
| `.menu-a` (item) | 1.25 rem | — | `clamp(0.875rem, 2.2dvh, 1rem)` |
| `.nav-l a span` (side rail) | 1.25 rem (hover 1.5 rem) | — | — |

---

## 5. Reusable Pattern Rules

### 5.1 Eyebrow Label

A category/group label that sits above a row. Uniform shape:

```
font-size: 0.6875rem
font-weight: 600
text-transform: uppercase
letter-spacing: 0.14em (use 0.16em only for contact info)
color: var(--main-color)
opacity: 0.4
```

Used by `.mem-group-title`, `.news-cat-title`, `.publi-group-title`, `.news-item-category`. **New label-style text must adopt this exact recipe** — see issue [E-1] for the one place it drifts.

### 5.2 Status / Category Badge

```
font-size: 0.625rem
font-weight: 600
text-transform: uppercase
letter-spacing: 0.1em
padding: 0.15rem 0.55rem
line-height: 1.6
color: status-specific (var(--r-*))
```

Used by `.publi-status-badge` and `.news-row-badge`. On mobile shrink the font to **0.5625 rem**.

### 5.3 Date / Number Marker

For year-as-anchor (publication year, news year, member-row year):

```
font-size: 1.375rem (news/breadcrumb) | 1.5rem (news-item hero) | 1.0625rem (publication compact)
font-weight: var(--fw-h1) (600)
letter-spacing: -0.025em
color: var(--main-color)   /* full opacity */
```

The accompanying month uses ~0.6× the year's size, weight 600, opacity 0.45–0.7.

### 5.4 List Item Title (rows in News, Publications, Members)

Item-level "titles" are **not** semantic `<h*>` tags — they live inside rows. Treat them as a tier between Body-L and Heading-S:

| List type | Title rem (desktop) | Class |
|---|---|---|
| News row | 1.125 rem | `.news-row-title` |
| Publication row | 1.5 rem | `.publi-title` |
| Member row (name) | 2.25 rem | `.mem-row-en` |

The 2× spread between news and member is intentional — member rows are page-defining, news rows are dense.

### 5.5 Section Title with View-all Link

Always render as `<h2>` wrapped in `.section-title-link`. The hover state animates the trailing underline; do not introduce a separate "View all" pill — reuse `.section-cta-btn` (1.125 rem desktop / 1 rem on small) at the bottom of the section.

---

## 6. Responsive Scaling — Three Versions

### 6.1 Mobile (`≤ 600 px`, root 14 px)

Triggers:
- `html { font-size: 87.5% }` → every rem auto-shrinks 12.5%
- Per-component overrides under `@media (max-width: 37.5rem)`
- Layouts collapse to single column; hamburger replaces side rail
- Hero h1: 2.25 rem; section titles: 2 rem; body article: 1 rem; eyebrow: 0.625 rem
- Minimum readable size on mobile = **0.75 rem (10.5 px)**. Anything smaller (e.g. `.news-row-badge` at 0.5625 rem ≈ 7.9 px) is borderline — see [A-1].

### 6.2 Tablet (`601 – 1024 px`, root 16 px)

Triggers:
- Per-component overrides under `@media (max-width: 64rem)`
- Section titles: 4 rem → 2.5 rem; h3: 1.75 → 1.25 rem; member-row name: 2.25 → 1.75 rem
- Gutters tighten (`--gutter-x: clamp(2rem, 5vw, 4rem)`)
- Layout still grid-based; menu still hamburger / left-rail depending on element

### 6.3 Desktop (`> 1024 px`, root 16 px)

- Full type scale as listed in §2
- Section gutter clamped at 6 rem (`--gutter-x` ceiling); section max-width 80 rem
- Left rail navigation visible on homepage
- `--header-h: 7.25rem`

### 6.4 The Single Rule for New Components

Define the **desktop** values directly. Add **only** tablet/mobile overrides where the auto-scale (12.5%) is insufficient. Most body text needs **no** explicit overrides; titles and large display sizes almost always do.

---

## 7. Heading Hierarchy & Semantic Rules

| Page | Should have one h1 | Currently has h1 |
|---|---|---|
| `/` (homepage) | yes — "E3 Center …" | yes (`#home .hp-title h1`) |
| `/members/` | yes | **no** — first heading is `<h3>` per group |
| `/publications/` | yes | **no** — first heading is `<h3>` per group |
| `/news/` | yes | **no** — categories are `<h2>` inside hidden `<div>`s |
| `/group-life/` | yes | **no** |
| `/contact/` | yes | **no** — `Get in touch` is `<h2 class="contact-lead">` |
| `/members/{id}/` | yes | yes (`.main-name h1`) |
| `/news/{slug}/` | yes | yes (`.news-item-title` h1) |

> **Rule:** Every page MUST contain exactly one `<h1>`. Section groupings inside subpages should be `<h2>`; sub-groupings `<h3>`. See [S-1] – [S-3] for fixes.

---

## 8. Line-Height & Letter-Spacing Conventions

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

---

## 9. Accessibility Floor

- Body text contrast: `#0a557e` on `#ffffff` = ~7.2:1. Passes WCAG AAA.
- Text dimmed to **opacity 0.45 or below** on white drops to ~3.2:1 — **below WCAG AA 4.5:1** for body. Allowed only for *decorative* text (separators, placeholders, eyebrow labels ≤ Body-S). See [A-2].
- Smallest acceptable mobile size: **0.75 rem (10.5 px)**. Badges at 0.5625 rem violate this.
- Minimum tap target: 44×44 px — preserved by current padding on filter tabs and CTA buttons. Do not shrink padding below `0.3rem 0.875rem` on mobile.

---

## 10. Findings — Status

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
- **[W-2] [L] 🟡** News-article body forces every heading (h2–h6) to `var(--fw-h1)`. Intentional editorial gravitas — documented in §4.6.

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
- **[I-2] [L] 🟡** `.publi-title` (1.5 rem) and `.news-row-title` (1.125 rem) differ by 33%. Intentional emphasis on research output — documented in §5.4.

### Scaling Strategy

- **[R-1] [L] 🟡** Only `.news-item-title` uses `clamp()`. Rule for new components: prefer `clamp(min, vw, max)` over three breakpoint overrides for hero-tier text. Captured in §6.4.
- **[R-2] [L] 🟡** Tablet (`@64rem`) does not scale the root. Verify each new component at 900 px width. Captured in §6.4.

### House-keeping

- **[K-1] [L] ✅** `--fs-*` design tokens declared in `general.css :root` (additive — Display-XL/L/M/S, Heading-L/M/S, Body-XL/L/Body/Base/S, Caption/-S, Eyebrow, Badge). Existing CSS still uses hard-coded rem; new CSS should reach for these tokens first.
- **[K-2] [L] ✅** `.text-eyebrow` and `.text-badge` utility classes added in `general.css`. Existing classes retain their own declarations for backward compat — new label/badge UI should use the utilities.

---

## 11. Quick Checklist for New Components

When introducing a new piece of UI:

1. **Pick a tier** from §2.2 — don't invent a new size.
2. **Default color** to `var(--main-color)` and adjust emphasis with opacity from §3.1.
3. **Pick line-height & letter-spacing** from §8 based on context (display / body / uppercase).
4. **Add tablet/mobile overrides** only if the auto-scale (root 87.5%) leaves the size outside the intended tier on that viewport.
5. **Semantics**: if it's a page title, make it `<h1>`. If it's a section, `<h2>`. If it's a row's title, leave it as a `<p>`/`<div>` styled to a tier — do not use `<h4>`–`<h6>` for repeating list items.
6. **Check at 1440 / 900 / 375 px**. If any size lands below 0.75 rem at 375 px, redesign.
7. **Is it a surface?** Cards, buttons, images, chips, and inputs must be `.skewed-block`s — −3° skew, hard offset shadow, counter-skewed children, radius-doubling hover. See §1.7. Never add a flat or soft-shadowed surface.
