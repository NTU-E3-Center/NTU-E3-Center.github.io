# Brand Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the E3 Center visual identity so the site reads cleaner without any change a visitor could name — by documenting the colour system's three layers, fixing the contrast failures that audit exposes, retiring a half-finished token migration, and making the skewed-block rule describe what the design actually wants.

**Architecture:** Pure CSS + documentation refactor against the existing three-layer token system in `static/css/general.css`. No template, layout, or JS changes. A new root-level `validate_design_tokens.py` (mirroring the existing `validate_member.py`) provides the test harness: it asserts contrast, alias, and token-layer invariants so every task has a real red→green cycle instead of eyeballing.

**Tech Stack:** Vanilla CSS with custom properties and `color-mix()`, Jinja2 templates, Python 3 build script (`build.py`), conda env at `~/miniconda3/envs/E3website/bin/python`.

## Global Constraints

- Branch: `brand-refinement`. Never push to `source` from this plan.
- Every task ends with a local verification on `http://localhost:8001` before commit.
- `python build.py` must finish with **0 SEO warnings** after every task.
- The three animated background SVG tiles and all `sprite.svg` artwork stay byte-identical — this is the user's one explicit off-limits item.
- No new typeface, no hue changes to primitives, no change to `--page-bg-color`, no layout/IA changes.
- Bump the relevant `?v=` query on any stylesheet touched, in **all five** templates that reference it (`templates/base.html` plus the four standalone detail templates), or detail pages will serve stale CSS. **Never hardcode the current version number** — tasks run in sequence and each bump invalidates the next task's hardcoded value. Always increment whatever is there, using this command (substitute `general.css` or `subpage.css` for `ASSET`):

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - ASSET <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding="utf-8").read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, "w", encoding="utf-8").write(bumped)
        print("bumped", asset, "in", f)
EOF
```
- Commit messages use conventional prefixes; never add `Co-Authored-By` trailers.

---

# Phase 1 — invisible changes (§1, §3, §4)

If anything in Phase 1 changes what a page looks like, that is a bug, not the intent. The one deliberate exception is that three category label colours get slightly darker, because they currently fail WCAG AA.

---

### Task 1: Add the design-token audit harness

**Files:**
- Create: `validate_design_tokens.py`

**Interfaces:**
- Produces: `main() -> int` (0 = pass, 1 = failures), and three check functions
  `check_category_contrast()`, `check_deprecated_aliases()`, `check_primitive_leakage()`,
  each returning `list[str]` of failure messages. Tasks 2–4 consume this by running the script.

- [ ] **Step 1: Write the harness**

Create `validate_design_tokens.py`:

```python
"""Design-token invariants for the E3 Center site.

Mirrors validate_member.py: run standalone, exit non-zero on failure.
Three invariants, each mapping to a rule in DESIGN_RULES/:

  1. Every --cat-*-text colour clears WCAG AA (4.5:1) both on its own tinted
     badge background and on the page background (the phone bare-label case).
  2. No deprecated --fs-* alias is referenced anywhere.
  3. No component rule consumes a raw primitive (--r-*, --*-light, --house-*)
     directly; primitives are reachable only through a semantic alias or the
     illustration utility layer.
"""
import re
import sys
from pathlib import Path

CSS_DIR = Path("static/css")
GENERAL = CSS_DIR / "general.css"
PAGE_BG = "#f7fafb"
AA = 4.5

# Deprecated aliases retired by the v3 token ladder.
DEPRECATED_ALIASES = [
    "fs-display-xl", "fs-display-l", "fs-display-m", "fs-display-s",
    "fs-heading-l", "fs-heading-m", "fs-heading-s",
    "fs-body-xl", "fs-body-l", "fs-body-s",
    "fs-caption", "fs-caption-s", "fs-prose-lede", "lh-prose",
]

# Primitives: raw hues that only the illustration layer may consume directly.
PRIMITIVE_RE = re.compile(r"var\(--(r-[a-z]+|main-light|main-3-light|secondary-light|house-dark|house-light)\)")
# Selectors that ARE the illustration layer. Matched against the enclosing
# selector, never the declaration line — `.fill-r-green { fill: var(--r-green) }`
# puts the selector and the declaration on different lines.
ILLUSTRATION_SELECTOR_RE = re.compile(r"^\.(fill|stroke)-")


def _srgb(hex_colour):
    h = hex_colour.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def _luminance(hex_colour):
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
         for x in _srgb(hex_colour)]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _mix(a, b, pct_a):
    ca, cb = _srgb(a), _srgb(b)
    return "#%02x%02x%02x" % tuple(
        round(255 * (ca[i] * pct_a + cb[i] * (1 - pct_a))) for i in range(3))


def _read_root_tokens(css):
    """Map token name -> raw value string, from every :root-level declaration."""
    tokens = {}
    for name, value in re.findall(r"^\s+--([a-z0-9-]+):\s*([^;]+);", css, re.M):
        tokens.setdefault(name, value.strip())
    return tokens


def resolve(value, tokens, depth=0):
    """Resolve a token value to a #rrggbb hex string.

    Handles the three forms the stylesheet actually uses: a literal hex, a
    var() reference, and color-mix(in srgb, <colour> N%, <colour>).
    Returns None for anything else (e.g. keywords like `transparent`).
    """
    if depth > 8:
        return None
    value = value.strip()

    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value.lower()

    var_match = re.fullmatch(r"var\(--([a-z0-9-]+)\)", value)
    if var_match:
        inner = tokens.get(var_match.group(1))
        return resolve(inner, tokens, depth + 1) if inner else None

    if value.startswith("color-mix("):
        inner = value[len("color-mix("):].rstrip(")")
        parts = [p.strip() for p in _split_top_level(inner)]
        if len(parts) == 3 and parts[0] == "in srgb":
            first, second = parts[1], parts[2]
            pct_match = re.search(r"(\d+(?:\.\d+)?)%", first)
            if not pct_match:
                return None
            pct = float(pct_match.group(1)) / 100
            c1 = resolve(first[:pct_match.start()].strip(), tokens, depth + 1)
            c2 = resolve(re.sub(r"\s*\d+(?:\.\d+)?%", "", second).strip(), tokens, depth + 1)
            if c1 and c2:
                return _mix(c1, c2, pct)
    return None


def _split_top_level(text):
    """Split on commas that are not inside parentheses."""
    parts, depth, current = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    return parts


def check_category_contrast():
    css = GENERAL.read_text(encoding="utf-8")
    tokens = _read_root_tokens(css)
    failures = []
    for name in sorted(t for t in tokens if t.startswith("cat-") and t.endswith("-text")):
        base = name[:-len("-text")]
        text_hex = resolve(tokens[name], tokens)
        base_hex = resolve(tokens.get(base, ""), tokens)
        if not text_hex or not base_hex:
            failures.append(f"--{name}: could not resolve to a hex colour")
            continue
        # Badge tint: the base hue mixed over white. 13% is the listing default;
        # faculty uses 22% and outreach 14%. Test the lightest (weakest) case.
        tint = _mix(base_hex, "#ffffff", 0.13)
        on_tint = contrast(text_hex, tint)
        on_page = contrast(text_hex, PAGE_BG)
        if min(on_tint, on_page) < AA:
            failures.append(
                f"--{name} ({text_hex}): {on_tint:.2f}:1 on tint, "
                f"{on_page:.2f}:1 on page bg — below AA {AA}:1")
    return failures


def check_deprecated_aliases():
    failures = []
    for css_file in sorted(CSS_DIR.glob("*.css")):
        for lineno, line in enumerate(css_file.read_text(encoding="utf-8").splitlines(), 1):
            for alias in DEPRECATED_ALIASES:
                if f"var(--{alias})" in line:
                    failures.append(f"{css_file}:{lineno}: deprecated var(--{alias})")
    return failures


def check_primitive_leakage():
    """Flag primitives used outside :root and outside the illustration layer.

    Tracks the enclosing selector stack rather than testing the declaration
    line, because a rule's selector and its declarations are on different
    lines — `.fill-r-green { fill: var(--r-green); }` is legitimate and must
    not be reported.
    """
    failures = []
    for css_file in sorted(CSS_DIR.glob("*.css")):
        depth = 0
        stack = []  # list of (depth_at_open, selector_text)
        for lineno, line in enumerate(css_file.read_text(encoding="utf-8").splitlines(), 1):
            opens, closes = line.count("{"), line.count("}")
            if opens:
                stack.append((depth, line.split("{")[0].strip()))
            exempt = any(
                sel == ":root" or ILLUSTRATION_SELECTOR_RE.match(sel)
                for _, sel in stack)
            if not exempt and PRIMITIVE_RE.search(line):
                failures.append(
                    f"{css_file}:{lineno}: component rule consumes a primitive directly "
                    f"— add a semantic alias in :root first")
            depth += opens - closes
            while stack and stack[-1][0] >= depth:
                stack.pop()
    return failures


def main():
    all_failures = []
    for label, check in (
        ("category contrast", check_category_contrast),
        ("deprecated aliases", check_deprecated_aliases),
        ("primitive leakage", check_primitive_leakage),
    ):
        failures = check()
        status = "OK" if not failures else f"{len(failures)} failure(s)"
        print(f"{label:<22} {status}")
        for failure in failures:
            print(f"    {failure}")
        all_failures.extend(failures)
    print()
    if all_failures:
        print(f"Design token check: {len(all_failures)} failure(s).")
        return 1
    print("Design token check: 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it and confirm it fails**

```bash
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py
```

Expected: exit 1, with roughly this shape —
- `category contrast` — 3 failures (`--cat-faculty-text`, `--cat-student-text`, `--cat-events-text`)
- `deprecated aliases` — 22 failures
- `primitive leakage` — about 20, in `style.css`, `subpage.css`,
  `project-item.css` and `publication-item.css`. The ~15 `.fill-*` / `.stroke-*`
  rules in `general.css` must **not** appear; if they do, the selector-stack
  logic is wrong and would send Task 3b chasing artwork.

If `category contrast` reports 0 failures, the resolver is broken — verify by hand
that `resolve()` returns `#5e8887` for `--cat-faculty-text` before continuing.

- [ ] **Step 3: Commit the harness**

```bash
git add validate_design_tokens.py
git commit -m "test(design): add design-token contrast and layering audit"
```

---

### Task 2: Fix the category label contrast failures (§1)

Three of the five `--cat-*-text` tokens fail WCAG AA. Measured values today:
`faculty #5e8887` 3.48:1 · `student #318382` 3.96:1 · `events #2b82ae` 3.82:1
(against their 13% tint; media 5.16:1 and outreach 5.10:1 already pass).

**Files:**
- Modify: `static/css/general.css` (the `--cat-*-text` block in `:root`)
- Modify: `templates/base.html`, `templates/pages/news/news-item.html`, `templates/pages/member/member.html`, `templates/pages/publications/publication-item.html`, `templates/pages/projects/project-item.html` (cache-bust `general.css`)

**Interfaces:**
- Consumes: `validate_design_tokens.py::check_category_contrast` from Task 1.
- Produces: `--cat-{faculty,student,events}-text` at AA-compliant values, consumed by `.news-row-badge` (`subpage.css`) and `.news-item-category` (`news-item.css`).

- [ ] **Step 1: Confirm the failing check**

```bash
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | head -8
```
Expected: three `--cat-*-text ... below AA 4.5:1` lines.

- [ ] **Step 2: Deepen the three failing mixes**

In `static/css/general.css`, replace these three declarations:

```css
    --cat-faculty-text:  color-mix(in srgb, var(--secondary-color) 45%, var(--main-color));
    --cat-student-text:  color-mix(in srgb, var(--r-green) 55%, var(--main-color));
    --cat-events-text:   color-mix(in srgb, var(--main-color-2) 50%, var(--main-color));
```

with:

```css
    /* Hue percentages are set by contrast, not taste: each is the highest
       proportion of its hue that still clears WCAG AA (4.5:1) against both
       the 13% badge tint and the page background. Verified by
       validate_design_tokens.py — do not raise these without re-running it. */
    --cat-faculty-text:  color-mix(in srgb, var(--secondary-color) 22%, var(--main-color));
    --cat-student-text:  color-mix(in srgb, var(--r-green) 40%, var(--main-color));
    --cat-events-text:   color-mix(in srgb, var(--main-color-2) 35%, var(--main-color));
```

- [ ] **Step 3: Verify the check passes**

```bash
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | head -4
```
Expected: `category contrast          OK`

If any of the three still fails, lower that hue's percentage by 5 and re-run.

- [ ] **Step 4: Cache-bust and rebuild**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - general.css <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding='utf-8').read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, 'w', encoding='utf-8').write(bumped)
EOF
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep -E "SEO check|error"
```
Expected: `SEO check: 0 warnings (0 errors).`

- [ ] **Step 5: Verify visually on localhost**

Open `http://localhost:8001/news/` and one news detail page. The category labels
(STUDENTS / EVENTS / FACULTY) should be marginally deeper in tone and still
clearly hue-distinct from one another. Nothing else should differ.

- [ ] **Step 6: Commit**

```bash
git add static/css/general.css templates/base.html templates/pages/news/news-item.html templates/pages/member/member.html templates/pages/publications/publication-item.html templates/pages/projects/project-item.html
git commit -m "fix(color): bring category label colours up to WCAG AA"
```

---

### Task 3: Retire sky as a text and focus colour (§1)

`--main-color-2` (`#4caedd`) measures 2.38:1 on the page background — unusable
for text and too weak for a focus indicator. It has 35 references; 12 set `color`,
several set focus-ring `outline`, and the rest are illustration fills or tints.

**Files:**
- Modify: `static/css/general.css` (add `--accent-ink` to `:root`; fix `:focus-visible` at line ~99)
- Modify: `static/css/subpage.css` (lines ~405, ~1461, ~1805, ~2068, ~2179)
- Modify: `static/css/project-item.css` (lines ~51, ~204, ~246, ~264, ~309, ~411, ~458, ~502, ~508)
- Modify: `static/css/publication-item.css` (lines ~32, ~79, ~93)
- Modify: the five templates (cache-bust)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `--accent-ink` — sky deepened to `#21749f`, the semantic token any
  component uses when it needs sky *as text*. Task 5 documents it in `color.md`.

- [ ] **Step 1: Add the semantic token**

In `static/css/general.css`, immediately after the `--cat-*-text` block, add:

```css
    /* Sky (--main-color-2) is 2.38:1 on the page background — fine as an
       illustration fill or a tint, unusable as text. --accent-ink is sky
       deepened toward navy to the point where it clears AA (4.60:1 on a 13%
       sky tint, 4.93:1 on the page background). Components that want "sky,
       but as text" use this; none use --main-color-2 for a colour or an
       outline. */
    --accent-ink: color-mix(in srgb, var(--main-color-2) 35%, var(--main-color));
```

- [ ] **Step 2: List every site to change**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
grep -rn "var(--main-color-2)" static/css/ | grep -E "^\S+:[0-9]+:\s*(color|outline):" 
```
Expected: about 18 lines across `subpage.css`, `project-item.css`,
`publication-item.css`, and `general.css`.

- [ ] **Step 3: Rewrite text uses to --accent-ink**

For every line the previous step listed that sets `color:`, replace
`var(--main-color-2)` with `var(--accent-ink)`:

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re
from pathlib import Path
for path in ("static/css/subpage.css", "static/css/project-item.css",
             "static/css/publication-item.css"):
    p = Path(path)
    out = []
    for line in p.read_text(encoding="utf-8").splitlines(keepends=True):
        if re.match(r"\s*color:\s*var\(--main-color-2\);", line):
            line = line.replace("var(--main-color-2)", "var(--accent-ink)")
        out.append(line)
    p.write_text("".join(out), encoding="utf-8")
    print("rewrote", path)
EOF
```

Then handle the one blended case by hand — `static/css/publication-item.css:79`
currently reads:

```css
    color: color-mix(in srgb, var(--main-color) 55%, var(--main-color-2) 45%);
```

Replace it with:

```css
    color: var(--accent-ink);
```

- [ ] **Step 4: Rewrite focus rings to navy**

Focus indicators must reach 3:1; sky is 2.38:1. Navy is 7.66:1 and is already
what most of the site uses, so this also removes an inconsistency. Replace
`var(--main-color-2)` with `var(--main-color)` on every `outline:` and
`outline-color:` line found in Step 2:

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re
from pathlib import Path
for path in ("static/css/general.css", "static/css/subpage.css",
             "static/css/project-item.css"):
    p = Path(path)
    out = []
    for line in p.read_text(encoding="utf-8").splitlines(keepends=True):
        if re.match(r"\s*outline(-color)?:.*var\(--main-color-2\)", line):
            line = line.replace("var(--main-color-2)", "var(--main-color)")
        out.append(line)
    p.write_text("".join(out), encoding="utf-8")
    print("rewrote focus rings in", path)
EOF
```

- [ ] **Step 5: Confirm only legitimate uses remain**

```bash
grep -rn "var(--main-color-2)" static/css/ | grep -vE "(fill|stroke|background|border-color|background-image):" | grep -v ":root"
```
Expected: **no output**. Every surviving `--main-color-2` use is an illustration
fill/stroke, a tint background, or a `:root` alias definition.

- [ ] **Step 6: Rebuild and verify**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - general.css <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding="utf-8").read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, "w", encoding="utf-8").write(bumped)
EOF
~/miniconda3/envs/E3website/bin/python - subpage.css <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding="utf-8").read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, "w", encoding="utf-8").write(bumped)
EOF
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep -E "SEO check|error"
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | head -4
```
Expected: `SEO check: 0 warnings (0 errors).` and `category contrast          OK`.

- [ ] **Step 7: Verify visually on localhost**

Check `http://localhost:8001/projects/2026-sofc-ai-data-centers/`,
`http://localhost:8001/publications/`, and `http://localhost:8001/members/`.
Status pills, role badges, tag chips, author links and partner links should read
deeper blue but keep their shape and tint. Tab through the page — focus rings are
navy and clearly visible.

- [ ] **Step 8: Commit**

```bash
git add static/css/general.css static/css/subpage.css static/css/project-item.css static/css/publication-item.css templates/base.html templates/pages/news/news-item.html templates/pages/member/member.html templates/pages/publications/publication-item.html templates/pages/projects/project-item.html
git commit -m "fix(color): retire sky as a text and focus colour, add --accent-ink"
```

---

### Task 3b: Give the remaining primitives semantic aliases (§1)

`check_primitive_leakage` reports ~20 component rules consuming raw `--r-*`
hues. They fall into three meanings, none of which has a name today: publication
and project *status* (green = published/available), an *alert* state (red), and
the three *research fields* (Energy / Economics / Environment), whose colours are
already a documented convention in `layout.md` but only as raw hues.

**Files:**
- Modify: `static/css/general.css` (add aliases to `:root`)
- Modify: `static/css/style.css`, `static/css/subpage.css`, `static/css/project-item.css`, `static/css/publication-item.css`
- Modify: the five templates (cache-bust)

**Interfaces:**
- Consumes: `validate_design_tokens.py::check_primitive_leakage` from Task 1.
- Produces: `--status-ok`, `--status-ok-text`, `--status-alert`, `--status-alert-text`, `--field-energy`, `--field-economics`, `--field-environment` — the only tokens components may use for these meanings.

- [ ] **Step 1: Confirm the failing check and read the sites**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | grep "consumes a primitive"
```
Expected: ~20 lines, none of them in `general.css`.

- [ ] **Step 2: Add the semantic aliases**

In `static/css/general.css`, directly after the `--accent-ink` declaration added
in Task 3, add:

```css
    /* Status and research-field semantics. Components use these names, never the
       raw --r-* primitive behind them, so the meaning is greppable and the hue
       can change in one place. The -text variants are deepened to clear WCAG AA
       against their own tinted backgrounds — same discipline as --cat-*-text. */
    --status-ok:            var(--r-green);
    --status-ok-text:       color-mix(in srgb, var(--r-green) 40%, var(--main-color));
    --status-alert:         var(--r-red);
    --status-alert-text:    color-mix(in srgb, var(--r-red) 40%, var(--main-color));
    --field-energy:         var(--r-yellow);
    --field-economics:      var(--r-orange);
    --field-environment:    var(--r-green);
```

- [ ] **Step 2b: Normalise `--cat-outreach` to a raw hue**

Its four siblings are raw primitives (`--cat-student: var(--r-green)`), but
`--cat-outreach` is `color-mix(in srgb, var(--r-orange) 85%, #000)` — darkened,
which is the badge **text** tier's job. The token is currently unused (the
outreach badge tints with raw `--r-orange` directly), so this is a zero-change
correction that makes Step 3's substitution safe. In `static/css/general.css`:

```css
    --cat-outreach:      var(--r-orange);
```

Confirm it really is unused before changing it:

```bash
grep -rn "var(--cat-outreach)" static/css/ | grep -v ":root"
```
Expected: no output. If it *is* used somewhere, stop — changing the value would
alter that surface, and the substitution in Step 3 needs rethinking.

- [ ] **Step 3: Rewrite the component rules**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re
from pathlib import Path

# Field glyph colours (style.css) — exact, single-line rules.
style = Path("static/css/style.css")
s = style.read_text(encoding="utf-8")
s = s.replace(".field-energy    { color: var(--r-yellow); }",
              ".field-energy    { color: var(--field-energy); }")
s = s.replace(".field-economics { color: var(--r-orange); }",
              ".field-economics { color: var(--field-economics); }")
s = s.replace(".field-environment { color: var(--r-green); }",
              ".field-environment { color: var(--field-environment); }")
style.write_text(s, encoding="utf-8")
print("rewrote field glyph colours")

# Status colours: green -> --status-ok*, red -> --status-alert*.
# The hand-rolled `color-mix(--r-X N%, #darkhex)` text colours all become the
# corresponding -text token, which is contrast-checked centrally.
for path in ("static/css/subpage.css", "static/css/project-item.css",
             "static/css/publication-item.css"):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"color-mix\(in srgb, var\(--r-green\) \d+%, #1a3d2e\)",
                  "var(--status-ok-text)", text)
    text = re.sub(r"color-mix\(in srgb, var\(--r-red\) \d+%, #4a1818\)",
                  "var(--status-alert-text)", text)
    text = text.replace("var(--r-green)", "var(--status-ok)")
    text = text.replace("var(--r-red)", "var(--status-alert)")
    text = text.replace("var(--r-orange)", "var(--cat-outreach)")
    p.write_text(text, encoding="utf-8")
    print("rewrote status colours in", path)
EOF
```

Note the last substitution: `subpage.css:829` tints with `--r-orange`, and that
rule is the news Education-and-Outreach badge — it should consume the existing
`--cat-outreach` token rather than a new one. Verify that line reads
`color-mix(in srgb, var(--cat-outreach) 14%, transparent)` afterwards; if the
rule turns out to be something other than the outreach badge, give it its own
semantic alias instead.

- [ ] **Step 4: Verify the check passes**

```bash
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | head -6
```
Expected: `primitive leakage      OK`

- [ ] **Step 5: Rebuild and verify visually**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - general.css <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding="utf-8").read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, "w", encoding="utf-8").write(bumped)
EOF
~/miniconda3/envs/E3website/bin/python - subpage.css <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding="utf-8").read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, "w", encoding="utf-8").write(bumped)
EOF
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep -E "SEO check|error"
```
Expected: `SEO check: 0 warnings (0 errors).`

On `http://localhost:8001/publications/` and `…/projects/`, the green
"published"/"available" pills and the research-field glyph colours should look
the same or very slightly deeper. The homepage research section keeps its
yellow/orange/green field coding.

- [ ] **Step 6: Commit**

```bash
git add static/css/ templates/base.html templates/pages/news/news-item.html templates/pages/member/member.html templates/pages/publications/publication-item.html templates/pages/projects/project-item.html
git commit -m "refactor(color): name status and research-field colours as semantic tokens"
```

---

### Task 4: Retire the deprecated type aliases (§3)

Seven `--fs-*` aliases from the pre-v3 ladder still have 22 call sites.

**Files:**
- Modify: every file reported by the grep in Step 1 (expected: `style.css`, `subpage.css`, `member.css`, `news-item.css`, `project-item.css`, `publication-item.css`)
- Modify: `static/css/general.css` (delete the alias block)
- Modify: the five templates (cache-bust)

**Interfaces:**
- Consumes: `validate_design_tokens.py::check_deprecated_aliases` from Task 1.
- Produces: a single type ladder — `--fs-h1/h2/h3`, `--fs-lede/body/body-base/secondary`, `--fs-eyebrow/badge`.

- [ ] **Step 1: List the call sites**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | grep "deprecated var"
```
Expected: 22 lines.

- [ ] **Step 2: Verify each substitution is value-preserving**

The alias block in `general.css` defines these. Confirm the mapping below matches
what is actually written there before rewriting anything:

| Alias | Becomes | Why it is safe |
|---|---|---|
| `--fs-display-m` | `--fs-h1` | alias is defined as `var(--fs-h1)` |
| `--fs-heading-l` | `--fs-h2` | alias is defined as `var(--fs-h2)` |
| `--fs-heading-s` | `--fs-h3` | alias is defined as `var(--fs-h3)` |
| `--fs-body-l` | `--fs-lede` | alias is defined as `var(--fs-lede)` |
| `--fs-caption` | `--fs-secondary` | alias is defined as `var(--fs-secondary)` |
| `--fs-caption-s` | `--fs-secondary` | alias is defined as `var(--fs-secondary)` |
| `--fs-prose-lede` | `--fs-lede` | alias is defined as `var(--fs-lede)` |

```bash
grep -nE "^\s+--fs-(display|heading|body-xl|body-l|body-s|caption|prose)" static/css/general.css
```
Expected: each line shows the alias resolving to exactly the token in the table.
**If any alias resolves to something else, stop** and report it rather than
rewriting — the substitution would silently change a size.

- [ ] **Step 3: Rewrite the call sites**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - <<'EOF'
from pathlib import Path
MAP = {
    "fs-display-m": "fs-h1",
    "fs-heading-l": "fs-h2",
    "fs-heading-s": "fs-h3",
    "fs-body-l": "fs-lede",
    "fs-caption-s": "fs-secondary",
    "fs-caption": "fs-secondary",
    "fs-prose-lede": "fs-lede",
}
for p in sorted(Path("static/css").glob("*.css")):
    text = original = p.read_text(encoding="utf-8")
    for old, new in MAP.items():           # -s before bare, so ordering matters
        text = text.replace(f"var(--{old})", f"var(--{new})")
    if text != original:
        p.write_text(text, encoding="utf-8")
        print("rewrote", p)
EOF
```

Note: `fs-caption-s` is listed before `fs-caption` in `MAP` deliberately —
Python dicts preserve insertion order, and replacing the shorter name first
would corrupt the longer one.

- [ ] **Step 4: Delete the alias block**

In `static/css/general.css`, delete the whole deprecated-alias comment and its
declarations (the block beginning `/* Deprecated aliases — kept so legacy
var(--fs-*) call sites resolve` and ending at `--fs-prose-lede: var(--fs-lede);`),
and the separate `--lh-prose: var(--lh-body);` line with its comment.

Keep `--fs-prose` — it is not deprecated and the prose recipe still reads it.

- [ ] **Step 5: Verify no alias remains and nothing resolved to nothing**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py 2>&1 | head -6
grep -rn "var(--fs-display\|var(--fs-heading\|var(--fs-caption\|var(--fs-body-l\|var(--fs-body-xl\|var(--fs-body-s\|var(--lh-prose" static/css/ || echo "no deprecated aliases remain"
```
Expected: `deprecated aliases     OK`, then `no deprecated aliases remain`.

- [ ] **Step 6: Rebuild and confirm no size changed**

```bash
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep -E "SEO check|error"
```
Expected: `SEO check: 0 warnings (0 errors).`

Then on `http://localhost:8001/`, `…/members/`, `…/publications/` and one news
detail page, confirm **no text has changed size**. This task is a pure rename; a
visible size change means one of the aliases was not what the table claimed.

- [ ] **Step 7: Normalise label tracking**

The spec also calls for consistent tracking on label-tier text. Find the drift:

```bash
cd /home/jianhern/NTU-E3-Center.github.io
grep -rn "letter-spacing" static/css/*.css | grep -E "0\.0[6-9]em|0\.1[0-9]em"
```

Every rule that is an **eyebrow** (uppercase group/category label) uses
`letter-spacing: 0.14em`; every **badge** (status/category pill) uses `0.1em`.
Adjust any that differ, except the two documented exceptions: contact-info
labels stay at `0.16em`, and the phone `.news-row-badge[data-cat]` stays at
`0.08em` because it drops its pill and needs tighter tracking as bare text.

- [ ] **Step 8: Commit**

```bash
git add static/css/ templates/base.html templates/pages/news/news-item.html templates/pages/member/member.html templates/pages/publications/publication-item.html templates/pages/projects/project-item.html
git commit -m "refactor(type): retire deprecated font-size aliases for the v3 ladder"
```

---

### Task 5: Resync DESIGN_RULES to reality (§4)

**Files:**
- Modify: `DESIGN_RULES/color.md`, `DESIGN_RULES/components.md`, `DESIGN_RULES/typography.md`, `DESIGN_RULES/README.md`

**Interfaces:**
- Consumes: the token names introduced in Tasks 2–4 (`--accent-ink`, the tuned `--cat-*-text` values).
- Produces: documentation only; nothing consumes it programmatically.

- [ ] **Step 1: Add the three-layer model to `color.md`**

Replace the opening "Brand Color Tokens" table's introductory rule with a section
that names the layers. Insert immediately before the existing token table:

```markdown
## The three layers

Colour in this site is not one flat palette — it is three layers, and most
confusion about "which colours are safe to change" comes from reading them as one.

| Layer | Tokens | Consumed by |
|---|---|---|
| **Primitive** | `--r-{red,orange,yellow,green,blue,indigo,purple}`, `--main-light`, `--main-3-light`, `--secondary-light`, `--house-dark`, `--house-light`, `--main-color-3` | The illustration utility layer, and semantic aliases. **Never a component rule.** |
| **Semantic UI** | `--main-color`, `--main-bg-color`, `--page-bg-color`, `--secondary-color`, `--accent-ink`, `--link-color`, `--line-soft`, `--main-shadow-color`, `--selection-color`, `--cat-*`, `--cat-*-text` | UI components. |
| **Illustration** | the `.fill-*` / `.stroke-*` utility classes | `static/assets/sprite.svg` and inline SVG artwork only. |

> **Rule:** a UI component consumes semantic tokens only. If a component needs a
> spectrum hue, add a semantic alias first — as `--cat-student` did on top of
> `--r-green`. A raw `var(--r-*)` inside a component rule is a bug, and
> `validate_design_tokens.py` fails the build-adjacent check when it appears.

> **Why `--r-blue` looks unused:** it is referenced exactly once in CSS, by
> `.fill-r-blue`, and that utility is applied inside `sprite.svg`. Every
> primitive is load-bearing artwork. Do not "clean up" a primitive because a
> grep looks thin.
```

- [ ] **Step 2: Add the accent boundary to `color.md`**

In the "Accent Color Use" table, replace the `--main-color-2` row and add two rows:

```markdown
| `--main-color-2` (#4caedd) | Illustration fills and tinted backgrounds **only** — 2.38:1 on the page bg, so never text and never a focus ring |
| `--accent-ink` | Sky deepened to clear AA (4.93:1). The token to use when a component wants "sky, but as text" |
| `--secondary-color` (#c4c691) | Non-text accent marks only — 1.69:1, so it must never be a text fill, and never the sole signal of a state |
```

- [ ] **Step 3: Fix the stale entries in `components.md`**

Replace the "Subpage Header" table (the one listing `.breadcrumb-parent`,
`.breadcrumb-sep`, `.breadcrumb-current` at 2.75 rem) with:

```markdown
## Subpage Header (`partials/subpage-header.html` + `subpage.css` § Subpage header)

The header is one row at every width: brand + primary nav. The breadcrumb is not
in the header — it renders as `.page-trail`, the first element of the content
flow, and only on detail pages (listing pages are named by the active nav link).

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| `.hdr-nav-a` | `--fs-secondary`, `--fw-heading`, opacity 0.55 → 1 on hover | hidden (drawer takes over) | hidden |
| `.hdr-nav-a.is-current` | opacity 1 + sage underline | — | — |
| `.trail-parent` (in `.page-trail`) | `--fs-eyebrow`, uppercase, 0.14em | — | — |
| `.trail-current` | `--fs-secondary`, opacity 0.55 | — | `--fw-display` |
```

Then in the "Section Titles" table, change the `.section-title h2` desktop value
from **4 rem** to `--fs-h1` (3 rem; 3.25 rem at the ≥90rem tier), matching
finding S-4 and the current token.

- [ ] **Step 4: Drop the deprecated-alias table from `typography.md`**

Remove any table or paragraph describing the deprecated `--fs-*` aliases, and add
one line under the type-scale table:

```markdown
> The pre-v3 alias names (Display-XL … Caption-S) were fully retired on
> 2026-07-24. There is exactly one ladder; `validate_design_tokens.py` fails if
> an alias reappears.
```

- [ ] **Step 5: Log the findings in `README.md`**

Add to the findings section, immediately before `### House-keeping`:

```markdown
### 2026-07 Brand Refinement

- **[B-1] [H] ✅** Three of five `--cat-*-text` tokens failed WCAG AA against their own badge tint (faculty 3.48:1, student 3.96:1, events 3.82:1). Hue proportions retuned until each clears 4.5:1; percentages are now contrast-derived and guarded by `validate_design_tokens.py`.
- **[B-2] [H] ✅** `--main-color-2` (2.38:1) was used for text on 12 rules and for focus rings on several more. Text moved to the new `--accent-ink` (4.93:1); focus rings moved to `--main-color` (7.66:1), which also removes an inconsistency with the rest of the site.
- **[B-3] [M] ✅** Colour documented as three layers (primitive / semantic UI / illustration). The apparent "sprawl" of 124 root tokens was three systems read as one; no token was deleted, and the primitives are load-bearing `sprite.svg` artwork.
- **[B-4] [M] ✅** The v3 type migration finished: seven deprecated `--fs-*` aliases and their 22 call sites retired, leaving one ladder.
- **[B-5] [L] ✅** `components.md` resynced — the subpage-header table described `.breadcrumb-*` classes that had been renamed and then moved out of the header entirely; `.section-title h2` said 4 rem against a 3 rem token.
```

- [ ] **Step 6: Commit**

```bash
git add DESIGN_RULES/
git commit -m "docs(design): document the three colour layers and resync stale rules"
```

---

## Phase 1 checkpoint

Before starting Phase 2, confirm with the user on `localhost:8001`:

```bash
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep "SEO check"
```

Expected: `Design token check: 0 failures.` and `SEO check: 0 warnings (0 errors).`

The only visible difference across the whole site should be that three category
label colours are slightly deeper, and blue text/focus rings are deeper. Ask the
user to confirm before Phase 2, since Phase 2 is the visible one.

---

# Phase 2 — the visible change (§2)

### Task 6: Narrow the motif and lighten the block geometry

**Files:**
- Modify: `static/css/general.css` (the `--block-*` geometry tokens and the `b-role="block"` rule)
- Modify: `DESIGN_RULES/layout.md`
- Modify: `DESIGN_RULES/README.md`
- Modify: the five templates (cache-bust)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: revised `--block-shadow-shift`, `--block-hover-shadow-shift`, and block border width, consumed by every `.skewed-block[b-role="block"]`.

- [ ] **Step 1: Record the current values**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
grep -nE "block-shadow-shift|block-hover-shadow-shift|_adjusted-border-width|_adjusted-border-radius" static/css/general.css | head
```
Expected: `--block-shadow-shift: 0.3125rem;` and
`--block-hover-shadow-shift: 0.4375rem;`, plus the `b-role="block"` rule that
raises border width to `0.1875rem`.

- [ ] **Step 2: Lighten the geometry**

In `static/css/general.css`, change:

```css
    --block-shadow-shift: 0.3125rem;
    --block-hover-shadow-shift: 0.4375rem;
```

to:

```css
    /* Block tier lightened 2026-07-24: the 5px/7px pair read chunky at the
       sizes blocks are actually used (hero images, portraits, the drawer).
       Buttons were already at the lighter 3px/4px and are unchanged. */
    --block-shadow-shift: 0.25rem;
    --block-hover-shadow-shift: 0.375rem;
```

Then in the `.skewed-block[b-role="block"]` rule, change the border width
override from `0.1875rem` to `0.125rem`.

- [ ] **Step 3: Rebuild and compare at three widths**

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python - general.css <<'EOF'
import re, sys
asset = sys.argv[1]
for f in ["templates/base.html", "templates/pages/news/news-item.html",
          "templates/pages/member/member.html",
          "templates/pages/publications/publication-item.html",
          "templates/pages/projects/project-item.html"]:
    text = open(f, encoding='utf-8').read()
    bumped = re.sub(rf"({re.escape(asset)}\?v=)(\d+)",
                    lambda m: m.group(1) + str(int(m.group(2)) + 1), text)
    if bumped != text:
        open(f, 'w', encoding='utf-8').write(bumped)
EOF
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep -E "SEO check|error"
```

Then check at **1440 / 900 / 375 px** on `http://localhost:8001/`,
`…/members/`, and one news detail page with a hero image. Member portraits, the
hero image frame and the news date badge should read lighter but still clearly
skewed and shadowed. The hover nudge, radius-doubling, and −3° skew are unchanged.

- [ ] **Step 4: Invert the motif rule in `layout.md`**

Replace the rule paragraph under "The Skewed-Block Motif" that begins
`> **Rule:** Any new surface — card, button, image, chip, input — is a
.skewed-block.` with:

```markdown
> **Rule:** the skew is a gesture, and a gesture repeated twenty times in a list
> stops being one. So it is scoped by what a surface *is*, not by whether it is a
> surface:
>
> - **Skewed** — interactive and photographic surfaces: buttons and CTAs
>   (`b-role="btn"`), images, member portraits, the hero image frame, the news
>   date badge, the menu drawer.
> - **Flat** — dense repeating chrome: filter pills, show-more pills, listing
>   thumbnails, inline article images, keyword chips, status and category badges.
>
> Flat surfaces still take no blurred shadow — the hard-offset-only rule is
> absolute. Children of a skewed block always counter-skew (`+3deg`), and hover
> always does three things at once: nudge up-left, grow the shadow, double the
> radius.
```

Then update the geometry table in the same file: `--block-shadow-shift` 5px → **4px**,
`--block-hover-shadow-shift` 7px → **6px**, and the block border row 3px → **2px**.

- [ ] **Step 5: Log the finding**

Add to `DESIGN_RULES/README.md` under the `### 2026-07 Brand Refinement` heading
created in Task 5:

```markdown
- **[B-6] [M] ✅** The motif rule claimed every card, button, image, chip and input is a skewed block, while five component types were already flat and being logged as exceptions. Rule inverted to scope by surface kind (interactive/photographic = skewed, dense repeating chrome = flat). Block geometry lightened: border 3px → 2px, shadow 5px → 4px, hover shadow 7px → 6px.
```

- [ ] **Step 6: Commit**

```bash
git add static/css/general.css DESIGN_RULES/layout.md DESIGN_RULES/README.md templates/base.html templates/pages/news/news-item.html templates/pages/member/member.html templates/pages/publications/publication-item.html templates/pages/projects/project-item.html
git commit -m "style(motif): scope the skew to interactive surfaces, lighten block geometry"
```

---

## Final verification

```bash
cd /home/jianhern/NTU-E3-Center.github.io
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | grep "SEO check"
git log --oneline source..brand-refinement
```

Expected: 0 token failures, 0 SEO warnings, and seven commits on the branch.

Confirm on `localhost:8001` at 1440 / 900 / 375 px that the background tiles and
sprite artwork are untouched, then ask the user before merging to `source`.
