# Responsive Scaling

Part of [DESIGN_RULES/](./README.md). Covers root font size, breakpoints, the three viewports, and the strategy for new components.

---

## Root Font Size & Breakpoints

```css
html { font-size: 100%; }              /* 16px default */

@media (max-width: 64rem)  { :root { --gutter-x: clamp(2rem, 5vw, 4rem); ... } }   /* ≤1024px */
@media (max-width: 37.5rem){ html { font-size: 87.5%; } }                          /* ≤600px → 14px root */
```

Result: every `rem`-based size shrinks ~12.5% on mobile automatically. Component breakpoints layer additional explicit overrides on top of that.

---

## The Three Responsive Viewports

| Tier | Range | Root size | Identity |
|---|---|---|---|
| **Desktop** | `> 1024px` (`> 64rem`) | 16 px | Full type scale, 80rem section max-width, side rail nav. |
| **Tablet** | `601 – 1024px` (`37.5–64rem`) | 16 px | Tighter section padding (`--section-pad-y: 6rem`), section titles −37%, member/pub list compacted. |
| **Mobile** | `≤ 600px` (`≤ 37.5rem`) | 14 px | All rem scales drop 12.5% **plus** explicit per-component shrinks. Hamburger menu, single-column grids. |

> **Rule:** Always design and test against these three exact widths: **1440 px**, **900 px**, **375 px**.

---

## Mobile (`≤ 600 px`, root 14 px)

Triggers:

- `html { font-size: 87.5% }` → every rem auto-shrinks 12.5%
- Per-component overrides under `@media (max-width: 37.5rem)`
- Layouts collapse to single column; hamburger replaces side rail
- Hero h1: 2.25 rem; section titles: 2 rem; body article: 1 rem; eyebrow: 0.625 rem
- Minimum readable size on mobile = **0.75 rem (10.5 px)**. Anything smaller (e.g. `.news-row-badge` at 0.5625 rem ≈ 7.9 px) is borderline — see findings [A-1] in [`README.md`](./README.md).

## Tablet (`601 – 1024 px`, root 16 px)

Triggers:

- Per-component overrides under `@media (max-width: 64rem)`
- Section titles: 4 rem → 2.5 rem; h3: 1.75 → 1.25 rem; member-row name: 2.25 → 1.75 rem
- Gutters tighten (`--gutter-x: clamp(2rem, 5vw, 4rem)`)
- Layout still grid-based; menu still hamburger / left-rail depending on element
- Tablet does **not** scale the root — verify each new component at 900 px (finding [R-2]).

## Desktop (`> 1024 px`, root 16 px)

- Full type scale as listed in [`typography.md`](./typography.md)
- Section gutter clamped at 6 rem (`--gutter-x` ceiling); section max-width 80 rem
- Left rail navigation visible on homepage
- `--header-h: 7.25rem`

---

## The Single Rule for New Components

Define the **desktop** values directly. Add **only** tablet/mobile overrides where the auto-scale (12.5%) is insufficient. Most body text needs **no** explicit overrides; titles and large display sizes almost always do.

> **Rule:** Prefer `clamp(min, vw, max)` over three breakpoint overrides for hero-tier text (the news-item `h1` is the reference implementation). See finding [R-1].
