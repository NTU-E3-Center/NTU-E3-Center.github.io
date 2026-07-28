# Brand Refinement — Design Spec

**Date:** 2026-07-24
**Branch:** `brand-refinement`
**Status:** approved, pending implementation

Spec location note: the Superpowers default is `docs/superpowers/specs/`, but in this
repo `docs/` is the build output — gitignored, and deleted wholesale by
`shutil.rmtree(output_dir)` in [build.py](../build.py) on every run. This file lives in
`specs/`, which was removed from `.gitignore` so specs and plans are tracked.

Contrast figures below were measured, not estimated (WCAG relative luminance against
`--page-bg-color` `#f7fafb`): navy 7.66:1 · link 6.20:1 · sky 2.38:1 · sage 1.69:1.

---

## Purpose

Tune the E3 Center visual identity at **refinement intensity**: a returning visitor
should feel the site is cleaner without being able to name what changed. This is
explicitly *not* a character pass or an identity refresh — no new typeface, no new
hues, no layout or IA changes.

The brief covers four areas the user flagged: colour, the skewed-block motif,
typography, and the accuracy of `DESIGN_RULES/` itself.

## Constraints

- **Off-limits:** the three animated background SVG tiles (solar panels, turbines,
  buildings) stay exactly as they are — artwork, opacity, timing, all of it.
- **Permitted but declined:** a display typeface, relaxing the opacity-only text
  hierarchy, and narrowing the skew motif were all unlocked by the user. Only the
  motif scope is used; the other two are deferred to a future character pass.
- Every change is verified on `localhost:8001` before any merge or push.

## Correction to the original premise

The first version of this plan proposed retiring five "dead" colour tokens
(`--main-light`, `--house-dark`, `--house-light`, `--r-blue`, `--r-purple`) on the
grounds that each had exactly one CSS reference.

That was wrong. Each of those single references is a `.fill-*` / `.stroke-*` utility
class, and every one of those utilities is consumed inside
[static/assets/sprite.svg](../../static/assets/sprite.svg) — the hero and background
artwork. Deleting them would have silently broken the illustrations the user had just
protected. **No colour token is deleted by this spec.**

The real finding is structural, and it is what §1 addresses.

---

## §1 · Colour — name the three layers

### Problem

`DESIGN_RULES/color.md` presents every colour as one flat table. In reality the
system already has three distinct layers, and because they are undocumented nobody
can tell which colours are safe to touch, which is why the palette reads as sprawl
(124 tokens in `:root`).

### Design

Document the layers explicitly, matching the primitive → semantic → component model:

| Layer | Tokens | Consumed by |
|---|---|---|
| **Primitive** | `--r-{red,orange,yellow,green,blue,indigo,purple}`, `--main-light`, `--main-3-light`, `--secondary-light`, `--house-dark`, `--house-light`, `--main-color-3` | The illustration utility layer, and semantic aliases. Never by a UI component directly. |
| **Semantic UI** | `--main-color`, `--main-bg-color`, `--page-bg-color`, `--secondary-color`, `--link-color`, `--line-soft`, `--main-shadow-color`, `--selection-color`, `--cat-*`, `--cat-*-text` | UI components. |
| **Illustration** | `.fill-*` / `.stroke-*` utility classes | `sprite.svg` and inline SVG artwork only. |

**The rule to add:** a UI component consumes semantic tokens only. If a UI surface
needs a spectrum hue, add a semantic alias first — exactly as the news category work
did when it introduced `--cat-student` on top of `--r-green`. Raw `--r-*` in a
component rule is a bug.

This explains rather than deletes: `--r-blue` looks dead from a CSS grep and is in
fact load-bearing artwork.

### The one behavioural change

`--main-color-2` (sky `#4caedd`) has 35 references but measures 2.38:1 against the
page background — below the WCAG AA 4.5:1 floor for text. Audit all 35:

- **Keep:** illustration fills (`.fill-m-2`).
- **Reassign:** any text use moves to the existing emphasis ladder —
  `--main-color` at the appropriate opacity, or `--link-color` if it is a link.
  Measure the member-row position line specifically; if it does not clear 4.5:1 it
  moves too.

**Text never moves to sage.** `--secondary-color` (`#c4c691`) measures 1.69:1 against
the page background — reassigning small text from sky to sage would make contrast
worse, not better. Sage's role is strictly **non-text accent marks**: the active nav
underline, the h3 decorative bar, directional arrows. Those are legitimate because in
every case the colour is redundant with another cue (full-opacity text, position, an
icon shape), so no meaning is carried by colour alone — but sage must never be the
only thing distinguishing a state, and must never be used for a text fill.

This is a narrowing, not a promotion: sky loses its text duty, and sage gains a
documented boundary rather than more territory.

### Non-goals

No hue values change. `--page-bg-color` stays `#f7fafb` — warming it was considered
and rejected as (a) beyond refinement scope and (b) two-thirds of the current
AI-house-style cliché when combined with a display serif.

---

## §2 · Motif — make the written rule honest, lighten the geometry

### Problem

`layout.md` states that **every** card, button, image, chip, and input is a
`.skewed-block`, and that flat or soft-shadowed surfaces must never be introduced.
The CSS already disagrees in at least five places — news thumbnails, inline article
images, filter pills, show-more pills, and category badges are all flat. Those were
being logged as "documented exceptions," which is how a rule dies: by accumulating
exceptions until it describes nothing.

### Design

Invert the rule so it describes what the design actually wants:

- **Skewed** — interactive and photographic surfaces: buttons and CTAs
  (`b-role="btn"`), images, member portraits, the hero image frame, the news date
  badge, the menu drawer.
- **Flat** — dense repeating chrome: filter pills, show-more pills, listing
  thumbnails, inline article images, keyword chips, status and category badges.

The distinction has a reason a reader can apply to a new component: *the skew is a
gesture, and a gesture repeated twenty times in a list stops being one.*

### Geometry

Lighten the block tier so the motif reads assured rather than chunky. Buttons are
untouched — they are already at the lighter values.

| Token | Now | After |
|---|---|---|
| block border width | `0.1875rem` (3px) | `0.125rem` (2px) |
| `--block-shadow-shift` | `0.3125rem` (5px) | `0.25rem` (4px) |
| `--block-hover-shadow-shift` | `0.4375rem` (7px) | `0.375rem` (6px) |

This is the most visible change in the spec and was approved as such. The
radius-doubling hover behaviour, the −3° skew angle, the counter-skew on children,
and the hard-offset (never blurred) shadow rule all stay exactly as they are.

---

## §3 · Typography — one ladder, not two

### Problem

The v3 token ladder (`--fs-h1/h2/h3`, `--fs-lede/body/body-base/secondary`,
`--fs-eyebrow/badge`) was introduced with the old 17-tier names retained as
deprecated aliases "during the migration." The migration never finished: seven
aliases still have 22 call sites.

### Design

Rewrite each call site to its v3 token, then delete the alias block:

| Alias | Sites | Becomes |
|---|---|---|
| `--fs-heading-s` | 8 | `--fs-h3` |
| `--fs-caption` | 5 | `--fs-secondary` |
| `--fs-body-l` | 3 | `--fs-lede` |
| `--fs-heading-l` | 2 | `--fs-h2` |
| `--fs-caption-s` | 2 | `--fs-secondary` |
| `--fs-display-m` | 1 | `--fs-h1` |
| `--fs-prose-lede` | 1 | `--fs-lede` |

Aliases with zero call sites are deleted outright. Every substitution must be
value-preserving — verify the alias resolves to the same computed size at all three
breakpoints before rewriting, and flag any that do not rather than silently changing
a size.

Also normalise label tracking, which has drifted: eyebrows to `0.14em`, badges to
`0.1em`, everywhere.

No new typeface. No change to the scale values themselves.

---

## §4 · Rules docs — resync to reality

`DESIGN_RULES/` is the stated spec ("when the rules and the current CSS disagree,
treat these docs as the spec and the CSS drift as a bug"), so stale entries are
actively harmful. Known drift to fix:

- `components.md` documents `.breadcrumb-parent` / `.breadcrumb-sep` /
  `.breadcrumb-current` at 2.75rem. Those classes were renamed to `.trail-*` long
  ago, and as of the header work the trail is no longer in the header at all — it is
  `.page-trail` in the content flow.
- `components.md` lists `.section-title h2` at 4rem; finding S-4 in `README.md` says
  it was trimmed, and `--fs-h1` is now 3rem.
- `color.md` gains the three-layer model from §1.
- `layout.md` gains the inverted motif rule and the new geometry values from §2.
- `typography.md` drops the deprecated-alias table once §3 lands.
- `README.md` gains findings entries for each change.

---

## Implementation order

Split into two phases so the one visitor-visible change can be judged on its own
rather than mixed into a pile of invisible ones:

- **Phase 1 — §1, §3, §4.** Colour-layer documentation and the sky reassignment,
  the alias retirement, and the doc resync. All invisible by design: if anything
  here changes what a page looks like, that is a bug, not the intent.
- **Phase 2 — §2.** Motif scope and block geometry. Reviewed separately on
  localhost, since this is the only change a visitor can actually see.

## Verification

All work happens on `brand-refinement` and is checked on `localhost:8001` before any
merge or push.

1. `python build.py` completes with **0 SEO warnings**.
2. Visual check at **1440 / 900 / 375 px** (the three documented viewports) on: the
   homepage, one listing page, one detail page, and the members page.
3. Confirm the illustrations and background tiles render unchanged — this is the
   specific regression risk created by touching colour tokens.
4. Confirm no computed font size changed as a side effect of the alias rewrite.
5. Contrast spot-check on any element whose colour was reassigned in §1.

## Non-goals

- No display typeface (deferred to a character pass).
- No hue or background-colour changes.
- No layout, navigation, or information-architecture changes.
- No changes to the background tiles, hero animations, or sprite artwork.
