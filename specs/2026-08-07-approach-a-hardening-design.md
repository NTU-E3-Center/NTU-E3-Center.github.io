# Approach A — Harden the existing architecture (no framework migration)

**Date:** 2026-08-07
**Status:** Draft — pending review
**Decision context:** We evaluated rewriting the site in React (and, as a
middle option, migrating to Astro) against the two complaints driving the
question: the browser tab feels heavy, and development/maintenance feels
heavy and risky. The evaluation concluded that neither complaint is caused
by the absence of a framework — the site is pre-rendered static HTML with
~1,300 lines of vanilla JS, six stable Python build dependencies, and CI
gates already in place. A React rewrite would *increase* browser memory
(runtime + hydration), *increase* dev-environment weight (node_modules),
and discard tested, accumulated value (SEO work, design-token system and
validators, member-CV rendering rules, publications funnel) for weeks of
effort. The sustainable path is targeted hardening of what exists.

## Goals

1. Reduce the home page's idle CPU/memory cost in the browser.
2. Make builds fast enough for a comfortable edit-preview loop.
3. Make `build.py` safe to modify by splitting it into focused modules.
4. Mechanically enforce the RWD breakpoint discipline that today lives in prose.
5. Lower the bus factor with a one-page maintenance handoff doc.

## Non-goals

- No framework migration (React, Astro, or otherwise). Revisit only if a
  concrete handoff to a JS-only maintainer materialises.
- No visual redesign; built output must be byte-identical after the
  refactor (workstream 3) except where workstream 1 deliberately changes JS.
- No content changes.
- No sweeping clamp()/container-query rewrite of existing CSS — policy
  applies to touched components only (see workstream 4).

## Current state (verified 2026-08-07)

Already solved — out of scope:

- Home video is lazy: `preload="none"`, poster image, source injected on
  click (`templates/home/videos.html`).
- CI builds every PR against `source` and gates on
  `validate_design_tokens.py` + `validate_site.py` (`deploy.yml`); deploy
  fires only on merge.
- `__pycache__/` and `docs/` are gitignored; images ship as WebP with
  srcset variants.
- Four-tier RWD system documented in `DESIGN_RULES/responsive.md`,
  including a component-local breakpoint registry.

Verified problems this spec addresses:

- `animateHpTheSky` (`static/js/script.js` ~line 153) runs a perpetual
  `requestAnimationFrame` loop whenever the tab is visible. It pauses on
  `visibilitychange` but has **no `prefers-reduced-motion` check** (the
  group-life carousel at line 348 has one) and **no viewport gate** — it
  keeps mutating SVG polygon attributes even when the hero is scrolled
  far off-screen.
- `convert_to_webp` (`build.py:1031`) re-encodes **every** image on
  **every** build — 757 WebP outputs through Pillow each run. This is the
  dominant build cost (time and memory) and makes a watch-rebuild loop
  impractical.
- `build.py` is a 1,162-line monolith mixing page rendering, BibTeX
  generation, SEO validation, sitemap generation, and the image pipeline.
- The sanctioned-breakpoint rule exists only as prose in `responsive.md`;
  the token validator does not check `@media` queries against it.
- `contents/members/member-info.legacy.xlsx` is dead weight (superseded by
  `member-info.xlsx`).
- No single onboarding document for a successor maintainer.

## Design

### Workstream 1 — Home animation efficiency (browser)

In `static/js/script.js`, gate `animateHpTheSky` twice:

1. **Reduced motion:** bail out entirely when
   `window.matchMedia('(prefers-reduced-motion: reduce)').matches`, matching
   the existing carousel pattern (line 348) and the 11 CSS
   `prefers-reduced-motion` blocks.
2. **Viewport gate:** wrap the rAF loop in an `IntersectionObserver` on the
   hero SVG — cancel the frame loop when the hero leaves the viewport,
   resume when it re-enters. The existing `visibilitychange` pause stays;
   the two guards share the same `rafId` start/stop helpers so they cannot
   double-start the loop (same single-source-of-truth pattern as
   `resBlockAniRunning`).

Measurement: before/after numbers from Chrome DevTools Performance Monitor
(CPU % and JS heap while idle at mid-page scroll) recorded in the PR
description. Success = frame loop provably stopped when hero is off-screen.

### Workstream 2 — Incremental image pipeline (build)

The build starts by deleting `docs/` entirely (`build.py` `__main__`,
deliberately — the clean-build guarantee prevents stale pages), so a
skip-if-output-newer check would never fire. Instead, `convert_to_webp`
gains a **persistent encode cache** outside the output tree:

- New gitignored `.webp-cache/` directory. Each encoded variant is stored
  under a key hashing the source path, requested width, quality,
  target aspect, and source mtime.
- On build, a cache hit is `shutil.copy2`ed into `docs/` (cheap); a miss
  encodes as today and populates the cache. The clean-build guarantee for
  HTML/stale pages is untouched — only redundant *re-encoding* is skipped.
- `python build.py --force-images` clears the cache first; a
  `make clean-cache` target does the same standalone. CI is unaffected —
  fresh checkouts have no cache, so CI always encodes everything.

Expected effect: warm rebuilds drop from encoding 757 images to encoding
only changed ones (usually zero), making workstream 5's watch loop viable.

### Workstream 3 — Modularize `build.py`

Split by page type into `lib/`, alongside the existing
`lib/excel_to_content.py` and `lib/seo_helpers.py`:

| New module | Moves from `build.py` |
|---|---|
| `lib/publications.py` | `bold_author`, `get_pub_sort_key`, `pub_year4`, `pub_slug`, BibTeX helpers, `render_publication_pages` |
| `lib/members.py` | `render_member_pages`, `compress_member_images` |
| `lib/news.py` | `news_slug_from_pagelink`, `render_news_pages` |
| `lib/projects.py` | `proj_slug`, `_funder_bucket`, `render_project_pages` |
| `lib/assets.py` | `copy_static`, `copy_videos`, `convert_to_webp`, `compress_and_convert_images` |
| `lib/seo_site.py` | `generate_sitemap`, `validate_seo`, `_check_page` |

`build.py` remains the entry point and orchestrator (target ≤ ~250 lines):
config, data loading, and ordered calls into the modules. Helpers shared
across page types (e.g. `slugify_title`, used by both publication and
project slugs) move to a small shared module (`lib/slugs.py` or similar) —
exact placement is the implementer's call, gated by the empty-diff test.
No function bodies change in this workstream — moves only.

**Behaviour-preservation gate:** build to a snapshot before the refactor,
build after, and `diff -r` the two `docs/` trees. The diff must be empty.
(Sitemap dates derive from file mtimes, which don't change during a
refactor, so the output is deterministic.) This gate is the workstream's
acceptance test and runs before its PR is opened.

### Workstream 4 — RWD guardrails

1. **Validator rule** (new check in `validate_design_tokens.py`): every
   width-based `@media` query in `static/css/*.css` must use a breakpoint
   from the sanctioned set — tier edges `37.5rem`, `64rem`, `90rem` plus
   the component-local registry in `responsive.md` (`56rem`, `48rem`,
   `64.0625rem`). Any other value fails the build with a message pointing
   to the registry. Adding a breakpoint = add it to the registry table and
   the validator's list in the same PR, keeping spec and enforcement in
   lockstep. Non-width queries (`prefers-reduced-motion`, `print`,
   `hover`) are exempt.
2. **Policy documentation** (extend `DESIGN_RULES/responsive.md`, building
   on finding [R-1]): when a component is touched, prefer `clamp(min, vw,
   max)` over new breakpoint overrides for hero-tier text, and prefer
   container queries for components rendered in multiple width contexts
   (member cards, publication rows). No proactive sweep of existing CSS.

### Workstream 5 — Live-reload dev loop

New `make dev` target using the `livereload` package (added to
`requirements.txt` — it is small and keeps one source of truth, matching
the file's stated policy): watch `contents/`, `templates/`, `static/`,
`build.py`, `lib/`; on change, run the (now incremental) build and trigger
a browser reload, serving `docs/` on the same port 8000 as `make serve`.
Depends on workstream 2 for acceptable rebuild latency.

### Workstream 6 — Repo hygiene + handoff doc

- Delete `contents/members/member-info.legacy.xlsx` (recoverable from git
  history; the active file is `member-info.xlsx`). Remove its entry from
  `STRUCTURE.md`, which currently documents it as an archived reference.
- New `MAINTENANCE.md` at repo root — a one-page successor guide: how to
  add a publication (including the issue-date rule from `CLAUDE.md`), add
  a news item, add/update a member, run `make dev`/`build`/`tokens`/
  `audit-site`, and where the deeper docs live (`STRUCTURE.md`,
  `DESIGN_RULES/`, `specs/`). Written for a new student with no context;
  every task ≤ 15 minutes by following it.

## Testing

- **W1:** manual — DevTools Performance Monitor before/after; verify loop
  stops off-screen, restarts on-screen, and never runs under reduced
  motion. Existing behaviour (visibilitychange pause) re-verified.
- **W2:** `make clean && make build` twice — second build skips all
  encodes and produces an identical `docs/` tree (`diff -r`); touching one
  source image re-encodes only that image's variants.
- **W3:** empty `diff -r` output gate (above) + CI validators green.
- **W4:** validator passes on current CSS as-is (proves the sanctioned
  list is complete), then fails when a rogue `@media (max-width: 50rem)`
  is temporarily added (proves enforcement works).
- **W5:** manual — edit a template, browser refreshes with the change
  within a few seconds.
- **W6:** `make build` + full CI green after the deletion (proves nothing
  reads the legacy file).

## Order and delivery

Each workstream is a small, independently revertible PR to `source`.
Sequence: **W2 → W3 → W5** (build speed unblocks the refactor's diff gate
and then the watch loop) and **W1, W4, W6** in any order alongside.

## Out of scope / future

- Astro migration: only upon a concrete JS-only maintainer handoff.
- Sweeping clamp()/container-query conversion of existing components.
- Any change to the signature homepage visual identity (per
  `DESIGN_RULES`, that requires explicit sign-off).
