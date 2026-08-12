# Rebrand handoff — brand foundation branch

**Date:** 2026-08-12
**Branch:** `rebrand/brand-foundation` (35 commits ahead of `source`, pushed to origin)
**Spec:** [specs/2026-08-11-e3-brand-foundation-design.md](../specs/2026-08-11-e3-brand-foundation-design.md)
**Checklist:** [plans/2026-08-11-rebrand-checklist.md](2026-08-11-rebrand-checklist.md) — the working rule is
one item at a time with user approval between items; do not batch.

## Why this branch exists

Director feedback (Lisa Hsieh, relayed in Chinese): the site was 太可愛了 ("too cute") and
目前的前端設計也看不出來淨零智慧城市 ("the frontend doesn't convey net-zero smart city").
The response is a full rebrand: a new design system built from scratch whose every colour
traces to the seven colours of the existing logo (the logo itself is kept). Targets are
website + slides + posters/print; paper figures excluded.

## The new design system

- **Source of truth:** [tokens/e3.tokens.json](../tokens/e3.tokens.json) (W3C Design Tokens
  format, platform-neutral). `make tokens-new` runs `validate_tokens.py` (six invariants,
  including 5.0:1 text contrast on every surface) then `build_tokens.py`, which emits
  [static/css/_tokens.css](../static/css/_tokens.css). Never edit `_tokens.css` by hand.
- **Pipeline inversion:** the old system's source of truth was `general.css :root` (123
  tokens). The new one generates CSS from JSON. `general.css` still declares families the
  token file doesn't model yet (rainbow primitives `--r-*`, illustration utilities,
  `--illo-*`); they migrate family-by-family.
- **Core palette:** paper `#faf9f7` · surface `#eeeede` · line `#ced8d8` · ink `#0a557e`
  (the wordmark navy) · muted `#2c6888` · accent text `#1e6a65` / graphic `#237a74` (mark
  teal) · marker `#aab157` (mark moss — never text).
- **Principle worth remembering:** *the mark supplies identity, not distinguishability.*
  The vivid field trio (yellow/orange/green) stays for badge coding because the mark's
  seven colours sit within ~40° of hue and can't be told apart at badge size.
- **Cache-busting is manual:** every CSS/JS change needs a `?v=N` bump in
  [templates/base.html](../templates/base.html) or browsers serve stale files. Currently
  `_tokens.css v=5 · general.css v=72 · style.css v=69 · subpage.css v=82 · script.js v=5`.
  The sprite (`/assets/sprite.svg`) has **no** version param — stale caches degrade
  gracefully (old hardcoded fills) but a `?v=` scheme is worth adding if it changes again.

## Homepage state (rebuilt this session)

Four sections: hero → About (slogan + one-line lede, narrow measure) → Research (three
pillars) → Recent work / News. Members, projects, group-life sections deleted from the
homepage (subpages untouched). Alternating paper/surface banding starts at About
(`box-shadow: 0 0 0 100vmax` + `clip-path` full-bleed technique).

**Hero:** inline logo top-left, "Energy × Economics × Environment" right-aligned on the
same line (moss ×), centred illustration, no CTAs, no scroll cue. Covers the viewport via
`max(--_home-min-height, 100lvh)`.

**Hero illustration — the palette went round trip.** Single-ink proved too austere; the
user asked for the original fills back. Now: original pre-rebrand blues (`#4caedd` /
`#badcea` / `#f4fafc`, hue verbatim from `328e990f~1`) each mixed a step toward paper —
minted as `--illo-sky/-pale/-faint` in `general.css :root`, deliberately **outside** the
mark-traceable token file, decorative only. Battery + PV needed a separate fix (their
animations override class fills via `--icon-flash-*`; re-pointed hero-scoped inside
`#home .hp-img`). The bolt flashes sky→ink. Navy outlines, moss dashes, orange 101 beacon
unchanged. **Important SVG fact:** `home.svg` has zero strokes — every "line" is the
exposed edge of a dark `fill-m` polygon under lighter overlays. Never add strokes to its
filled shapes; you get doubled lines.

**Arrows:** sprite arrow symbols now `fill="currentColor"`; one rule in `general.css`
(`svg:has(use[href*="#svg-arrow"])`) sets `--marker` sitewide. The sprite's quote/hashtag/
play glyphs still carry hardcoded sage `#c4c691` — undecided.

**script.js:** the deleted homepage sections left dead code that crashed at line 266
(null `.glf-slider-wrapper`), killing everything below it. Removed. Checklist 6.1
("homepage doesn't scroll") did **not** reproduce — the crash was the real defect.

## How to verify

```bash
make tokens-new        # validate + regenerate _tokens.css
python build.py        # full site build into docs/
python3 .claude/hooks/validate_css_hook.py   # the edit hook, runnable standalone
```

Both validators are at 0 failures on HEAD. `validate_design_tokens.py` reads tokens from
BOTH `_tokens.css` and `general.css` and derives the paper colour from `_tokens.css` —
don't re-hardcode it.

## Open items, ranked

1. **Type scale rollout** — the biggest remaining consolidation. Adopt the emitted
   `--fs-*` / `--lh-*` / `--tracking-*` across stylesheets and retire the old per-tier
   root font scaling. Unlocks the full RWD pass (375/768/1024/1440/1920), which has
   never run on the rebuilt homepage.
2. **5.1 Flatten skewed buttons** — `.menu-btn` (every page) and `.section-cta-btn
   skewed-block` in `pages/about.html`, `pages/research.html`, `pages/members.html`.
3. **Line-weight decision** — 9 `border-color` ink mixes at 45–50% need either a
   `--line-strong` token or demotion to `--line`; ~15 background tints at 3–14% stay.
4. **6.2 `showInHome` should mean curated, not latest-N** — recency surfaced an
   off-topic Cobb-angle paper (IEEE TMI) among the homepage five.
5. **Hygiene:** orphaned `templates/home/videos.html` (1.7); untracked `.agents/`,
   `skills-lock.json`, `static/assets/sprite.svg.bak` (6.5/6.6); zero-consumer tokens
   `--structure`, `--ink-hsl`, `--fw-h2/h3`, `--w-prose`.
6. **Governance: show Lisa the spec + rebuilt homepage before going further** — a
   centre-wide rebrand needs director sign-off, and the restored illustration blues are
   adjacent to her original "too cute" comment; confirm the direction survives contact.
7. **Sub-project 2 remainder** — PPTX theme emitter and print/CMYK emitter from the same
   token file. `DESIGN_RULES/` retires only when the new system covers layout/components/
   patterns/a11y, in the same commit as fixing `generate_token_reference.py` (hardcodes
   `OUT = DESIGN_RULES/tokens.md`).

## Traps for the next session

- All entries in a `member.json`-style list must share identical keys (empty strings,
  never omitted keys) — see CLAUDE.md.
- Publication dates use the journal **issue** date, never "available online".
- Shell backticks in commit messages have bitten twice — always use quoted heredocs
  (`git commit -F - <<'MSG'`).
- `build.py` rmtree-races the static server occasionally (`Directory not empty: assets`);
  retry once.
- The homepage-only automated-browser scroll oddity was environmental; don't chase it.
