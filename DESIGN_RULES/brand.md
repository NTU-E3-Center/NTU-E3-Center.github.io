# Brand Foundation — E3 Center

Part of [DESIGN_RULES/](./README.md). This is the **identity layer** — the layer above tokens.
Every other file in this directory says *how* the site is built; this one says *why it looks
the way it does*, so future work (new subpages, refreshes, even a redesign) can evolve the
execution without losing the identity.

When a design decision isn't covered by a rule, decide from this file.

---

## Who this is for

**E3 Center — Energy × Economics × Environment.** A research center in the Department of
Civil Engineering at National Taiwan University, directed by Professor I-Yun Lisa Hsieh
謝依芸. The center works on the sustainable energy transition: transport electrification,
renewable energy, smart grids, hydrogen economics, carbon pricing, green finance — toward a
net-zero future that is "not only cleaner and smarter but also more equitable and resilient."

The audience is mixed: prospective students, academic peers, industry and policy partners,
and journalists. The site must read as **credible engineering** first and **approachable
lab** second — never as a marketing page.

## The design concept: a working engineer's notebook

The whole visual language derives from one idea — *the energy transition as a live
engineering project, drawn by hand and still in progress*:

- **Paper and ink.** The page is paper-white (`--page-bg-color` #f7fafb); nearly all text is
  one navy ink (`--main-color` #0a557e) with hierarchy carried by opacity, like pen pressure
  — not by a palette of greys. See [color.md](./color.md) § Text Emphasis Ladder.
- **The blueprint underneath.** Hand-drawn SVG tiles (solar panels, turbines, buildings) pan
  slowly at 5% opacity behind every page — the faint grid paper the work sits on. Never
  foreground, never faster.
- **Paper cutouts, not glass.** Cards, buttons, and portraits are skewed −3° with hard
  offset teal shadows — they read as physical paper pieces taped over the notebook. This is
  why blur, gradients, and "elevation" shadows are banned: glass morphism belongs to a
  different (and generic) material world. See [layout.md](./layout.md) § Skewed-Block Motif.
- **A world quietly working.** Motion is ambient and slow — the turbine spins, the EV rolls,
  the plane flies. Animation shows the subject's world operating; it never performs for
  attention.
- **Bilingual by nature.** Outfit (Latin) + Noto Sans TC (Traditional Chinese), geometrically
  paired. English leads, Chinese names sit beside it — `I-Yun Lisa Hsieh 謝依芸` — because the
  center is of Taiwan and speaks to the world.

## What the colors mean

| Color | Meaning |
|---|---|
| Navy `--main-color` | The ink. Everything written. |
| Sky `--main-color-2` / `--accent-ink` | Light on the horizon — illustration light and tinted surfaces; `--accent-ink` when sky must be legible text. |
| Olive sage `--secondary-color` | The field marker — underline bars, the "3E" dot, directional arrows and micro-interaction glyphs. Never text. |
| Rainbow primitives `--r-*` | The illustrated world's own colors, surfacing in UI only through semantic aliases (categories, statuses). |
| Yellow / Orange / Green | The three E's: **Energy** (`--r-yellow`), **Economics** (`--r-orange`), **Environment** (`--r-green`) — fixed field coding for research glyphs. |

## Voice

Plain, active, optimistic, a little informal — "Scroll for more!", "More features in
development!", "JOIN US". Sentence case everywhere; ALL-CAPS is rationed to eyebrow labels,
badges, and at most one high-conviction CTA per page. Say what a thing does; never
sell it. Body copy is English; Chinese appears for proper names and addresses.

## The signature list — protected identity

These are the elements that make the site unmistakably E3. Changing any of them is a
**rebrand decision**, not a design tweak — it needs an explicit call by the center, recorded
as a finding in [README.md](./README.md):

1. The −3° skewed-block motif with hard offset teal shadows (no blur, ever).
2. Single-ink typography: navy + opacity ladder, Outfit × Noto Sans TC.
3. The hand-drawn sprite world: one icon source (`sprite.svg`), the blueprint background
   tiles, the animated hero.
4. Paper-white surfaces — no gradients, no photographic backgrounds.
5. Slow ambient motion; 0.15s micro-interactions; radius-doubling tactile hover.
6. The three-E color coding (yellow/orange/green) for research fields.

Everything *not* on this list — layouts, component shapes, type scale bindings, spacing,
page structure, category hues — is open for redesign at any time through the normal rules
process ([extending.md](./extending.md) § Changing a rule).

## Decision principles

1. **One signature moment per page.** Spend boldness in one place (the hero illustration,
   the skew motif); keep everything around it quiet.
2. **Accessibility is brand.** An engineering center that ships sub-AA contrast undermines
   its own credibility. The floor in [semantics-a11y.md](./semantics-a11y.md) is not
   negotiable and `validate_design_tokens.py` enforces the color half mechanically.
3. **Evolution over revolution.** The identity compounds with consistency. Prefer extending
   the system (new semantic token, new pattern, new page from existing recipes) over
   parallel one-off styles. If a rule blocks a genuinely better design, change the rule
   deliberately and record why — never silently diverge.
4. **The content is research.** Publications get typographic emphasis one tier above news
   by design; member pages are page-defining portraits. Hierarchy decisions should keep
   research output the loudest content on the site.
