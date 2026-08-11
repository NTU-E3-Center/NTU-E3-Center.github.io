# E3 Center — Brand Foundation

**Date:** 2026-08-11
**Branch:** `rebrand/brand-foundation`, cut from `design/minimal-refresh` rather than `source`, so
the layout work that carries forward is already in the base (see § Prior work)
**Status:** Draft — pending user review
**Topic:** Sub-project 1 of 5 — the platform-neutral identity layer

Spec location follows the convention set by [2026-07-24-brand-refinement-design.md](./2026-07-24-brand-refinement-design.md):
`docs/` is build output (gitignored, `shutil.rmtree`'d by `build.py` on every run), so specs
live in `specs/`.

**Every contrast figure in this document was computed, not estimated** — WCAG relative
luminance against `--paper`, via the derivation scripts described in § Palette.

---

## Goal

Give E3 Center a brand and a design system that is **platform-neutral**, so the website
becomes its first consumer rather than its definition. Today the identity is defined by
`static/css/general.css :root` — which cannot be compiled into a slide theme or a print
swatch book, so every non-web surface hand-copies hex values and drifts.

## What changed, and why this is not the original task

This work began as "make the site cleaner and more minimal" and ran as visual iteration on
`design/minimal-refresh` (10 commits). Two inputs changed the task:

1. **The director's read.** Lisa Hsieh: 太可愛了 ("too cute") and 目前的前端設計也看不出來淨零智慧城市
   ("the current frontend doesn't show net-zero smart city"). The first puts the illustrated
   identity in play; the second is a requirement the refresh never had.
2. **The decision to rebrand.** Rather than refresh within `DESIGN_RULES/`, build a new system
   that also serves slides and print.

> **Governance.** Lisa's 按照你們的想法 authorises adjusting the website. A centre-wide rebrand is
> normally a director-level sign-off. This spec should be shown to her before implementation
> begins, not after.

## Scope — this spec is 1 of 5

| # | Sub-project | Status |
|---|---|---|
| **1** | **Brand foundation** — concept, palette, type, imagery, motion, voice | **this spec** |
| 2 | Token architecture — neutral source + per-platform emitters | next |
| 3 | Component system — web components on the tokens | after 2 |
| 4 | Website redesign — all 13 page types | after 3 |
| 5 | Non-web surfaces — slide theme, poster, print | parallel with 3 |

**Target platforms** (user-selected): website, slides/presentations, posters & print.
Paper figures (matplotlib/ggplot) were considered and **excluded** — noted here because the
token source makes adding them later cheap, and for a centre that publishes constantly it
remains the highest-value future target.

---

## Fixed input: the logo does not change

`e3-center-logo-inline.svg`, `e3-logo-icon.svg` and the `#svg-e3-logo` sprite symbol are
unchanged. The mark therefore stops being decoration and becomes the **specification**.

The mark is three ribbons woven into a hexagonal knot — Energy × Economics × Environment,
interlocking. Two consequences the old system never exploited:

- **Its geometry is isometric line-work.** Technical, axonometric drawing is the logo's own
  visual language, not a borrowed one.
- **It contains seven colours.** The old site palette shared exactly one of them (`#0a557e`),
  and only on the wordmark. The mark was olive/sage/moss/teal; the site was navy/cyan. They
  read as two organisations.

---

## Concept

**Three strands, woven.** Energy, Economics and Environment are not three topics side by side —
they are interdependent, which is the centre's actual argument and the mark's actual geometry.
The system expresses this through interlocking structure, isometric technical drawing, and
field coding taken from the ribbons themselves.

This replaces "a working engineer's notebook." That concept produced a *friendly* register —
hand-drawn cartoon objects — which is precisely what the director flagged.

**Register:** credible engineering first, approachable lab second, never marketing.

---

## Palette

Derived entirely from the mark. Every colour in the logo has exactly one job; nothing is
invented and nothing is left over.

`--paper` = **`#faf9f8`** (warmth +2, where warmth = R − B). Selected from a seven-step ramp.
It removes the blue cast of the old `#f7fafb` without reading as cream. Ink legibility is
effectively constant across that whole ramp (7.66:1 → 7.30:1), so this was an aesthetic call
with no accessibility cost.

### Semantic tokens

| Token | Value | On paper | Source | Role |
|---|---|---|---|---|
| `--paper` | `#faf9f8` | — | chosen | Page / slide background; print stock reference |
| `--surface` | `#eeeede` | — | `#d3d6a3` @ 30% | Tinted band, cards |
| `--line` | `#ced8d9` | — | `#aabdbf` @ 55% | Hairlines, dividers, table rules |
| `--muted` | `#2e6e90` | **5.33:1** | ink @ 85% over paper | Secondary text |
| `--ink` | `#0a557e` | **7.64:1** | **the wordmark's own navy** | All primary text |
| `--structure` | `#1f5979` | **7.23:1** | mark | Rules, chart axes, header |
| `--accent` | `#237a74` | **4.86:1** | mark, exact | Links, active states |

`--ink` is the colour the wordmark "E3 Center" is already set in, so body copy and the lockup
are literally the same navy and the logo sits on the page natively.

### Field coding — the three ribbons

Each ribbon ships as a pair: the mark's own value for fills, charts and graphics, and a
**computed** text-safe sibling. The sibling is the hue walked down in lightness by script
until it clears 5.0:1 — headroom above the AA line rather than sitting on it.

| Field | Graphic | On paper | Text | On paper |
|---|---|---|---|---|
| Energy | `#aab157` | 2.18:1 | `#6a6f33` | **5.08:1** |
| Environment | `#bfceaa` | 1.58:1 | `#5d7041` | **5.17:1** |
| Economics | `#aabdbf` | 1.86:1 | `#556e71` | **5.18:1** |

> **Superseded.** An earlier draft said this "retires the `--r-yellow / --r-orange / --r-green`
> field coding" so that "field colour stops being an invention and becomes the mark." That was
> wrong and has been reversed. The three E's keep the vivid trio — yellow, orange, green.
>
> The mark's seven colours sit within roughly 40° of each other, so moss / sage / grey-blue are
> markedly harder to tell apart as *field codes* than yellow / orange / green. This is the same
> conclusion the category badges reached: **the mark supplies identity, not distinguishability.**
> Where a colour's job is to be recognised as E3, it comes from the mark; where its job is to be
> told apart from four siblings at badge size, it doesn't.
>
> The ribbon hues still serve `--marker` and the two badge anchors that need them.

**`--accent` is exempt from the 5.0 target.** Raising it would nudge `#237a74` to `#227670` — a
2-unit, invisible shift that would cost the palette its claim to be exactly the mark's colours.
It clears AA at 4.86:1 as-is.

### Governing principle

**Accessible by construction, not by audit.** The old system wrote colours by hand and checked
them afterwards with `validate_design_tokens.py`. Here the text variants are *generated* against
a contrast target, so the system cannot emit a failing text colour.

### The emphasis ladder is replaced

`DESIGN_RULES/color.md` defines opacity levels Secondary `0.7`, Muted `0.55`, Subtle `0.45–0.5`,
Eyebrow `0.4`. Measured against `--paper`, **these fail WCAG AA at body size**:

| Ladder level | Opacity | Measured | Verdict |
|---|---|---|---|
| Secondary | 0.70 | 3.77:1 | fails AA |
| — | 0.75 | 4.23:1 | fails AA |
| — | 0.80 | 4.74:1 | passes |
| — | 0.85 | 5.33:1 | passes |

**New rule:** the opacity ladder's usable range for text at body size is **0.80–1.00**. Below
0.80, ink may be used only for non-text decoration (rules, glyphs, dividers). Two named steps
replace six: `--ink` (1.0) and `--muted` (0.85). Anything dimmer is not text.

This also closes a gap the old rules left open: the ladder was paper-calibrated and had no
tint-aware variant, so metadata on a tinted band could land far below AA.

---

## Typography

**Families are unchanged: Outfit + Noto Sans TC.** (User decision: type direction A.)

> **Carried constraint.** Outfit is a *geometric* sans, and geometric sans is a real contributor
> to the friendliness the director flagged. Keeping it means the de-cuteing must be won entirely
> by **layout, colour and imagery**. Nothing at the type layer will help. Every later decision in
> this system inherits that constraint.

### Scale — rebuilt

With weight unable to carry hierarchy (Outfit's range is narrow and heavy weights read
cartoonish), hierarchy comes from **size and space**. The top of the scale widens for editorial
authority; the middle compresses so h3 stops competing with h2.

| Role | Token | Desktop | Line-height | Tracking |
|---|---|---|---|---|
| Display / h1 | `--fs-display` | 3.5rem / 56px | 1.05 | −0.03em |
| h2 | `--fs-h2` | 2rem / 32px | 1.15 | −0.025em |
| h3 | `--fs-h3` | 1.5rem / 24px | 1.25 | −0.015em |
| Lede | `--fs-lede` | 1.25rem / 20px | 1.50 | 0 |
| Body | `--fs-body` | 1.0625rem / 17px | 1.65 | 0 |
| Small | `--fs-small` | 0.9375rem / 15px | 1.55 | 0 |
| Meta | `--fs-meta` | 0.8125rem / 13px | 1.45 | 0 |
| Eyebrow | `--fs-eyebrow` | 0.6875rem / 11px | 1.2 | 0.14em |

Old scale for comparison: 48 / 36 / 28 / 22 / 18 / 16. The h1→h2 jump goes from 1.33× to 1.75×;
h3 drops from 28px to 24px.

**Weights:** 400 light (Zh subtitles, de-emphasis), 450 body, 500 display, 600 small UI only.
Size carries hierarchy; weight only whispers.

**Chinese:** Noto Sans TC at the same sizes, line-height +0.10 over the Latin value. CJK needs
more leading at equal size.

**Measure:** 66ch maximum for prose; 56rem for list/row content (carried from the branch, where
it tested well).

---

## Spacing, radii, motion

**Spacing** — 4px base, geometric: `4, 8, 12, 16, 24, 32, 48, 64, 96, 128`. Section rhythm on
the landing page uses 96 desktop / 64 tablet / 48 phone.

**Radii** — **2px, and only 2px.** Plus `0` for full-bleed. Carried from the branch, where
flattening was the change that worked. No pills, no large radii.

**Skew is retired as a system-wide motif.** It survives on at most **one** CTA per page. The
`.menu-btn` currently carries `skewed-block` on every page and must be flattened — it is the
main violation of the one-per-page rule today.

**Motion** — 150ms micro-interactions, 300ms state transitions, ambient loops ≥ 6s. All motion
sits behind `prefers-reduced-motion: reduce`. Motion shows the subject's world operating; it
never performs for attention.

---

## Imagery doctrine

1. **Subject matter is never a cartoon icon.** Reference institutions (Ember, Agora, MIT
   Senseable, ETH D-BAUG) signal their field through photography, data, or their own research
   output — none through decorative illustration.
2. **Drawn material is technical.** Single-weight line, isometric where depth is needed,
   matching the mark's own geometry. No faces, no rounded cartoon volumes, no colour fills
   where an outline will do.
3. **The research output is the imagery.** Charts, figures and real numbers carry the subject.
   This is also what answers 看不出來淨零智慧城市 most cheaply — recent publication titles
   (decarbonization, carbon pricing equity, air-quality policy) state the field without a
   picture of it.
4. **Portraits are unframed** — no skew, no border, `object-fit: cover`, 2px radius.
5. **No photographic page backgrounds and no gradients.** Full-bleed video heroes are excluded:
   generic, and they invert the page's colour logic.

### Hero — carried forward, flagged

The existing hand-drawn hero is **retained** (user decision). It already depicts Taipei 101,
Nanshan A21, Fubon A25, rooftop PV, wind, battery storage and an electrified fleet with energy
animating through the distribution wires — the subject matter is present and correct; only the
register reads as a toy.

> **Open.** This decision was made *before* the pivot to a rebrand, and a rebrand reopens it.
> A CSS-only conversion exists and is cheap: the file has **zero hardcoded colours**, and 173 of
> its 175 drawable shapes carry a styling class (137 fill-only, 36 stroke-only, none with both;
> 2 inherit and need checking individually). So `fill → paper` plus a hairline stroke on
> `[class*="fill-"]` converts filled silhouettes to line art in ~8 lines, keeping geometry and
> every animation. Fills must become *opaque paper*, not `none`, so overlapping towers still
> occlude and depth survives.

---

## Voice

Plain, active, specific. Say what a thing does; never sell it. Sentence case; ALL-CAPS rationed
to eyebrows, badges and at most one CTA per page. English body copy; Chinese for proper names,
addresses and the research pillars.

**Retire the exclamatory register** — "Scroll for more!", "More features in development!".
Cheerful punctuation is part of what reads as cute, and it is the cheapest thing on this list to
fix. (This is about exclamation marks, not capitals: a single all-caps CTA per page remains
sanctioned above.)

---

## Multi-platform architecture (defines sub-project 2)

**Invert the pipeline.** Today `general.css :root` is the source of truth and
`generate_token_reference.py` reads *out* of it. Instead:

```
tokens/e3.tokens.json          ← single source of truth (W3C Design Tokens format)
   │
   ├─► static/css/_tokens.css  :root custom properties (web)
   ├─► dist/E3-theme.xml       PowerPoint / Google Slides theme
   └─► dist/e3-print.json      CMYK + Pantone equivalents (poster, letterhead)
```

`make tokens` runs the emitters. Validation moves to the **JSON source**, so a failing colour
is caught before it reaches any platform — replacing the current post-hoc CSS scan.

**Print** needs a proofing pass this spec cannot substitute for: sRGB→CMYK depends on the press
profile, and the olives and sages (`#d3d6a3`, `#bfceaa`, `#aab157`) are the values that shift
most. Treat any computed CMYK as provisional until proofed on the actual stock.

---

## Prior work this supersedes

- **`DESIGN_RULES/`** (11 files) — superseded in full. **Retire in the same commit the new
  system lands, not before:** `validate_design_tokens.py` and `generate_token_reference.py` are
  wired into `make`, and deleting the rules while those still run breaks the build.
- **`specs/2026-07-24-brand-refinement-design.md`** — superseded.
- **`design/minimal-refresh`** (10 commits) — partially retained. The layout work (56rem
  measure, flattened chrome, the news-row `grid-column` fix, unframed portraits) is
  brand-agnostic and carries forward. Colour and token work is re-derived.

Signature-list items formally changed: **1** (skew motif → one CTA per page), **2** (type scale
rebuilt; families kept), **3** (sprite world / blueprint tiles retired), **6** (three-E coding
now from the mark). Item **4** (paper-white, no gradients/photo backgrounds) is retained and
reaffirmed.

---

## Carried decisions from brainstorming

- **Landing page banding.** The homepage already carries six sections below the hero — *The
  Center, The team, Recent work, Selected projects, In the news, Around the lab* (6,320px),
  assembled by `templates/index.html` looping `pages['index']['structure']` and including
  `templates/home/<id>.html`. All six have transparent backgrounds, so alternating
  `--paper` / `--surface` is a small change to existing sections, not new page construction.

  > **Correction.** An earlier draft of this spec claimed the homepage was hero-only and that
  > `.hp-scroll-for-more` promised a scroll that did not exist. That was wrong: it came from
  > reading `templates/home/home.html` (the hero alone) without reading `templates/index.html`.
  > The related claim that `.subpage-header--home` can never appear was also wrong — the header
  > gains `is-visible` on the built page.

- **Genuinely missing:** `research-topics` is in the nav structure but has no
  `templates/home/research-topics.html`, so it is silently skipped by `ignore missing`. Research
  is the one pillar with no homepage presence — and the one that would carry 淨零智慧城市.
  Conversely `templates/home/videos.html` exists but no `videos` id is in the structure, so it
  is never rendered.
- `showInHome` already exists in `publications.json` (5) and `news.json` (6) — the data layer
  anticipated this page. Redefine it as *curated*, not *latest N*: pure recency surfaces
  off-theme work (a Cobb-angle paper in *IEEE TMI* is currently among the five most recent).
- Header and footer are **not** redesigned. Both are complete and well-built.

## Open questions

1. **Hero register** — reopened by the rebrand (see § Imagery doctrine).
2. **`--line` semantics** — rules derive from `#aabdbf`, which also codes Economics. A colour
   serving both a field and a structural role needs an explicit naming rule.

## Acceptance

- No text colour anywhere measures below 4.5:1 on its own background.
- Every colour in the system traces to a logo colour or to `--paper`.
- `tokens/e3.tokens.json` emits web CSS, a slide theme, and print values from one source.
- `python validate_site.py` passes; `make tokens` regenerates without diff noise.
