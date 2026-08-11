# E3 Rebrand — Working Checklist

Live checklist, worked **one item at a time**. Each item is scoped so it can be built, seen in
the browser, and accepted or reverted on its own. No batching.

Branch: `rebrand/brand-foundation`
Spec: [specs/2026-08-11-e3-brand-foundation-design.md](../specs/2026-08-11-e3-brand-foundation-design.md)

**Working rule:** one item → build → screenshot → you accept or reject → commit → next.

---

## ✅ Done

- [x] **Brand foundation spec** committed (`7c566361`)
- [x] **Palette trial** — semantic slots remapped to the logo-derived palette in
      `general.css :root`. Passes `validate_design_tokens.py` (0 failures).
      Paper `#faf9f8`, accent `#237a74`, olive `#aab157`, ink `#0a557e` unchanged.
- [x] **Lisa's row sized like every other member** — removed the `.mem-group--pi`
      scale overrides at all three breakpoints. Verified: PI 144px/36px = staff 144px/36px.
- [x] **Cache-bust versions bumped** (`general.css?v=63`, `subpage.css?v=81`) — required or
      returning visitors keep the old CSS.

---

## 1 · Landing page

- [ ] **1.1 Remove the members section** from the homepage. Delete the `members` entry's
      homepage include (`templates/home/members.html`) or drop it from the loop. The team stays
      reachable via nav and `/members/`.
- [ ] **1.2 Add the research section** — `templates/home/research-topics.html`. It's in
      `pages['index']['structure']` already but the template doesn't exist, so it's silently
      skipped by `ignore missing`. **This is the only section that carries 淨零智慧城市.**
- [ ] **1.3 Three pillars** in that section, from `contents/research/research.json`:
      Smart Energy Systems 智慧能源系統 · Low-Carbon Transport & Supply Chains 低碳運輸供應鏈 ·
      Sustainable Energy Decision-Making 永續能源決策.
- [ ] **1.4 Section order** — decide. Current: The Center → The team → Recent work →
      Selected projects → In the news → Around the lab.
      Proposed: The Center → **Research** → Recent work → Selected projects → In the news →
      Around the lab.
- [ ] **1.5 Alternating band backgrounds** — `--paper` / `--surface`. All six sections are
      currently transparent, so this is a small addition, not new construction.
- [ ] **1.6 Decide the tint value** — the earlier 12% pick was against the *old* palette and
      needs re-deriving from `#d3d6a3` on the new paper.
- [ ] **1.7 `templates/home/videos.html` is orphaned** — no `videos` id in the structure, so it
      never renders. Wire it up or delete it.

## 2 · Hero

- [ ] **2.1 Decide hero content.** Proposal on the table: strip to the logo alone.
      **My recommendation: partial.** Keep the logo, keep *Energy / Economics / Environment*
      (it defines what E3 means — a visitor who doesn't know the centre learns nothing from a
      bare logo), keep the director line (for academic peers the PI *is* the credential).
      Cut "About the center" — the nav already has it. Keep or move the publications count.
- [ ] **2.2 Shorten the hero below 100vh** so the next section peeks. This addresses the real
      problem — a full screen of low density — better than emptying it, and it makes
      "Scroll for more!" unnecessary.
- [ ] **2.3 Remove "Scroll for more!"** once 2.2 lands. Exclamatory register, and redundant
      once the page shows it's scrollable.
- [ ] **2.4 Hero illustration register** — leave as-is, or apply the CSS-only line-art
      conversion (~8 lines, no redraw). Reopened by the rebrand; currently unresolved.

## 3 · Palette rollout

- [ ] **3.1 Review the trial in context** — the city now reads sage-green. Watch for it
      reading "garden/eco" rather than "energy systems"; `--main-color-3` is the lever.
- [ ] **3.2 `--main-bg-color`** is still `#ffffff`. On warm paper, pure-white fills read cold.
      Decide: keep white, or move to paper.
- [ ] **3.3 Add `--surface` and `--line`** as real tokens. Today ~20 hand-rolled `color-mix()`
      calls at nine different strengths exist across the CSS with no named surface token.
- [ ] **3.4 Retire `--r-yellow` / `--r-orange` / `--r-green`** field coding in favour of the
      three ribbons.
- [ ] **3.5 Fold the 20 ad-hoc `color-mix()` calls** onto the new tokens.

## 4 · Type

- [ ] **4.1 Rebuilt scale** — 56 / 32 / 24 / 20 / 17 / 15 / 13 / 11. Least-evidenced part of
      the spec; derived from principle, not tested. Worth trialling on one page first.
- [ ] **4.2 Emphasis ladder → two steps** (`--ink` 1.0, `--muted` 0.85). The documented ladder
      ships sub-AA text: Secondary 0.70 measures 3.77:1.

## 5 · Chrome

- [ ] **5.1 Flatten `.menu-btn`** — it carries `skewed-block` on every page, the main violation
      of one-skewed-CTA-per-page.
- [ ] **5.2 Footer surface** — with banding, the footer follows a tinted section. Recommend
      paper so alternation continues.

## 6 · Bugs / hygiene

- [ ] **6.1 Homepage does not scroll** in an automated browser while every subpage does; the
      difference is homepage-only `js/script.js` + the loading overlay.
      **Check in a real browser first** — if it reproduces for users this outranks everything
      else on this list.
- [ ] **6.2 `showInHome` should mean curated, not latest-N** — recency alone surfaced a
      Cobb-angle paper in *IEEE TMI* among the five most recent.
- [ ] **6.3 `.hp-last-update`** orphan rule deletion — still uncommitted.
- [ ] **6.4 `.gitignore`** — `.superpowers/` addition uncommitted.
- [ ] **6.5 `.agents/` + `skills-lock.json`** — 13 unused skills, commit or ignore.
- [ ] **6.6 `static/assets/sprite.svg.bak`** — stray backup, delete or ignore.

## 7 · Deferred (needs its own cycle)

- [ ] Token architecture — `tokens/e3.tokens.json` as source of truth, emitting web CSS +
      slide theme + print values. *(This is sub-project 2.)*
- [ ] Slide theme, poster/print CMYK.
- [ ] Subpage rollout across the remaining 13 page types.
- [ ] Retire `DESIGN_RULES/` — same commit as the new system, not before, or `make` breaks.
- [ ] Show the spec to Lisa before implementation goes further.
