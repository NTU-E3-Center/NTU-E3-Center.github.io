# Extending the System

Part of [DESIGN_RULES/](./README.md). Playbooks for the three ways this site grows: a new
subpage, a new component, a new category/status. Plus the procedure for changing a rule,
and the redesign policy.

---

## Adding a new subpage

1. **Template.** Extend `base.html`; include `partials/subpage-header.html`. Every page gets
   exactly one `<h1>` — visible if the page has a natural title, `sr-only` via the partial
   otherwise; a template that renders its own visible h1 passes `suppressSrH1 = True`.
   Detail pages (not listings) render `.page-trail` as the first element of content flow.
2. **Type.** Pick roles from [typography.md](./typography.md) § Content Roles — every piece
   of content on the new page should map to an existing role. A prose surface is added to
   the unified prose recipe's `:where()` list in `general.css`, never given its own
   `font-size`. If the page genuinely needs a new role, add it to the role table first.
3. **Color.** Semantic tokens only ([color.md](./color.md)); hierarchy via the opacity
   ladder; new hue needs → new semantic alias in `:root`.
4. **Layout.** `--gutter-x` governs the edges — no inner `padding-inline`. Sections cap at
   80rem. Surfaces follow the skew/flat split in [layout.md](./layout.md).
5. **Navigation.** Register the page in the header nav / menu drawer partials and the
   sitemap; SEO meta comes from the `seo_*` helpers in `build.py`.
6. **Images** go through the `build.py` Pillow pipeline (responsive WebP widths from
   `config.py`) — never hand-placed full-size files.
7. **Verify:** run `python validate_design_tokens.py`; test at the five widths in
   [responsive.md](./responsive.md); check one-h1, focus visibility, and reduced-motion
   variants ([semantics-a11y.md](./semantics-a11y.md)).

## Adding a new component

Follow the quick checklist in [README.md](./README.md). The two decisions that shape
everything else:

- **Which roles does its text play?** → bindings in [typography.md](./typography.md).
- **What kind of surface is it?** Interactive/photographic → skewed block; dense repeating
  chrome → flat. → [layout.md](./layout.md) § Skewed-Block Motif.

Reuse recipes from [patterns.md](./patterns.md) (eyebrow, badge, date marker, list-item
title) before inventing anything.

## Adding a news category or lifecycle status

1. Add the token **pair** in `general.css :root`: `--cat-<name>` (raw hue for the pill
   tint) and `--cat-<name>-text` (hue mixed toward `--main-color` for bare text). Statuses
   use `--status-<name>` / `--status-<name>-text` the same way.
2. Mixing toward navy only stays in-hue when the source hue is close enough to navy — red
   is not (see finding [B-7]); anchor far hues toward a dark same-hue color instead.
3. `validate_design_tokens.py` picks up any base/`-text` pair automatically and enforces
   AA on the real composited tint — run it; retune the mix percentage until it passes.
4. Consume only the semantic tokens in components; the badge recipe is in
   [patterns.md](./patterns.md).

## Changing a rule

Rules encode intent, not history. When a better design conflicts with a rule:

1. Change the rule **first**, in the file that owns it, in one place.
2. Record a finding in [README.md](./README.md) § Findings — what changed, why, severity.
3. Then change the CSS to match.

Never the reverse order, and never silently. A rule nobody is willing to change is dead
weight; a rule changed without a trace is drift.

## Redesign policy: evolution over revolution

The identity ([brand.md](./brand.md)) is healthy, distinctive, and fully token-migrated —
a ground-up redesign would spend a lot to lose a real asset. The sanctioned path:

- **Free to redesign anytime** through the normal rules process: page layouts, component
  shapes, the type-scale bindings, spacing rhythm, category hues, listing designs.
- **Rebrand decisions** (explicit sign-off, recorded finding): anything on the signature
  list in [brand.md](./brand.md).
- A redesign of any scope starts by editing these docs (the spec), not the CSS — the same
  docs-are-spec posture that governs small changes.
