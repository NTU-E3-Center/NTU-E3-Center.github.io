# `contents/` folder restructure — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize `contents/` so it contains only hand-edited source, grouped one subpage per folder. Eliminate every gitignored build artifact under `contents/`.

**Architecture:** Convert `excel_to_content.py` from a side-effecting script into a function (`build_member_data()`) returning a Python dict in memory. `build.py` consumes the dict directly and loads other subpage data from explicit per-subpage paths. No JSON or markdown is written to disk during the build except the final HTML in `docs/`.

**Tech Stack:** Python 3.x, Jinja2, openpyxl, markdown, Pillow. No new dependencies. No unit-test framework exists in this repo — verification is **byte-identical `docs/` output diff** before vs. after each task.

**Spec:** [`specs/2026-05-15-contents-restructure-design.md`](../specs/2026-05-15-contents-restructure-design.md)

---

## Verification harness (used by every task)

Each task uses the same verification ritual:

```bash
# One-time baseline (Pre-flight Task 0 below)
python build.py
cp -r docs /tmp/docs-baseline

# After every code task
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
# Expected: NO output (or only mtime-noise lines)
```

If `diff -r --brief` reports content differences, **stop** — that's a bug, not a refactor.

---

## Pre-flight

### Task 0: Capture the byte-diff baseline

**Files:** none

- [ ] **Step 1: Confirm you're on the right branch**

```bash
git status --short
git rev-parse --abbrev-ref HEAD
```

Expected branch: `feat/member-content-restructure`. Working tree should be clean (no uncommitted edits to `build.py`, `excel_to_content.py`, or templates). The `M SEO/recommendations/*` lines from the session start are fine; they don't affect the build.

- [ ] **Step 2: Build the baseline output**

```bash
conda activate E3website
python build.py
```

Expected: build succeeds, `docs/` contains the rendered site.

- [ ] **Step 3: Snapshot it**

```bash
rm -rf /tmp/docs-baseline
cp -r docs /tmp/docs-baseline
```

- [ ] **Step 4: Confirm the snapshot is intact**

```bash
ls /tmp/docs-baseline/index.html /tmp/docs-baseline/members/iyunlisahsieh/index.html
```

Both files must exist.

- [ ] **Step 5: Verify diff is clean**

```bash
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO output. This proves the harness works.

---

## Commit 1 — Eliminate intermediates

Goal: Remove all gitignored build artifacts from `contents/` by making `excel_to_content.py` return data in memory. **No file moves in this commit** — source files stay at their current paths.

### Task 1.1: Add `build_member_data()` function (backward-compatible)

Wrap the existing script body in a function. The function still writes the artifacts to disk for now — this is a pure refactor with no behavior change.

**Files:**
- Modify: `excel_to_content.py` (entire file)
- Modify: `build.py:14-17` (switch from importlib exec to a normal import + function call)

- [ ] **Step 1: Read the current file**

```bash
wc -l excel_to_content.py
```

Note the line count. The script's executable body starts after the helper definitions and runs to the end of the file (currently ~lines 240–466).

- [ ] **Step 2: Wrap the executable body in a function**

Move everything from `wb = openpyxl.load_workbook(...)` (currently around line 242) through the end of the file inside a new function:

```python
def build_member_data():
    """Read Excel + per-member folders, validate, write artifacts (for now),
    and return a dict that build.py can consume directly.

    Return shape:
      {
        'members_listing': [...],   # the section-grouped roster
        'members_by_id':   {webId: {...}, ...},
        'members_md':      {webId: {'about': html, 'position': html, 'interest': html}, ...},
      }
    """
    wb = openpyxl.load_workbook('contents/member-info.xlsx', data_only=True)
    # ... (the existing body)
    # At the end (after the existing summary prints), build and return the dict:
    members_by_id_inmem = {}
    members_md_inmem = {}
    # Re-derive these from what the script already computed (collect during the
    # existing loop instead of re-reading). The cleanest path: as you build each
    # member_json above, also stash it into members_by_id_inmem[web_id].
    # As you write each markdown file, also stash the rendered HTML into
    # members_md_inmem[web_id][kind].
    return {
        'members_listing': output,
        'members_by_id': members_by_id_inmem,
        'members_md': members_md_inmem,
    }
```

To minimize churn, do the dict-stashing in-place inside the existing for-loop. After the existing `with open(json_path, 'w', ...) as f: json.dump(member_json, f, ...)` line, add:

```python
members_by_id_inmem[web_id] = member_json
```

After each existing `write_text(p, about)` / `write_text(p, position)` / `write_text(p, ...)` call, add:

```python
members_md_inmem.setdefault(web_id, {})
members_md_inmem[web_id]['about']    = markdown.markdown(about, extensions=['md_in_html']) if about else ''
members_md_inmem[web_id]['position'] = markdown.markdown(position, extensions=['md_in_html']) if position else ''
members_md_inmem[web_id]['interest'] = markdown.markdown('\n\n'.join(f'/{topic}' for topic in interests), extensions=['md_in_html']) if interests else ''
```

(Add `import markdown` at the top of `excel_to_content.py` if not already present.)

- [ ] **Step 3: Add a guarded auto-run for backward compatibility**

At the bottom of the file (outside the function):

```python
if __name__ == "__main__":
    build_member_data()
```

This keeps the CLI usage (`python excel_to_content.py`) working.

- [ ] **Step 4: Build via the existing import path to confirm nothing broke**

`build.py` still uses `importlib.util.spec_from_file_location` to execute `excel_to_content` at import time. With the body moved into a function, that import will now run zero work (only function/helper definitions). The build will be missing the artifact files on a clean tree.

Therefore: **call the function from build.py for this step's verification.** Edit `build.py:14-17`:

```python
# OLD:
_spec = importlib.util.spec_from_file_location("excel_to_content", "excel_to_content.py")
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# NEW:
from excel_to_content import build_member_data
_member_data = build_member_data()   # still writes artifacts in this task; consumed in Task 1.2
```

- [ ] **Step 5: Run the build and verify byte-identical output**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences. Artifacts in `contents/structures/members/` and `contents/articles/members-*/` are regenerated identically.

- [ ] **Step 6: Stage but do not commit yet**

```bash
git add excel_to_content.py build.py
```

Commit happens at the end of Commit 1's task chain (Task 1.5).

---

### Task 1.2: Switch `build.py` to consume the in-memory dict (and stop reading regenerated files)

**Files:**
- Modify: `build.py:14-17` (import), `build.py:83-105` (structures load + members_by_id), `build.py:184-260` (render_member_pages), `build.py:255-263` (interest md lookup)
- Modify: `templates/pages/member/member.html:225-243` (about / interest section rendering)

- [ ] **Step 1: Update the structures glob to skip `members.json`**

`build.py:85` currently globs all `*.json` in `contents/structures/`. The regenerated `members.json` will still be there at this point (Task 1.1 hasn't removed writes yet). Override after the glob:

In `build.py` after the `for filename in os.listdir(structures_path):` loop (around line 92), add:

```python
# Use the in-memory members listing instead of the regenerated members.json
structures['members'] = _member_data['members_listing']
```

And replace the `members_by_id` block (lines 104–110):

```python
# OLD:
_members_detail_path = os.path.join(structures_path, 'members')
members_by_id = {}
if os.path.exists(_members_detail_path):
    for _fname in os.listdir(_members_detail_path):
        if _fname.endswith('.json'):
            _web_id = _fname[:-5]
            with open(os.path.join(_members_detail_path, _fname), 'r', encoding='utf-8') as _f:
                members_by_id[_web_id] = json.load(_f)
structures['members_by_id'] = members_by_id

# NEW:
members_by_id = _member_data['members_by_id']
structures['members_by_id'] = members_by_id
```

- [ ] **Step 2: Update `render_member_pages()` to use the in-memory dict**

Find the per-member loop (around `build.py:206-220`). The current code reads `member_base.get('pageStructure')` and json-loads it from disk. Replace with:

```python
# OLD:
page_structure_path = member_base.get('pageStructure')
if not page_structure_path:
    continue
if os.path.exists(page_structure_path):
    with open(page_structure_path, 'r', encoding='utf-8') as f:
        try:
            member_details = json.load(f)
        except json.JSONDecodeError:
            print(f"Error parsing JSON from {page_structure_path}")
            member_details = {}
else:
    print(f"Warning: pageStructure file not found: {page_structure_path}")
    member_details = {}

# NEW:
web_id = member_base.get('pageLink', '').rstrip('/').rsplit('/', 1)[-1]
if not web_id:
    continue
member_details = members_by_id.get(web_id)
if member_details is None:
    continue
```

- [ ] **Step 3: Replace the about/position markdown file reads with in-memory lookups**

Find the block around `build.py:230-250` that walks `pageContent['aboutSection']` and `pageContent['positionSection']` reading markdown from disk into `about_content[md_path]`. Replace with:

```python
# OLD: about_content = {}, then loops that read .md files keyed by md_path
# NEW:
about_content = {}
md_for_member = _member_data['members_md'].get(web_id, {})
# Make 'content' fields look themselves up in about_content for backward-compat
# with current template indexing. The artifact paths still exist as keys today;
# we keep them as the lookup key for this transitional task.
if page_content.get('aboutSection'):
    for section in page_content['aboutSection']:
        about_content[section['content']] = md_for_member.get('about', '')
if page_content.get('positionSection'):
    pos_path = page_content['positionSection']['content']
    about_content[pos_path] = md_for_member.get('position', '')
```

- [ ] **Step 4: Replace the interest .md read with in-memory lookup**

Find lines around `build.py:255-263` that read `contents/articles/members-interest/{member_id}.md`. Replace:

```python
# OLD: open(interest_path) / markdown.markdown(...)
# NEW:
interest_html = md_for_member.get('interest', '')
if interest_html:
    member['interest_content'] = interest_html
```

- [ ] **Step 5: Run the build and verify byte-identical output**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences. The artifact files are still being written by `excel_to_content.py` but `build.py` no longer reads them.

- [ ] **Step 6: Stage**

```bash
git add build.py
```

---

### Task 1.3: Stop writing artifacts from `excel_to_content.py`

**Files:**
- Modify: `excel_to_content.py` — remove every `os.makedirs`, `json.dump`-to-file, and `write_text` call inside `build_member_data()`

- [ ] **Step 1: Identify the write call sites**

Find and prepare to remove or comment out:

| Line area | Code to remove |
|---|---|
| ~`excel_to_content.py:354-357` | `os.makedirs(os.path.dirname(json_path), ...)` + `with open(json_path, 'w', ...) as f: json.dump(...)` |
| ~`excel_to_content.py:361-363` | `p = f'contents/articles/members-about/{web_id}.md'` + `write_text(p, about)` |
| ~`excel_to_content.py:365-367` | `p = f'.../members-position/{web_id}.md'` + `write_text(p, position)` |
| ~`excel_to_content.py:369-371` | `p = f'.../members-interest/{web_id}.md'` + `write_text(p, ...)` |
| ~`excel_to_content.py:454-456` | `members_json_path = '...'` + the final `json.dump(output, f, ...)` |
| Print lines | `print(f'Written: {members_json_path}')` and similar — turn into a single summary line |

- [ ] **Step 2: Make the deletions**

Delete the lines listed above. Keep the dict-stashing lines you added in Task 1.1 (those are the new contract). Keep the validation calls and the in-loop building of `member_json` / `entry`.

Also drop the now-unused helper `write_text(path, text)` and its callers if any — search:

```bash
grep -n "write_text\|json_written\|md_written" excel_to_content.py
```

Remove the helper definition + the tracking lists `json_written` / `md_written` if they exist.

Replace the summary print block (around `excel_to_content.py:458-465`) with:

```python
print(f'Member data: {sum(len(s["members"]) for s in output)} entries across {len(output)} sections')
```

- [ ] **Step 3: Delete the regenerated directories locally**

```bash
rm -rf contents/structures/members/ contents/structures/members.json
rm -rf contents/articles/members-about/ contents/articles/members-position/ contents/articles/members-interest/
```

- [ ] **Step 4: Run the build and verify byte-identical output**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences. No files are now written to `contents/structures/members/` or `contents/articles/members-*/`.

- [ ] **Step 5: Confirm no orphan artifacts exist**

```bash
ls contents/structures/members/ 2>/dev/null && echo "FAIL: still exists" || echo "OK: removed"
ls contents/articles/members-about/ 2>/dev/null && echo "FAIL: still exists" || echo "OK: removed"
```

Both lines must print `OK: removed`.

- [ ] **Step 6: Stage**

```bash
git add excel_to_content.py
```

---

### Task 1.4: Update `member.html` to use pre-rendered HTML directly (clean up the path-key indirection)

**Files:**
- Modify: `templates/pages/member/member.html` (the `about_content[X]` lookups)

- [ ] **Step 1: Replace `about_content[section['content']]` with the value itself**

In `member.html`, find:

```jinja
{{ about_content[section['content']] }}
```

(appears around line 230 inside the aboutSection for-loop, and around line 196 for `pos_path`).

Change them to:

```jinja
{{ section['content'] | safe }}
```

…**but** because Task 1.2 currently sets `section['content']` to be the *artifact path string* (and then keys `about_content` by it), this only works after we stop doing that indirection. So at the same time, in `build.py`'s `render_member_pages` (the block updated in Task 1.2 Step 3), change:

```python
# Task 1.2's transitional code:
about_content[section['content']] = md_for_member.get('about', '')

# Task 1.4 replacement:
section['content'] = md_for_member.get('about', '')
```

And the same for positionSection:

```python
page_content['positionSection']['content'] = md_for_member.get('position', '')
```

Now `section['content']` IS the HTML string. The `about_content` dict can be removed entirely (it's no longer used).

- [ ] **Step 2: Remove `about_content` from the template render call**

In `build.py:render_member_pages`, find the `template.render(...)` call (around line 295). Remove the `about_content=about_content` kwarg.

- [ ] **Step 3: Search for any other `about_content` references**

```bash
grep -rn "about_content" templates/ build.py
```

Every remaining usage must be either removed or updated. Expected: zero matches after edits.

- [ ] **Step 4: Run the build and verify byte-identical output**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences.

- [ ] **Step 5: Stage**

```bash
git add build.py templates/pages/member/member.html
```

---

### Task 1.5: Update `.gitignore` and commit

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Remove the 4 artifact lines**

Edit `.gitignore` and delete:

```
# Per-member build artifacts — regenerated every build by excel_to_content.py
# from contents/members/{webId}/ + the slim Excel. The SOURCE of member
# content is contents/members/{webId}/{member.json,about.md}; these dirs are
# transient intermediates that build.py consumes.
contents/structures/members/
contents/articles/members-about/
contents/articles/members-position/
contents/articles/members-interest/
```

Keep all other entries (`__pycache__/`, `docs/`, `.DS_Store`, etc.).

- [ ] **Step 2: Final verification**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences.

- [ ] **Step 3: Stage and commit Commit 1**

```bash
git add .gitignore
git status   # Inspect — should show modified excel_to_content.py, build.py, member.html, .gitignore
git commit -m "refactor: eliminate gitignored build artifacts under contents/

excel_to_content.py becomes a function build_member_data() that returns
member data in memory instead of writing JSON/MD intermediates to disk.
build.py consumes the returned dict directly. docs/ output is byte-
identical to before this commit."
```

---

## Commit 2 — Move source files to the new layout

Goal: Pure file moves + path-constant updates. Each task verifies `docs/` is still byte-identical. All changes staged across tasks land as one commit at the end.

### Task 2.1: Move `member-info.xlsx`, legacy, and `MEMBER_TEMPLATE/` into `contents/members/`

**Files:**
- Move: `contents/member-info.xlsx`, `contents/member-info.legacy.xlsx`, `contents/MEMBER_TEMPLATE/`
- Modify: `excel_to_content.py:242`, `build.py:447`

- [ ] **Step 1: Move via git mv**

```bash
git mv contents/member-info.xlsx        contents/members/member-info.xlsx
git mv contents/member-info.legacy.xlsx contents/members/member-info.legacy.xlsx
git mv contents/MEMBER_TEMPLATE         contents/members/MEMBER_TEMPLATE
```

- [ ] **Step 2: Update the Excel path in `excel_to_content.py`**

In `build_member_data()` (around the old line 242 inside the function):

```python
# OLD:
wb = openpyxl.load_workbook('contents/member-info.xlsx', data_only=True)
# NEW:
wb = openpyxl.load_workbook('contents/members/member-info.xlsx', data_only=True)
```

- [ ] **Step 3: Update the sitemap lastmod reference in `build.py:447`**

```python
# OLD:
lastmod=file_mtime("contents/member-info.xlsx")
# NEW:
lastmod=file_mtime("contents/members/member-info.xlsx")
```

- [ ] **Step 4: Build + verify**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO differences.

- [ ] **Step 5: Stage**

```bash
git add excel_to_content.py build.py
```

---

### Task 2.2: Move `pages.json` to `contents/pages.json`

**Files:**
- Move: `contents/structures/pages.json`
- Modify: `build.py:76`

- [ ] **Step 1: Move**

```bash
git mv contents/structures/pages.json contents/pages.json
```

- [ ] **Step 2: Update the load**

`build.py:76`:

```python
# OLD:
with open("contents/structures/pages.json", "r") as f:
# NEW:
with open("contents/pages.json", "r") as f:
```

- [ ] **Step 3: Confirm the structures glob no longer picks up pages.json**

`build.py:85` globs `contents/structures/*.json`. Now that `pages.json` is gone from there, the glob will not load it — which is what we want. (The dedicated `open()` at line 76 handles it.)

- [ ] **Step 4: Build + verify**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO differences.

- [ ] **Step 5: Stage**

```bash
git add build.py
```

---

### Task 2.3: Move per-subpage JSON files to per-subpage folders

**Files:**
- Move: each `contents/structures/*.json` into its subpage folder
- Modify: `build.py:83-92` — replace the glob with an explicit per-subpage load list

- [ ] **Step 1: Create destination folders**

```bash
mkdir -p contents/publications contents/research contents/group-life contents/about contents/contact contents/videos
# contents/news/ and contents/projects/ already exist
```

- [ ] **Step 2: Move each JSON file**

```bash
git mv contents/structures/publications.json contents/publications/publications.json
git mv contents/structures/news.json         contents/news/news.json
git mv contents/structures/research.json     contents/research/research.json
git mv contents/structures/group-life.json   contents/group-life/group-life.json
git mv contents/structures/about.json        contents/about/about.json
git mv contents/structures/contact.json      contents/contact/contact.json
git mv contents/structures/videos.json       contents/videos/videos.json
```

- [ ] **Step 3: Move the structures README (or delete)**

```bash
git rm contents/structures/README.md
```

(If you want to keep its content, copy any non-obsolete parts into `STRUCTURE.md` first.)

- [ ] **Step 4: Replace the glob in `build.py` with an explicit list**

`build.py:82-92` currently does:

```python
# Load JSON files from contents/structures
structures_path = 'contents/structures'
structures = {}
for filename in os.listdir(structures_path):
    if filename.endswith('.json'):
        file_path = os.path.join(structures_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        var_name = os.path.splitext(filename)[0]
        structures[var_name] = data
```

Replace the whole block with:

```python
# Load JSON for each subpage from its dedicated folder. Each entry is
# (key_in_structures, path).
structures = {}
_SUBPAGE_JSON_SOURCES = [
    ('publications', 'contents/publications/publications.json'),
    ('news',         'contents/news/news.json'),
    ('research',     'contents/research/research.json'),
    ('group-life',   'contents/group-life/group-life.json'),
    ('about',        'contents/about/about.json'),
    ('contact',      'contents/contact/contact.json'),
    ('videos',       'contents/videos/videos.json'),
]
for _key, _path in _SUBPAGE_JSON_SOURCES:
    with open(_path, 'r', encoding='utf-8') as _f:
        structures[_key] = json.load(_f)
```

Note: `group-life` keeps the hyphenated key (that's what templates reference today via `structures['group-life']`). Verify with:

```bash
grep -rn "structures\['group-life'\]\|structures\.get('group-life')\|group-life" templates/ build.py
```

- [ ] **Step 5: Confirm the projects load is unaffected**

`build.py:95-100` loads `contents/projects/projects.json` separately. That's already correct — leave it as-is.

- [ ] **Step 6: Remove the now-empty `contents/structures/` directory**

```bash
rmdir contents/structures 2>/dev/null || ls contents/structures
```

If `rmdir` fails, list the remaining contents and remove them appropriately.

- [ ] **Step 7: Build + verify**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO differences.

- [ ] **Step 8: Stage**

```bash
git add build.py
```

(The git mv operations are already staged.)

---

### Task 2.4: Move `about.md` and `contact.md` and news article markdown

**Files:**
- Move: `contents/articles/about.md`, `contents/articles/contact.md`, `contents/articles/news/*.md`
- Modify: `build.py:132-145` (articles walker), `build.py:380` + `build.py:455` (news md path)

- [ ] **Step 1: Move the page-body markdown**

```bash
git mv contents/articles/about.md   contents/about/about.md
git mv contents/articles/contact.md contents/contact/contact.md
```

- [ ] **Step 2: Move news article markdown**

```bash
mkdir -p contents/news/articles
git mv contents/articles/news/*.md contents/news/articles/
rmdir contents/articles/news
```

- [ ] **Step 3: Replace the articles walk in `build.py` with explicit loads**

`build.py:132-145` currently walks `contents/articles/` recursively. Replace with explicit loads:

```python
# OLD entire block:
articles_path = 'contents/articles'
articles = {}
for root, dirs, files in os.walk(articles_path):
    ...

# NEW:
articles = {}
_PAGE_BODY_MD = [
    ('about',   'contents/about/about.md'),
    ('contact', 'contents/contact/contact.md'),
]
for _key, _md_path in _PAGE_BODY_MD:
    with open(_md_path, 'r', encoding='utf-8') as _f:
        _md = _f.read()
    articles[_key] = markdown.markdown(_md, extensions=['md_in_html'])
```

The news item markdown is read on-demand inside `render_news_item_pages` (it's not in `articles`).

- [ ] **Step 4: Update the news md path in `build.py`**

Find lines `build.py:380` and `build.py:455`:

```python
# OLD (both occurrences):
md_path = f"contents/articles/news/{slug}.md"
# NEW:
md_path = f"contents/news/articles/{slug}.md"
```

- [ ] **Step 5: Confirm `contents/articles/` is empty**

```bash
ls contents/articles/
```

Expected: nothing (or only `.DS_Store`, which can be deleted).

- [ ] **Step 6: Remove the empty folder**

```bash
rm -f contents/articles/.DS_Store
rmdir contents/articles
```

- [ ] **Step 7: Build + verify**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO differences.

- [ ] **Step 8: Stage**

```bash
git add build.py
```

---

### Task 2.5: Move images to their subpage folders, retire `contents/images/`

**Files:**
- Move: `contents/images/news/` → `contents/news/images/`, `contents/images/group-life/` → `contents/group-life/images/`, `contents/images/research/` → `contents/research/images/`
- Move: `contents/images/home.svg` → `templates/partials/home.svg`
- Modify: `build.py:350` (news image discovery), `build.py:587` + `compress_and_convert_images()` body
- Modify: `templates/home/home.html:23` (`{% include 'images/home.svg' %}`)
- Modify: `build.py:21` (Jinja2 loader — remove `'contents'`)

- [ ] **Step 1: Move news images**

```bash
mkdir -p contents/news/images
git mv contents/images/news/* contents/news/images/
rmdir contents/images/news
```

- [ ] **Step 2: Move group-life images**

```bash
mkdir -p contents/group-life/images
git mv contents/images/group-life/* contents/group-life/images/
rmdir contents/images/group-life
```

- [ ] **Step 3: Move research images (if any exist)**

```bash
if [ -d contents/images/research ] && [ -n "$(ls -A contents/images/research 2>/dev/null)" ]; then
  mkdir -p contents/research/images
  git mv contents/images/research/* contents/research/images/
  rmdir contents/images/research
elif [ -d contents/images/research ]; then
  rmdir contents/images/research
fi
```

- [ ] **Step 4: Move `home.svg` to `templates/partials/`**

```bash
git mv contents/images/home.svg templates/partials/home.svg
```

- [ ] **Step 5: Remove the now-empty `contents/images/`**

```bash
rm -f contents/images/.DS_Store
rmdir contents/images
```

- [ ] **Step 6: Update `templates/home/home.html:23`**

```jinja
{# OLD: #}
{% include 'images/home.svg' %}
{# NEW: #}
{% include 'partials/home.svg' %}
```

- [ ] **Step 7: Remove `'contents'` from the Jinja2 loader in `build.py:21`**

```python
# OLD:
env = Environment(loader=FileSystemLoader(['templates', 'contents']),
# NEW:
env = Environment(loader=FileSystemLoader(['templates']),
```

- [ ] **Step 8: Update news image discovery in `build.py:350`**

Find the discovery block (around line 350 in `render_news_item_pages`):

```python
# OLD:
news_images_dir = f"contents/images/news/{slug}"
# NEW:
news_images_dir = f"contents/news/images/{slug}"
```

(Exact variable name may differ — search for `contents/images/news` to locate.)

- [ ] **Step 9: Update `images_path` and the image-processor source paths**

`build.py:587`:

```python
# OLD:
images_path = 'contents/images'
# NEW: removed entirely — the function now takes per-subpage source roots directly.
```

Search for every `os.path.join(images_path, ...)` and `contents/images/` reference inside `compress_and_convert_images()`. Replace with the new per-subpage roots:

| Old (under `contents/images/`) | New |
|---|---|
| `contents/images/news/` | `contents/news/images/` |
| `contents/images/group-life/` | `contents/group-life/images/` |
| `contents/images/research/` | `contents/research/images/` |

The output paths inside `docs/assets/...` stay unchanged — that's part of what byte-diff verifies.

- [ ] **Step 10: Build + verify**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO differences.

If any image regenerates with a different byte content (rare but possible if Pillow output isn't deterministic), spot-check a few WebP files visually before accepting the diff. The image bytes should be reproducible from the same source.

- [ ] **Step 11: Stage**

```bash
git add build.py templates/home/home.html
```

(All git mv operations are already staged.)

---

### Task 2.6: Update `validate_member.py` docstring path

**Files:**
- Modify: `validate_member.py:3`, `validate_member.py:204`

- [ ] **Step 1: Update the docstring**

`validate_member.py:3`:

```python
# OLD:
Used by excel_to_content.py to verify contents/members/{webId}/ folders
```

That line is actually still correct — `contents/members/{webId}/` did not change. Verify by reading the file:

```bash
grep -n "contents/" validate_member.py
```

Expected outputs:

```
3:Used by excel_to_content.py to verify contents/members/{webId}/ folders
204:        python validate_member.py iyunlisahsieh contents/members/iyunlisahsieh
```

Both are correct under the new layout. **No changes needed in this file.**

- [ ] **Step 2: Sanity check**

```bash
python validate_member.py iyunlisahsieh
```

Expected: `✓ contents/members/iyunlisahsieh: no issues` (or warnings only).

---

### Task 2.7: Final verification and commit Commit 2

- [ ] **Step 1: Final byte-diff**

```bash
rm -rf docs && python build.py
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences.

- [ ] **Step 2: Manual smoke test**

```bash
cd docs && python -m http.server 8000 &
sleep 1
# Then open each in a browser or use curl:
for url in / /members/ /members/iyunlisahsieh/ /publications/ /projects/ /news/ /about/ /contact/; do
  curl -s -o /dev/null -w "%{http_code} ${url}\n" http://localhost:8000${url}index.html
done
# Stop the server:
kill %1
cd ..
```

Expected: every line `200 /...`.

- [ ] **Step 3: Inspect `contents/` shape**

```bash
ls -1 contents/
```

Expected output (order may vary):

```
about
contact
group-life
members
news
pages.json
projects
publications
research
videos
```

No `structures/`, no `articles/`, no `images/`, no top-level Excel files.

- [ ] **Step 4: Commit Commit 2**

```bash
git status   # Inspect staged files
git commit -m "refactor: regroup contents/ by subpage

Each subpage's source (JSON + markdown + images) now lives in its own
folder under contents/. The member-info Excel + MEMBER_TEMPLATE move
into contents/members/. The contents/structures/ and contents/articles/
folders are removed. home.svg moves into templates/partials/ since it's
a Jinja2 template fragment, not data.

docs/ output is byte-identical."
```

---

## Commit 3 — Documentation pass

Goal: Update every doc that describes paths in the old layout. No code changes.

### Task 3.1: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the architecture diagram**

Replace the diagram in the "## Architecture" section to reflect the new flow (no intermediate artifacts, per-subpage folders). Use this:

```
contents/members/member-info.xlsx          ← admin roster (11 cols)
contents/members/{webId}/                  ← per-member content (member.json, about.md, photo.{ext})
        ↓
excel_to_content.build_member_data()       ← merges admin + content, validates, returns Python dict
        ↓                                    (NO intermediate files written)
contents/{publications,projects,news,research,group-life,about,contact,videos}/
                                           ← per-subpage source (JSON + Markdown + images)
contents/pages.json                        ← site-level nav config
templates/*.html                           ← Jinja2 templates (home.svg is here too)
static/                                    ← CSS, JS, fonts, sprites (copied as-is)
        ↓
    build.py
        ↓
    docs/                                  ← generated static site (GitHub Pages)
```

- [ ] **Step 2: Update the "build.py performs these steps" list**

Replace step 1's wording: `excel_to_content.build_member_data()` returns an in-memory dict; no longer "regenerates `members.json` + per-member JSON + member Markdown as gitignored build artifacts".

Update step 2 to reference per-subpage JSON paths instead of `contents/structures/`. Update step 4 to note members are looked up from the in-memory `members_by_id` dict.

- [ ] **Step 3: Update the "Content Structure" table**

Replace the path column for each row:

| What to change | Where |
|---|---|
| Member admin fields | `contents/members/member-info.xlsx` |
| Member content | `contents/members/{webId}/` — `member.json` + `about.md` + `photo.{ext}` |
| Publications | `contents/publications/publications.json` |
| News items | `contents/news/news.json` |
| News item article body | `contents/news/articles/{slug}.md` |
| News item images | `contents/news/images/{slug}/` |
| Research topics | `contents/research/research.json` |
| Group photos data | `contents/group-life/group-life.json` |
| Group photos images | `contents/group-life/images/` |
| Videos | `contents/videos/videos.json` (files in same folder) |
| Page navigation | `contents/pages.json` |
| About / Contact text | `contents/about/about.md`, `contents/contact/contact.md` |

- [ ] **Step 4: Update "Adding a new member" / "Updating a member" / "Adding a news item" sections**

Replace `cp -r contents/MEMBER_TEMPLATE contents/members/{webId}` with `cp -r contents/members/MEMBER_TEMPLATE contents/members/{webId}`. Replace `contents/articles/news/{slug}.md` with `contents/news/articles/{slug}.md`. Replace `contents/images/news/{slug}/` with `contents/news/images/{slug}/`.

- [ ] **Step 5: Remove the warning paragraph about intermediate artifacts**

The paragraph beginning "Do not manually edit `members.json`, `contents/structures/members/`, or `contents/articles/members-*/`..." can be deleted entirely — those paths no longer exist. Replace with a one-liner:

> `contents/members/member-info.legacy.xlsx` is a read-only archive of the original spreadsheet.

- [ ] **Step 6: Verify CLAUDE.md reads consistently**

```bash
grep -n "contents/structures\|contents/articles\|contents/images/" CLAUDE.md
```

Expected: NO matches.

- [ ] **Step 7: Stage**

```bash
git add CLAUDE.md
```

---

### Task 3.2: Update `STRUCTURE.md`, `CONTRIBUTING.md`, `SEO-RUNBOOK.md`

**Files:**
- Modify: `STRUCTURE.md`
- Modify: `CONTRIBUTING.md`
- Modify: `SEO-RUNBOOK.md`

- [ ] **Step 1: Audit each file**

```bash
grep -n "contents/structures\|contents/articles\|contents/images\|contents/MEMBER_TEMPLATE\|contents/member-info" STRUCTURE.md CONTRIBUTING.md SEO-RUNBOOK.md
```

Every match needs updating to its new path.

- [ ] **Step 2: Apply the same path substitutions used in CLAUDE.md**

The exact rewrite mapping:

| Old | New |
|---|---|
| `contents/member-info.xlsx` | `contents/members/member-info.xlsx` |
| `contents/MEMBER_TEMPLATE/` | `contents/members/MEMBER_TEMPLATE/` |
| `contents/structures/pages.json` | `contents/pages.json` |
| `contents/structures/news.json` | `contents/news/news.json` |
| `contents/structures/publications.json` | `contents/publications/publications.json` |
| `contents/structures/research.json` | `contents/research/research.json` |
| `contents/structures/group-life.json` | `contents/group-life/group-life.json` |
| `contents/structures/about.json` | `contents/about/about.json` |
| `contents/structures/contact.json` | `contents/contact/contact.json` |
| `contents/structures/videos.json` | `contents/videos/videos.json` |
| `contents/articles/about.md` | `contents/about/about.md` |
| `contents/articles/contact.md` | `contents/contact/contact.md` |
| `contents/articles/news/{slug}.md` | `contents/news/articles/{slug}.md` |
| `contents/images/news/{slug}/` | `contents/news/images/{slug}/` |
| `contents/images/group-life/` | `contents/group-life/images/` |
| `contents/images/research/` | `contents/research/images/` |
| Any reference to `contents/structures/members/` or `contents/articles/members-*/` as build artifacts | Delete or rephrase — those paths no longer exist |

- [ ] **Step 3: Update `contents/members/MEMBER_TEMPLATE/README.md` if it has paths**

```bash
grep -n "contents/" contents/members/MEMBER_TEMPLATE/README.md
```

Update any matches per the table above.

- [ ] **Step 4: Final audit**

```bash
grep -rn "contents/structures\|contents/articles\|contents/images" *.md contents/members/MEMBER_TEMPLATE/README.md 2>/dev/null
```

Expected: NO matches across docs.

- [ ] **Step 5: Stage and commit Commit 3**

```bash
git add STRUCTURE.md CONTRIBUTING.md SEO-RUNBOOK.md contents/members/MEMBER_TEMPLATE/README.md
git commit -m "docs: update path references to new contents/ layout

CLAUDE.md, STRUCTURE.md, CONTRIBUTING.md, SEO-RUNBOOK.md, and the
member template README all reflect the post-restructure paths.
No code changes."
```

---

## Post-flight

### Task 4: Final smoke test on the whole restructured tree

- [ ] **Step 1: Clean build**

```bash
rm -rf docs
python build.py
```

Expected: build succeeds, prints the usual member-count summary, exits 0.

- [ ] **Step 2: Final byte-diff against baseline**

```bash
diff -r --brief docs /tmp/docs-baseline
```

Expected: NO content differences.

- [ ] **Step 3: Confirm git tree is clean**

```bash
git status
git log --oneline -5
```

Expected: 3 new commits ahead of the pre-task HEAD; working tree clean.

- [ ] **Step 4: (Optional) Tear down baseline snapshot**

```bash
rm -rf /tmp/docs-baseline
```

---

## What this plan deliberately does not do

The SEO sweep (meta-tag refinement, name-variant generator in `seo_helpers.py`, per-subpage `keywords` plumbing, `news.topics` population, `about.md` research-area headings) is a separate effort with its own spec to be written after this plan ships. See the deferred tasks #3 and #4 in the project task list.

Stronger member-input validation (placeholder-prose detection, `metaDescription` length checks, required-field rules for members with a page) is also a separate effort, deferred per the spec's §8.
