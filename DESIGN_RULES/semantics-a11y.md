# Semantics & Accessibility

Part of [DESIGN_RULES/](./README.md). Heading hierarchy, the contrast/size floor, focus,
motion, and forms. Accessibility is brand here ([brand.md](./brand.md) § Decision
principles): the floor is not negotiable, and the color half is machine-enforced by
`validate_design_tokens.py`.

---

## Heading Hierarchy

Every page MUST contain exactly one `<h1>`. Section groupings inside subpages are `<h2>`;
sub-groupings `<h3>`.

| Page | Has h1? | Source |
|---|---|---|
| `/` (homepage) | yes | `#home .hp-title h1` |
| `/members/`, `/publications/`, `/news/`, `/group-life/` | yes (sr-only) | `partials/subpage-header.html` |
| `/contact/` | yes | `.contact-lead` |
| member profile, news article, publication/project detail | yes (visible) | template's own h1, with `suppressSrH1 = True` |

> **Rule:** list-item titles (member-row, publication-row, news-row) are **not** `<h*>` —
> see [patterns.md](./patterns.md) § List Item Title. Never use `<h4>`–`<h6>` for repeating
> list items.

## Contrast & Size Floor

- **Body text:** `#0a557e` on `#ffffff` ≈ 7.2:1 — AAA.
- **Opacity floor:** opacity ≤ 0.45 on white drops below AA (≈3.2:1) — allowed only for
  *decorative* text (separators, placeholders, eyebrow labels at small sizes). Body-size
  secondary text keeps opacity ≥ **0.6**; interactive text too (findings [C-1], [N-4]).
- **Token pairs:** every `--cat-*`/`--status-*` base/`-text` pair must clear AA on its real
  composited tint *and* the bare page background — enforced by `validate_design_tokens.py`
  (finding [B-6]: validate against the real backdrop, never white).
- **Smallest mobile size:** 0.75rem (10.5px at the 14px root). The LABEL token bump exists
  to guarantee this — never restate label sizes in rem ([A-1]).
- **Tap targets:** ≥ 44×44px. Don't shrink control padding below `0.3rem 0.875rem` on
  mobile.

## Focus

- The global recipe (`general.css` `:focus-visible`): `0.125rem solid var(--main-color)`
  outline, `0.125rem` offset. Focus rings are always `--main-color` — never the sky accent
  (2.38:1, finding [B-2]).
- Skewed blocks mirror their hover state on `:focus-visible` (translate + shadow growth),
  so keyboard users get the same tactile feedback as pointer users. Give any new
  interactive component a visible `:focus-visible` state.
- **Never** `outline: none` without an equal-or-better visible replacement in the same
  rule.

## Motion

- **Global kill-switch:** under `prefers-reduced-motion: reduce`, a blanket rule in
  `general.css` (beside the smooth-scroll rule) collapses every `animation` to one instant
  frame, snaps smooth scrolling to `auto`, and turns off cross-page `@view-transition`
  navigation — the sprite world and the blueprint pan read as a still drawing. Ambient
  loops therefore need no per-component guard ([A-3] resolved).
- **Transition-based states** (drawers, filters, sticky headers) still add targeted
  `prefers-reduced-motion` blocks — the kill-switch covers `animation` only, never
  `transition`. A new animated component relies on the kill-switch; a new *transitioned*
  state ships its own reduce variant.
- Micro-interactions stay at `--hover-transition-time` (0.15s); ambient motion stays slow
  ([brand.md](./brand.md) — "a world quietly working", never performing).

## Forms

- **16px auto-zoom floor:** form inputs never compute below 16px font-size on phones, so
  iOS Safari never zoom-snaps on focus. The phone root is 14px, so inputs pin their size
  with `max(var(--fs-*), var(--fs-input-floor))` — `--fs-input-floor` (1.1875rem) is the
  device-constant token in `general.css :root`. Use the same recipe on any new input.
- Labels follow the eyebrow recipe; status feedback uses the `--status-*` token pairs so
  contrast is validator-guarded; color is never the sole signal of a state
  ([color.md](./color.md) § Accent Color Use).
