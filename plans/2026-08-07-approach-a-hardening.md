# Approach A Hardening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the existing Python static-site architecture per
`specs/2026-08-07-approach-a-hardening-design.md` — faster builds, safer
`build.py`, gated home animation, enforced RWD breakpoints, live-reload dev
loop, and a successor handoff doc. No framework migration.

**Architecture:** The site stays a Jinja2/JSON static generator deployed by
GitHub Actions. Work splits into six independent workstreams delivered as
small commits on branch `hardening-approach-a`: a persistent WebP encode
cache, a moves-only decomposition of `build.py` into `lib/` modules guarded
by an empty-output-diff gate, JS animation gating, a new validator check,
a `livereload` dev server, and documentation.

**Tech Stack:** Python 3 (jinja2, Pillow, markdown, openpyxl, bs4), vanilla
JS, GNU Make, `livereload` (new dev dependency).

## Global Constraints

- Branch: `hardening-approach-a` (off `origin/source`); one PR per this plan.
- Commits: conventional prefixes, subject ≤ 72 chars, **no Co-Authored-By or
  any trailer lines**, stage files by name (never `git add .`).
- Every task ends with `python build.py && python validate_design_tokens.py
  && python validate_site.py` green unless the task says otherwise.
- Refactor tasks (2–8) are **moves only**: function bodies byte-identical;
  the built `docs/` tree must be identical before/after (`diff -r` empty).
- `DESIGN_RULES/` is spec: any CSS/token-adjacent change reruns
  `python validate_design_tokens.py`. No change to the homepage's visual
  identity.
- Repo conventions in `CLAUDE.md` apply (publication issue-date rule, etc.).
- The `E3website` conda env is assumed active (see README).

**The diff gate**, referenced by Tasks 2–8. Run BEFORE the change:

```bash
python build.py && rm -rf /tmp/e3-snap && cp -r docs /tmp/e3-snap
```

and AFTER the change:

```bash
python build.py && diff -r /tmp/e3-snap docs && echo IDENTICAL
```

Expected: the word `IDENTICAL` and no diff output. Any diff = the move
changed behaviour; fix before committing. (Sitemap `lastmod` values derive
from `contents/` mtimes only, which these tasks never touch, so the gate is
deterministic. Task 1's cache makes each gate build fast.)

---

### Task 1: Persistent WebP encode cache (W2)

**Files:**
- Modify: `config.py` (add one constant)
- Modify: `build.py:1031-1062` (`convert_to_webp`), `build.py:1132-1139` (`__main__` head)
- Modify: `.gitignore`, `Makefile`

**Interfaces:**
- Consumes: existing `convert_to_webp(path, dst_path, sizes, compression_quality, basename, target_aspect)` — signature unchanged.
- Produces: same signature (callers at `build.py:1091-1092, 1126-1127` untouched); new `WEBP_CACHE_DIR` constant in `config.py`; new `_webp_cache_key(path, size, quality, target_aspect) -> str` helper in `build.py`.

- [ ] **Step 1: Baseline timing** — record the cost the cache removes.

```bash
make clean && time python build.py 2>&1 | tail -1
```

Note the `real` time (expect minutes; 757 encodes).

- [ ] **Step 2: Add the cache constant to `config.py`** (append at end):

```python
# Persistent WebP encode cache (gitignored). build.py rmtree's docs/ every
# run for the clean-build guarantee, so already-encoded variants are reused
# from here instead of re-encoding; keys include the source mtime, so an
# edited image re-encodes automatically.
WEBP_CACHE_DIR = ".webp-cache"
```

- [ ] **Step 3: Rewrite `convert_to_webp` with the cache.** In `build.py`,
add `import hashlib` to the imports at the top, extend the `from config
import (...)` list with `WEBP_CACHE_DIR`, and replace the body of
`convert_to_webp` (keep the existing docstring, appending the cache
paragraph shown):

```python
def _webp_cache_key(path, size, quality, target_aspect):
    """Cache key for one encoded variant. Includes the source mtime so an
    edited image invalidates its own entries; stale entries are only ever
    orphaned, never wrongly reused."""
    raw = f"{os.path.relpath(path)}|{size}|{quality}|{target_aspect}|{os.stat(path).st_mtime_ns}"
    return hashlib.sha1(raw.encode()).hexdigest()


def convert_to_webp(path, dst_path, sizes, compression_quality=WEBP_QUALITY, basename=None, target_aspect=None):
    """<existing docstring unchanged>

    Encoded variants are cached in WEBP_CACHE_DIR keyed on source path,
    width, quality, aspect, and source mtime — a hit is copied into place,
    a miss encodes as before and populates the cache."""
    if basename is None:
        basename = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(WEBP_CACHE_DIR, exist_ok=True)
    to_encode = []
    for size in sizes:
        webp_output_path = f"{dst_path}/{basename}-{size}w.webp"
        cache_file = os.path.join(
            WEBP_CACHE_DIR,
            f"{_webp_cache_key(path, size, compression_quality, target_aspect)}.webp")
        if os.path.exists(cache_file):
            shutil.copy2(cache_file, webp_output_path)
        else:
            to_encode.append((size, cache_file, webp_output_path))
    if not to_encode:
        return
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        src_w = img.width
        for size, cache_file, webp_output_path in to_encode:
            # Never upscale: when the requested width exceeds the source
            # width, cap at the source. Pillow's resize can't add detail —
            # upscaled WebPs look soft on retina screens (see Jun '26
            # group-life: 1477-px source upscaled to 2000w rendered blurry).
            effective_size = min(size, src_w)
            if target_aspect:
                w_aspect, h_aspect = target_aspect
                target_size = (effective_size, int(effective_size * h_aspect / w_aspect))
                img_resized = ImageOps.fit(img, target_size, centering=(0.5, 0.5))
            else:
                img_resized = img.resize((effective_size, int(effective_size * img.height / img.width)))
            img_resized.save(webp_output_path, "WEBP", quality=compression_quality)
            shutil.copy2(webp_output_path, cache_file)
```

- [ ] **Step 4: Add `--force-images`.** In the `if __name__ == "__main__":`
block, immediately before the existing `if os.path.isdir(output_dir):`
lines, insert:

```python
    import sys
    # --force-images: drop the encode cache so every variant re-encodes.
    if "--force-images" in sys.argv and os.path.isdir(WEBP_CACHE_DIR):
        shutil.rmtree(WEBP_CACHE_DIR)
```

- [ ] **Step 5: Gitignore + Makefile.** In `.gitignore`, under the
`# Build output` comment block, add:

```
# WebP encode cache (see config.WEBP_CACHE_DIR)
.webp-cache/
```

In `Makefile`: add `clean-cache` to the `.PHONY` line, a help line
`@echo "make clean-cache      - drop the WebP encode cache (forces full re-encode)"`,
and the target:

```make
clean-cache:
	rm -rf .webp-cache
```

- [ ] **Step 6: Verify correctness and speedup.**

```bash
make clean && make clean-cache && time python build.py          # cold: encodes all, populates cache
rm -rf /tmp/e3-snap && cp -r docs /tmp/e3-snap
make clean && time python build.py                              # warm: expect large speedup
diff -r /tmp/e3-snap docs && echo IDENTICAL
touch contents/videos/2025-1.jpg && python build.py 2>&1 | grep "2025-1"  # only this image re-encodes
```

Expected: warm build much faster than cold; `IDENTICAL`; the touch causes
exactly that image's variants to re-encode (its convert prints reappear).

- [ ] **Step 7: Validators + commit.**

```bash
python validate_design_tokens.py && python validate_site.py
git add config.py build.py .gitignore Makefile
git commit -m "perf(build): cache WebP encodes across builds in .webp-cache/"
```

---

### Task 2: Extract shared build context to `lib/site.py` (W3)

**Files:**
- Create: `lib/site.py`
- Modify: `build.py` (delete moved blocks; import from `lib.site`)

**Interfaces:**
- Produces (importable from `lib.site`, names unchanged): `env`,
  `output_dir`, `pages`, `structures`, `articles`, `members_by_id`,
  `_member_data`, `_CENTER_SECTIONS`, and any other module-level names the
  moved blocks defined.

- [ ] **Step 1: Snapshot** — run the diff gate's BEFORE command.

- [ ] **Step 2: Create `lib/site.py`** holding, verbatim, these
module-level pieces of `build.py` (line numbers as of Task 1's commit;
locate by content, not number):

1. The import of `build_member_data` / `seo_helpers` / `config`, and the
   `_member_data = build_member_data()` call (`build.py:11-18`).
2. The Jinja `env = Environment(...)` setup and `env.globals[...]` SEO
   registrations (`build.py:20-28`).
3. `with open("contents/pages.json") ...` → `pages` (`~line 184`),
   `output_dir = OUTPUT_DIR` (`~188`), the `structures = {}` +
   `_SUBPAGE_JSON_SOURCES` loading loop (`~192-213`).
4. `_CENTER_SECTIONS` and `members_by_id = _member_data['members_by_id']`
   plus any adjacent roster-derived globals (`~215-227`).
5. The `articles = {}` + `_PAGE_BODY_MD` loop, the
   `contents/news/articles/*.md` loading loop, and the member-markdown loop
   (`~339-369`).

**Do NOT move** the page-type preprocessing loops (news image scan
`~229-251`, publications `~252-319`, projects `~320-338`) — Tasks 3–5 turn
those into `prepare()` functions. `lib/site.py` needs its own stdlib
imports (`os`, `json`, `markdown`, …) — copy the relevant lines from
`build.py`'s header.

- [ ] **Step 3: Rewire `build.py`.** Delete the moved blocks; at the top
add:

```python
from lib.site import (env, output_dir, pages, structures, articles,
                      members_by_id, _member_data, _CENTER_SECTIONS)
```

(Extend the tuple with any other moved name `build.py` still references —
run `python build.py` and chase `NameError`s until clean. The page-type
preprocessing loops left behind in `build.py` mutate `structures` in place,
which works unchanged since the dict object is shared.)

- [ ] **Step 4: Diff gate** — AFTER command. Expected: `IDENTICAL`.

- [ ] **Step 5: Commit.**

```bash
git add lib/site.py build.py
git commit -m "refactor(build): extract shared env/data loading to lib/site.py"
```

---

### Task 3: Extract `lib/slugs.py` + `lib/publications.py` (W3)

**Files:**
- Create: `lib/slugs.py`, `lib/publications.py`
- Modify: `build.py`

**Interfaces:**
- Consumes: `lib.site` globals from Task 2.
- Produces: `lib.slugs.slugify_title(text, max_words=7)`;
  `lib.publications` exporting `bold_author`, `get_pub_sort_key`,
  `pub_year4`, `pub_slug`, `generate_bibtex`, `prepare()` (no args),
  `render_publication_pages()`.

- [ ] **Step 1: Snapshot** (diff-gate BEFORE command).

- [ ] **Step 2: Create `lib/slugs.py`** — move `slugify_title`
(`build.py:95`) verbatim, with the stdlib imports it uses (`re`).

- [ ] **Step 3: Create `lib/publications.py`** — move verbatim:
`bold_author` (31), `get_pub_sort_key` (55), `pub_year4` (89), `pub_slug`
(101), `_bibtex_authors` (119), `_bibtex_key` (133), `generate_bibtex`
(149), `_BIBTEX_STOPWORDS`/`_MONTHS3` (84-88), the two module-level
publications preprocessing blocks (`~252-319`) wrapped as:

```python
def prepare():
    """Module-level publications preprocessing moved verbatim from build.py.
    Mutates the shared structures dict in place."""
    # <the two `if 'publications' in structures:` blocks, re-indented>
```

and `render_publication_pages` (612). Header imports:

```python
import os
import re
from markupsafe import Markup, escape
from lib.site import env, output_dir, structures, articles, members_by_id
from lib.slugs import slugify_title
```

(adjust to exactly what the moved code references — chase `NameError`s.
Never import from `build.py` into a `lib/` module — that would be
circular; if a moved function needs a helper still living in `build.py`,
move that helper here too and re-import it into `build.py`.)

- [ ] **Step 4: Rewire `build.py`.** Delete moved code. Import
`from lib import publications` and `from lib.slugs import slugify_title`
(other page types still use `slugify_title` until their own tasks). In
`__main__`, insert `publications.prepare()` **before** any `render_*`
call (preserving the original module-level execution order), and change
the call `render_publication_pages()` → `publications.render_publication_pages()`.
If projects' preprocessing (still in `build.py`) uses `pub_slug` or pub
helpers, import them: `from lib.publications import pub_slug`.

- [ ] **Step 5: Diff gate** — expect `IDENTICAL`.

- [ ] **Step 6: Commit.**

```bash
git add lib/slugs.py lib/publications.py build.py
git commit -m "refactor(build): extract publications + slug helpers to lib/"
```

---

### Task 4: Extract `lib/news.py` (W3)

**Files:**
- Create: `lib/news.py`
- Modify: `build.py`

**Interfaces:**
- Produces: `lib.news` exporting `news_slug_from_pagelink`, `prepare()`,
  `render_news_pages()`.

- [ ] **Step 1: Snapshot.**

- [ ] **Step 2: Create `lib/news.py`** — move verbatim:
`news_slug_from_pagelink` (179), `_NEWS_IMG_EXTS` + the news image-scan
loop (`~228-241`) and `_news_years` loop (`~242-251`) together wrapped as
`def prepare():` (same pattern as Task 3), and `render_news_pages` (518).
Imports mirror Task 3's pattern (`from lib.site import env, output_dir,
structures, articles`; plus stdlib/markdown as the moved code needs).
If `_news_years` (or other names built by the loop) is referenced by
code still in `build.py` or by templates via a render context built
elsewhere, export it as a module attribute and import it where needed.

- [ ] **Step 3: Rewire `build.py`** — delete moved code, add
`from lib import news`, call `news.prepare()` in `__main__` **before**
`publications.prepare()` (original file order: news scan ran first), and
`render_news_pages()` → `news.render_news_pages()`.

- [ ] **Step 4: Diff gate** — expect `IDENTICAL`.

- [ ] **Step 5: Commit.**

```bash
git add lib/news.py build.py
git commit -m "refactor(build): extract news pipeline to lib/news.py"
```

---

### Task 5: Extract `lib/projects.py` (W3)

**Files:**
- Create: `lib/projects.py`
- Modify: `build.py`

**Interfaces:**
- Produces: `lib.projects` exporting `proj_slug`, `prepare()`,
  `render_project_pages()`.

- [ ] **Step 1: Snapshot.**

- [ ] **Step 2: Create `lib/projects.py`** — move verbatim: `proj_slug`
(108), `_funder_bucket` (292), the `if 'projects' in structures:` block
(`~320-338`) as `def prepare():`, and `render_project_pages` (654).
Imports: `from lib.site import env, output_dir, structures, articles`,
`from lib.slugs import slugify_title`, and (if the moved code references
publication helpers, e.g. resolving related publications by citationId)
`from lib.publications import ...` as needed.

- [ ] **Step 3: Rewire `build.py`** — delete moved code, add
`from lib import projects`, call `projects.prepare()` in `__main__` after
`publications.prepare()` (original order), and
`render_project_pages()` → `projects.render_project_pages()`.

- [ ] **Step 4: Diff gate** — expect `IDENTICAL`.

- [ ] **Step 5: Commit.**

```bash
git add lib/projects.py build.py
git commit -m "refactor(build): extract projects pipeline to lib/projects.py"
```

---

### Task 6: Extract `lib/members.py` (W3)

**Files:**
- Create: `lib/members.py`
- Modify: `build.py`

**Interfaces:**
- Produces: `lib.members` exporting `render_member_pages()`,
  `compress_member_images()`.

- [ ] **Step 1: Snapshot.**

- [ ] **Step 2: Create `lib/members.py`** — move verbatim:
`render_member_pages` (409) and `compress_member_images` (1096). The
latter references `members_img_sizes`, `lazy_img_sizes`, and
`convert_to_webp`, which are still in `build.py` until Task 7 — to avoid
a circular import, ALSO move the size aliases `members_img_sizes = MEMBER_IMG_WIDTHS`
and `lazy_img_sizes = LAZY_IMG_WIDTHS` (`build.py:1018-1019`) into
`lib/members.py` temporarily (Task 7 relocates them to `lib/assets.py`),
importing `MEMBER_IMG_WIDTHS, LAZY_IMG_WIDTHS` from `config` — and move
`_webp_cache_key` + `convert_to_webp` into `lib/assets.py` **now** as
Step 2b (pulling that one piece of Task 7 forward):

Create `lib/assets.py` containing only `_webp_cache_key` and
`convert_to_webp` (verbatim from Task 1), with imports:

```python
import os
import shutil
import hashlib
from PIL import Image, ImageOps
from config import WEBP_QUALITY, WEBP_CACHE_DIR
```

Then `lib/members.py` uses `from lib.assets import convert_to_webp`, and
`build.py` replaces its local definitions with the same import (its other
caller `compress_and_convert_images` stays in `build.py` until Task 7).

- [ ] **Step 3: Rewire `build.py`** — delete moved code, add
`from lib import members`, `from lib.assets import convert_to_webp`;
`render_member_pages()` → `members.render_member_pages()`;
`compress_member_images()` → `members.compress_member_images()`. If
`build.py`'s remaining code references `members_img_sizes`/`lazy_img_sizes`,
import them from `lib.members` for now.

- [ ] **Step 4: Diff gate** — expect `IDENTICAL`.

- [ ] **Step 5: Commit.**

```bash
git add lib/members.py lib/assets.py build.py
git commit -m "refactor(build): extract member pages + WebP encoder to lib/"
```

---

### Task 7: Extract `lib/assets.py` (rest) + `lib/seo_site.py` (W3)

**Files:**
- Modify: `lib/assets.py` (add remaining asset functions), `lib/members.py`
  (import sizes from their final home), `build.py`
- Create: `lib/seo_site.py`

**Interfaces:**
- Produces: `lib.assets` exporting `convert_to_webp`, `copy_static()`,
  `copy_videos()`, `compress_and_convert_images()`, `members_img_sizes`,
  `lazy_img_sizes`, `_SUBPAGE_IMAGE_SOURCES`; `lib.seo_site` exporting
  `generate_sitemap()`, `validate_seo()`.

- [ ] **Step 1: Snapshot.**

- [ ] **Step 2: Complete `lib/assets.py`** — move verbatim from
`build.py`: `copy_static` (977), `copy_videos` (995), the size aliases and
`_SUBPAGE_IMAGE_SOURCES` table (`~1018-1030`, relocating the aliases put
in `lib/members.py` by Task 6 — update `lib/members.py` to
`from lib.assets import members_img_sizes, lazy_img_sizes`), and
`compress_and_convert_images` (1065). Add
`from lib.site import output_dir` and the config imports the moved code
uses (`SUBPAGE_IMG_WIDTHS`, `WEBP_LAZY_QUALITY`, …).

- [ ] **Step 3: Create `lib/seo_site.py`** — move verbatim:
`generate_sitemap` (753), `validate_seo` (889), `_check_page` (925).
Imports: `from config import SITE_URL`, `from lib.site import output_dir,
structures, pages` plus stdlib (`os`, `datetime`) and `bs4` as the moved
code needs. If `generate_sitemap` references page-type slug helpers,
import them from their new `lib/` homes.

- [ ] **Step 4: Rewire `build.py`** — delete moved code; imports:
`from lib import assets, seo_site`; call sites in `__main__`:
`copy_static()` → `assets.copy_static()`, `copy_videos()` →
`assets.copy_videos()`, `generate_sitemap()` → `seo_site.generate_sitemap()`,
`validate_seo()` → `seo_site.validate_seo()`,
`compress_and_convert_images()` → `assets.compress_and_convert_images()`.

- [ ] **Step 5: Diff gate** — expect `IDENTICAL`.

- [ ] **Step 6: Commit.**

```bash
git add lib/assets.py lib/seo_site.py lib/members.py build.py
git commit -m "refactor(build): extract asset pipeline and sitemap/SEO to lib/"
```

---

### Task 8: `build.py` orchestrator trim + docs (W3)

**Files:**
- Modify: `build.py`, `STRUCTURE.md`

**Interfaces:**
- Consumes: all Task 2–7 modules.
- Produces: final `build.py` shape relied on by Task 9's watcher.

- [ ] **Step 1: Snapshot.**

- [ ] **Step 2: Trim `build.py`.** After Tasks 2–7 it should contain only:
imports, `render_templates` (the top-level page renderer, deliberately kept
here per the spec), and the `__main__` block shaped like:

```python
if __name__ == "__main__":
    import sys
    if "--force-images" in sys.argv and os.path.isdir(WEBP_CACHE_DIR):
        shutil.rmtree(WEBP_CACHE_DIR)
    # Clean output dir: stale-page guarantee (see spec W2).
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    news.prepare()
    publications.prepare()
    projects.prepare()

    print("Rendering templates...")
    render_templates()
    print("Rendering member pages...")
    members.render_member_pages()
    print("Rendering news item pages...")
    news.render_news_pages()
    print("Rendering publication detail pages...")
    publications.render_publication_pages()
    print("Rendering project detail pages...")
    projects.render_project_pages()
    print("Copying static assets...")
    assets.copy_static()
    print("Copying videos...")
    assets.copy_videos()
    print("Generating sitemap...")
    seo_site.generate_sitemap()
    print("\nValidating SEO...")
    seo_site.validate_seo()
    print("Compressing images and converting to WebP format...")
    assets.compress_and_convert_images()
    members.compress_member_images()
    print("Build complete!")
```

Delete now-unused imports; `wc -l build.py` should be ≤ ~300 (spec target
~250; a small overrun from `render_templates` is acceptable).

- [ ] **Step 3: Update `STRUCTURE.md`** — replace the `lib/` tree listing
with the new modules, one line each mirroring the existing comment style
(`site.py # shared Jinja env + content loading`, `slugs.py`,
`publications.py`, `news.py`, `projects.py`, `members.py`, `assets.py`,
`seo_site.py`, plus the pre-existing `excel_to_content.py`,
`seo_helpers.py`).

- [ ] **Step 4: Diff gate** — expect `IDENTICAL`. Then full validators:

```bash
python validate_design_tokens.py && python validate_site.py
```

- [ ] **Step 5: Commit.**

```bash
git add build.py STRUCTURE.md
git commit -m "refactor(build): reduce build.py to a thin orchestrator"
```

---

### Task 9: Live-reload dev server (W5)

**Files:**
- Create: `dev_server.py` (repo root, matching the `build.py`/`validate_*.py`
  top-level-script convention)
- Modify: `requirements.txt`, `Makefile`, `STRUCTURE.md` (one line)

**Interfaces:**
- Consumes: `python build.py` CLI (Task 8 shape) — invoked as a subprocess,
  so build failures never kill the watcher.

- [ ] **Step 1: Add the dependency.** In `requirements.txt` append:

```
livereload>=2.7.1
```

Then `pip install -r requirements.txt`.

- [ ] **Step 2: Create `dev_server.py`:**

```python
"""Watch-rebuild-reload dev loop: `make dev`, then edit and save.

Watches source trees, reruns build.py on change (incremental thanks to the
WebP encode cache), and serves docs/ with livereload's injected refresh
script. Build errors print to this terminal and the previous good output
keeps being served — fix and save again."""
import subprocess
import sys

from livereload import Server

WATCHED = ["contents/", "templates/", "static/", "lib/", "build.py", "config.py"]


def rebuild():
    subprocess.run([sys.executable, "build.py"], check=False)


if __name__ == "__main__":
    rebuild()
    server = Server()
    for path in WATCHED:
        server.watch(path, rebuild, delay=0.5)
    server.serve(root="docs", host="0.0.0.0", port=8000)
```

- [ ] **Step 3: Makefile.** Add `dev` to `.PHONY`, a help line
`@echo "make dev              - watch contents/templates/static, rebuild + live-reload at :8000"`,
and:

```make
dev:
	python dev_server.py
```

Add the one-line `dev_server.py` entry to `STRUCTURE.md`'s root listing.

- [ ] **Step 4: Verify manually.** Run `make dev`, open
`http://localhost:8000`, edit a visible string in
`templates/home/about.html`, save — the browser must auto-refresh with the
change within a few seconds. Revert the template edit. Also verify a
syntax error in a template prints a traceback but the server stays up.

- [ ] **Step 5: Commit.**

```bash
git add dev_server.py requirements.txt Makefile STRUCTURE.md
git commit -m "feat(dev): live-reload dev server via make dev"
```

---

### Task 10: Gate the home-page sky animation (W1)

**Files:**
- Modify: `static/js/script.js:152-209` (`animateHpTheSky`)

**Interfaces:**
- Consumes: `.hp-the-sky-bg/-back/-front` SVG polygons in the homepage hero
  (from `templates/partials/home.svg`).

- [ ] **Step 1: Baseline measurement.** `make serve`, open
`http://localhost:8000` in Chrome, DevTools → Performance Monitor. Record
CPU % idling (a) at the top of the page, (b) scrolled to mid-page with the
hero off-screen. Note both in the eventual PR description.

- [ ] **Step 2: Replace the tail of `animateHpTheSky`.** Keep lines
154-197 (queriers, state, `easeInOut`, `animate()`) unchanged, except add
directly after the three `querySelector` lines:

```js
    if (!hpTheSkyBg || !hpTheSkyBack || !hpTheSkyFront) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
```

Then replace the existing block from `document.addEventListener('visibilitychange', ...)`
through `rafId = requestAnimationFrame(animate);` (current lines 199-207)
with:

```js
    // Two gates share one start/stop pair so they can't double-start the
    // loop (same single-source-of-truth idea as resBlockAniRunning):
    // visibilitychange pauses in background tabs; the IntersectionObserver
    // stops the loop entirely while the hero is scrolled off-screen.
    let heroInView = true;

    function startLoop() {
        if (!rafId && heroInView && !document.hidden) {
            start = null;
            rafId = requestAnimationFrame(animate);
        }
    }
    function stopLoop() {
        if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    }

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) { stopLoop(); } else { startLoop(); }
    });

    new IntersectionObserver((entries) => {
        heroInView = entries[0].isIntersecting;
        if (heroInView) { startLoop(); } else { stopLoop(); }
    }).observe(hpTheSkyBg.ownerSVGElement);

    startLoop();
```

- [ ] **Step 3: Verify.** Rebuild (`python build.py`), reload, and check in
DevTools:
1. Hero on-screen: animation runs (building bobs) — unchanged look.
2. Scroll to mid-page: Performance Monitor CPU drops; no rAF activity
   (Performance tab recording shows no `animate` frames).
3. Scroll back up: animation resumes.
4. Background the tab and return: resumes (existing behaviour preserved).
5. DevTools → Rendering → "Emulate CSS prefers-reduced-motion: reduce",
   reload: building never moves.
Record the after-numbers alongside Step 1's.

- [ ] **Step 4: Commit.**

```bash
git add static/js/script.js
git commit -m "perf(home): gate sky animation on viewport + reduced motion"
```

---

### Task 11: RWD breakpoint registry validator + policy (W4)

**Files:**
- Modify: `validate_design_tokens.py`, `DESIGN_RULES/responsive.md`

**Interfaces:**
- Consumes: the check-function convention in `validate_design_tokens.py`
  (`check_*() -> list[str]` registered in `main()`'s tuple).

- [ ] **Step 1: Add the check.** In `validate_design_tokens.py`, near the
other constants add:

```python
# Sanctioned @media width breakpoints — DESIGN_RULES/responsive.md: the
# tier edges plus the component-local registry. Adding a breakpoint means
# updating BOTH the registry table there and this set, in the same PR.
SANCTIONED_BREAKPOINTS = {"37.5rem", "48rem", "56rem", "64rem", "64.0625rem", "90rem"}
WIDTH_QUERY_RE = re.compile(r"\((?:max|min)-width:\s*([0-9.]+(?:rem|px|em|ch))\s*\)")
```

and the check function (following the file's existing pattern):

```python
def check_breakpoint_registry():
    """Rule 6: every width-based @media breakpoint must come from the
    sanctioned set (tier edges + responsive.md's component-local registry),
    so viewport behaviour changes stay deliberate and documented."""
    failures = []
    for css in sorted(CSS_DIR.glob("*.css")):
        for lineno, line in enumerate(css.read_text().splitlines(), 1):
            if "@media" in line:
                for match in WIDTH_QUERY_RE.finditer(line):
                    breakpoint = match.group(1)
                    if breakpoint not in SANCTIONED_BREAKPOINTS:
                        failures.append(
                            f"{css.name}:{lineno}: @media width {breakpoint} is not in the "
                            f"sanctioned registry — see DESIGN_RULES/responsive.md "
                            f"(component-local breakpoints) and SANCTIONED_BREAKPOINTS")
    return failures
```

Register it in `main()`'s tuple:

```python
        ("breakpoint registry", check_breakpoint_registry),
```

- [ ] **Step 2: Green test.** `python validate_design_tokens.py` —
expected: `breakpoint registry     OK` and exit 0 (proves the sanctioned
set covers all current CSS).

- [ ] **Step 3: Red test.** Temporarily append to `static/css/general.css`:

```css
@media (max-width: 50rem) { .never-ships { display: none; } }
```

Run the validator — expected: 1 failure naming `general.css` and `50rem`,
exit 1. **Revert the temporary edit** and re-run to confirm green.

- [ ] **Step 4: Update the docstring** at the top of
`validate_design_tokens.py` — the numbered invariant list gains:

```
  6. Every width-based @media breakpoint comes from the sanctioned registry
     (tier edges + responsive.md § component-local breakpoints), so a new
     breakpoint is a documented decision, not an accident.
```

- [ ] **Step 5: Extend `DESIGN_RULES/responsive.md`.** After the
component-local breakpoint registry table, add:

```markdown
The registry is enforced: `validate_design_tokens.py` (invariant 6) fails
the build on any width-based `@media` breakpoint outside the tier edges
(`37.5rem`, `64rem`, `90rem`) and this table. To add one, extend the table
here and `SANCTIONED_BREAKPOINTS` in the validator in the same PR.

## Preferred responsive tools for touched components

When you touch a component, prefer (in order):

1. **`clamp(min, preferred-vw, max)`** for hero-tier text instead of a new
   breakpoint override (extends [R-1]; `.news-item-title` is the model).
2. **Container queries** for components rendered in more than one width
   context (member cards, publication rows) — they remove the
   "breaks when placed in a narrower column" bug class entirely.
3. A registry breakpoint, only when neither of the above fits.

No proactive sweep: existing components migrate only as they're touched.
```

- [ ] **Step 6: Full check + commit.**

```bash
python build.py && python validate_design_tokens.py && python validate_site.py
git add validate_design_tokens.py DESIGN_RULES/responsive.md
git commit -m "feat(tokens): enforce the RWD breakpoint registry in the validator"
```

---

### Task 12: Repo hygiene + `MAINTENANCE.md` (W6)

**Files:**
- Delete: `contents/members/member-info.legacy.xlsx`
- Modify: `STRUCTURE.md` (remove its entry)
- Create: `MAINTENANCE.md`

- [ ] **Step 1: Prove the legacy file is unread.**

```bash
grep -rn "legacy" --include="*.py" .
```

Expected: no hit referencing `member-info.legacy.xlsx` (comments about the
"legacy pipeline" in docstrings are fine). If a code path reads it, STOP
and report instead of deleting.

- [ ] **Step 2: Delete + update docs.**

```bash
git rm contents/members/member-info.legacy.xlsx
```

In `STRUCTURE.md`, delete the line documenting
`member-info.legacy.xlsx   # Original 22-column Excel, archived read-only reference`.

- [ ] **Step 3: Create `MAINTENANCE.md`:**

```markdown
# Site maintenance — the 15-minute guide

For whoever inherits this site. Every routine task is below; none needs
more than 15 minutes. Deeper docs: [STRUCTURE.md](STRUCTURE.md) (what each
file is), [DESIGN_RULES/](DESIGN_RULES/) (visual system — read before any
CSS change), [CLAUDE.md](CLAUDE.md) (data-entry conventions), `specs/` and
`plans/` (design history).

## One-time setup

```bash
conda activate E3website        # or any Python 3.11+ env
pip install -r requirements.txt
make help                       # list all tasks
```

## Preview while editing

```bash
make dev        # http://localhost:8000 — rebuilds + refreshes on save
```

## Add a publication

1. Edit `contents/publications/publications.json` — copy the nearest
   existing entry as a template; **all entries must keep the same keys**
   (use `""` for blanks).
2. `month`/`year` = the journal **issue** date, never "available online"
   (full rule + examples in [CLAUDE.md](CLAUDE.md)).
3. `status`: `"published"` (+ a `citationId`) makes it appear on the
   public pages and member CVs; `"working"` keeps it tracked but unlisted.
4. Check it at `http://localhost:8000/publications/`.

## Add a news item

1. Add an entry to `contents/news/news.json`.
2. Body prose: `contents/news/articles/{slug}.md`, where `{slug}` is the
   last segment of the entry's `pageLink`.
3. Images: `contents/news/images/{slug}/` — `0.jpg` (or `.png`) is the
   hero; other files appear in the gallery.

## Add or update a member

1. Admin facts (name, section, batch, graduated…): one row per member in
   `contents/members/member-info.xlsx`.
2. Member-owned content: `contents/members/{webId}/` — `member.json`,
   `about.md`, `photo.jpg` (portrait, ≥800px wide). To ask a member for
   their folder, send them the skeleton: `make package-member MEMBER=<webId>`.
3. `python validate_member.py` (also runs in the build) flags folder
   mistakes.

## Ship it

```bash
make build && make audit-site && make tokens   # what CI will run
git checkout -b my-change && git add <files> && git commit && git push
```

Open a PR into **`source`**. CI builds and validates every PR; merging to
`source` auto-deploys to GitHub Pages (`gh-pages` branch) — never edit
`docs/` or `gh-pages` by hand.

## When something breaks

- Build fails → the traceback names the content file; fix and rerun.
- `make tokens` fails → a CSS change broke a design-token invariant; the
  message points at the rule in `DESIGN_RULES/`.
- `make audit-site` fails → dead link / missing alt / SEO regression in
  the built output; the message names the page.
- Weird image staleness → `make clean-cache && make build`.
```

- [ ] **Step 4: Verify.** `python build.py && python validate_site.py` —
green proves nothing read the deleted file. Skim `MAINTENANCE.md` and
confirm every command in it exists in `Makefile`/repo (`make dev`,
`make package-member`, `validate_member.py`, `make clean-cache`).

- [ ] **Step 5: Commit.**

```bash
git add MAINTENANCE.md STRUCTURE.md
git commit -m "docs: successor maintenance guide; drop archived legacy roster"
```

---

## Final gate (after all tasks)

- [ ] `make clean && make clean-cache && python build.py --force-images` —
  full cold build green.
- [ ] `python validate_design_tokens.py && python validate_site.py &&
  python validate_member.py` — all green.
- [ ] Push branch; open PR to `source` titled
  `Approach A hardening: build cache, lib/ split, animation gating, RWD guardrails`
  with the W1 before/after CPU numbers and the cold/warm build timings in
  the description. CI (build + validators) must pass.
