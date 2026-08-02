# Responsive Scaling

Part of [DESIGN_RULES/](./README.md). Root font size, the four viewport tiers, the
large-screen policy, and the strategy for new components.

---

## The mechanism: tokens re-declare per tier

Two levers produce every responsive size — there is no third:

```css
html { font-size: 100%; }                    /* 16px default */
@media (max-width: 37.5rem) { html { font-size: 87.5%; } }   /* phone → 14px root */
```

plus `:root` re-declarations of the type-scale tokens (`--fs-*`) and layout tokens
(`--gutter-x`, `--section-pad-y`, `--header-h`, …) inside each tier's media query in
`general.css`. Components consume tokens, so they scale without per-component overrides —
that is what makes the one-size-per-role invariant ([typography.md](./typography.md)
§ Content Roles) hold at every width.

## The Four Viewport Tiers

| Tier | Range | Root | What changes |
|---|---|---|---|
| **Phone** | ≤ 600px (`≤ 37.5rem`) | 14 px | Root drops 12.5%; `:root` re-declares HEADING/CONTENT tokens down and **bumps the LABEL group up** (`--fs-eyebrow` 0.8125, `--fs-badge` 0.75) to clear the WCAG floor. Single column, hamburger drawer, `--header-h: 2.75rem`. |
| **Tablet** | 601–1024px (`37.5–64rem`) | 16 px | Root does **not** scale ([R-2]) — the token re-declare carries it: `--fs-h1` 2.5, `--fs-h2` 2, `--fs-h3` 1.625, `--fs-lede` 1.25, `--fs-body` 1.0625; gutters tighten, `--section-pad-y: 6rem`, `--header-h: 4.5rem`. Drawer nav. |
| **Laptop / desktop** | 1025–1439px (`64–90rem`) | 16 px | The base ladder as written in `:root`. Inline header nav from `64.0625rem`. `--header-h: 5.5rem`. |
| **Wide** | ≥ 1440px (`≥ 90rem`) | 16 px | Editorial bump for greater viewing distance (`general.css` § wide tier): `--fs-h1` 3.25, `--fs-lede` 1.5, `--fs-body` 1.1875. LABEL group stays constant. Matches Medium/NYT-scale wide-display body sizes. |

## Large screens: content caps, whitespace grows (policy)

On HD/2K/4K displays the page does **not** keep widening. Sections cap at `80rem` with
`--gutter-x` clamped at 6rem — content area ≈1120px on every screen ≥1440px wide; homepage
sections cap at `120rem` (`--_home-max-width`). The wide tier adjusts *type*, not *measure*.

This is deliberate: capped measure keeps prose readable and the notebook identity intact
([brand.md](./brand.md)); a 2560px viewport frames the page in paper margin rather than
stretching it. If wide screens ever feel under-used, the sanctioned levers are the wide
tier's `:root` block (gutter ceiling, section max-width) — a rules change per
[extending.md](./extending.md), not per-component widening.

## Component-local breakpoints

The four tiers govern tokens; a component may additionally break where **its own content**
demands it, in `rem`, with a comment in the CSS explaining the trigger. Current registry:

| Breakpoint | Where | Why |
|---|---|---|
| `56rem` | publication & project detail | two-column layout stacks; metadata card moves above prose |
| `48rem` | subpage search/list chrome (`subpage.css`) | input/toolbar arrangement |
| `64.0625rem` (min) | header (`general.css`) | inline nav appears; drawer trigger hides |

Don't add a component-local breakpoint to resize *text* — that's the tokens' job.

## Testing rule

Design and test at **five widths: 375 / 768 / 1024 / 1440 / 1920** — one inside each tier
plus both edges of the tablet range — and spot-check 2560 for the whitespace framing.
(375 and 1024 sit *on* tier boundaries deliberately: off-by-one media-query bugs show up
there.) If any text lands below 0.75rem at 375px, redesign.

## The rule for new components

Define **desktop** values via tokens. Add tablet/phone overrides **only** where the token
re-declare plus the 87.5% root leaves the component outside its intended role — most body
text needs none; display-scale text usually does. Prefer `clamp(min, vw, max)` with token
endpoints over three breakpoint overrides for hero-tier text (`.news-item-title` is the
reference; [R-1]). Never restate LABEL-group sizes in rem — reference the tokens so the
phone bump applies ([A-1]).
