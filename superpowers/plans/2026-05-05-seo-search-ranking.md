# SEO Search Ranking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make member, news, and publications subpages outrank the homepage on Google for entity-specific queries (e.g., "I-Yun Lisa Hsieh" → `/members/iyunlisahsieh/`).

**Architecture:** A shared Python helper (`seo_helpers.py`) auto-generates per-page meta descriptions from existing source data, with optional manual overrides via new fields in `member-info.xlsx` / `news.json` / `pages.json` / `publications.json`. Templates emit richer JSON-LD using stable `@id` URIs that link homepage `Organization` ↔ subpage `Person`/`NewsArticle` graphs. A `validate_seo()` function runs at the end of `build.py` to surface quality regressions as warnings.

**Tech Stack:** Python 3.x, Jinja2, markdown library, openpyxl (existing) + beautifulsoup4 (added in Phase 6). No new test framework — stdlib `unittest` for the helper.

**Spec:** `superpowers/specs/2026-05-04-seo-search-ranking-design.md`

---

## File Structure

**Create:**
- `seo_helpers.py` — pure functions: `generate_meta_description`, `strip_markdown`, `detect_language`. Importable from `build.py` and templates (registered as Jinja globals).
- `tests/test_seo_helpers.py` — stdlib unittest tests for the three helpers.
- `static/robots.txt` — crawl directives + sitemap pointer.
- `SEO-RUNBOOK.md` — operator-facing post-publish workflow.
- `superpowers/plans/2026-05-05-seo-search-ranking.md` — this file.

**Modify:**
- `build.py` — wire helpers into Jinja env, improve `generate_sitemap()`, add `validate_seo()`.
- `excel_to_content.py` — propagate new optional `metaDescription` column to per-member JSON.
- `templates/base.html` — change defaults (Phase 5).
- `templates/pages/member/member.html` — description, keywords, JSON-LD strengthening, BreadcrumbList.
- `templates/pages/news/news-item.html` — same shape as member.
- `templates/pages/members.html` — listing description + CollectionPage JSON-LD + BreadcrumbList.
- `templates/pages/news.html` — same shape as members listing.
- `templates/pages/publications.html` — same + per-publication keyword chips.
- `templates/home/about.html` (or wherever Organization JSON-LD lives — confirmed in Task 4.5) — Organization upgrade with `founder`/`member` graph.
- `templates/home/about.html` — wrap "I-Yun Lisa Hsieh" mentions with `<a href="/members/iyunlisahsieh/">`.
- `contents/structures/pages.json` — add `description` to `members-page`, `news`, `publications-page` entries.
- `contents/structures/news.json` — add optional `excerpt` field convention (no schema, just allowed).
- `contents/structures/publications.json` — add optional `keywords` arrays per item.
- `contents/member-info.xlsx` — add optional `metaDescription` column.
- `static/editor/index.html` — add `<meta name="robots" content="noindex, nofollow">`.
- `.github/workflows/deploy.yml` — add `beautifulsoup4` to pip install line (Phase 6).

---

## Phase 1 — Foundation

Goal: ship low-risk, high-value crawl/discovery improvements before touching templates.

### Task 1.1: Create `static/robots.txt`

**Files:**
- Create: `static/robots.txt`

- [ ] **Step 1: Write the file**

```
User-agent: *
Allow: /
Disallow: /editor/

Sitemap: https://e3center.caece.net/sitemap.xml
```

- [ ] **Step 2: Build and verify the file lands in `docs/`**

Run: `conda activate E3website && python build.py`
Then: `cat docs/robots.txt`
Expected: identical contents to the file in `static/`. (The existing static-asset copy step in `build.py` handles this — no code change needed.)

- [ ] **Step 3: Commit**

```bash
git add static/robots.txt
git commit -m "seo: add robots.txt with sitemap pointer and /editor/ disallow"
```

### Task 1.2: Add `noindex` meta to internal editor page

**Files:**
- Modify: `static/editor/index.html` (add one `<meta>` tag inside `<head>`)

- [ ] **Step 1: Add the meta tag**

In `static/editor/index.html`, immediately after the `<meta name="viewport" ...>` line in `<head>`, add:

```html
<meta name="robots" content="noindex, nofollow">
```

- [ ] **Step 2: Build and verify**

Run: `python build.py`
Then: `grep "noindex, nofollow" docs/editor/index.html`
Expected: one matching line.

- [ ] **Step 3: Commit**

```bash
git add static/editor/index.html
git commit -m "seo: deindex internal editor dashboard via noindex meta"
```

### Task 1.3: Improve sitemap `lastmod` and `priority`

**Files:**
- Modify: `build.py` (the `generate_sitemap()` function near line 355)

- [ ] **Step 1: Add a per-file mtime helper at top of `generate_sitemap()`**

Replace the existing `today` line with:

```python
today = datetime.now().strftime("%Y-%m-%d")

def file_mtime(path):
    """Return ISO date of file's last modification, or today if file is missing."""
    try:
        return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
    except OSError:
        return today
```

- [ ] **Step 2: Use member-info.xlsx mtime for member entries**

Find the member loop (currently `for group in structures.get('members', []):`). Change the `add_url(...)` call from:

```python
add_url(f"{BASE}{link}/", changefreq="monthly", priority="0.6")
```

to:

```python
add_url(f"{BASE}{link}/", changefreq="monthly", priority="0.7",
        lastmod=file_mtime("contents/member-info.xlsx"))
```

(The single source-of-truth file mtime is the best per-member signal we have without per-row tracking.)

- [ ] **Step 3: Use per-news-item markdown mtime for news entries**

Find the news loop (currently `for section in structures.get('news', []):`). Replace the loop body with:

```python
for section in structures.get('news', []):
    for item in section.get('items', []):
        link = item.get('pageLink')
        if link:
            slug = link.rstrip('/').rsplit('/', 1)[-1]
            md_path = f"contents/articles/news/{slug}.md"
            add_url(f"{BASE}{link}", changefreq="yearly", priority="0.6",
                    lastmod=file_mtime(md_path))
```

- [ ] **Step 4: Build and inspect sitemap**

Run: `python build.py`
Then: `head -40 docs/sitemap.xml`
Expected: at least one `<lastmod>` value matches the file's actual mtime (older than today for unchanged content).

- [ ] **Step 5: Commit**

```bash
git add build.py
git commit -m "seo: per-file lastmod and bumped priority for member/news sitemap entries"
```

---

## Phase 2 — Helper + Member Subpages

### Task 2.1: Create `seo_helpers.py` with `generate_meta_description`

**Files:**
- Create: `seo_helpers.py`
- Create: `tests/test_seo_helpers.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_seo_helpers.py`:

```python
import unittest
from seo_helpers import generate_meta_description


class TestGenerateMetaDescription(unittest.TestCase):
    def test_returns_override_when_provided(self):
        result = generate_meta_description(
            "Director of E3 Center, working on hydrogen.",
            "fallback text",
        )
        self.assertEqual(result, "Director of E3 Center, working on hydrogen.")

    def test_uses_first_nonempty_fallback(self):
        result = generate_meta_description(None, "", "  ", "real fallback content here")
        self.assertEqual(result, "real fallback content here")

    def test_truncates_to_max_chars_at_word_boundary(self):
        long = " ".join(["word"] * 100)  # 499 chars
        result = generate_meta_description(None, long, max_chars=50)
        self.assertLessEqual(len(result), 50)
        self.assertFalse(result.endswith("wo"), "should not cut mid-word")

    def test_preserves_short_text_unchanged(self):
        result = generate_meta_description(None, "short text", max_chars=160)
        self.assertEqual(result, "short text")

    def test_returns_empty_string_when_all_sources_empty(self):
        self.assertEqual(generate_meta_description(None, "", None), "")

    def test_collapses_whitespace(self):
        result = generate_meta_description(None, "line1\n\n  line2  \tline3")
        self.assertEqual(result, "line1 line2 line3")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_seo_helpers -v`
Expected: `ModuleNotFoundError: No module named 'seo_helpers'` (or `tests`).

If `tests` module not found: create `tests/__init__.py` as an empty file.

- [ ] **Step 3: Write minimal implementation**

Create `seo_helpers.py`:

```python
"""SEO helper functions used by build.py and Jinja2 templates.

Pure functions — no I/O, no side effects. Safe to unit test in isolation.
"""
import re


def generate_meta_description(primary, *fallback_sources, max_chars=160, min_chars=70):
    """Return a description string ≤ max_chars, truncated at word boundary.

    `primary` (e.g. an author override) is used as-is when truthy after
    whitespace collapse. Otherwise, the first non-empty `fallback_sources`
    entry is used. All inputs are whitespace-collapsed.

    The min_chars argument is informational only — used by validate_seo()
    to flag too-short descriptions, not enforced here.
    """
    candidates = [primary, *fallback_sources]
    for raw in candidates:
        if not raw:
            continue
        cleaned = _collapse_whitespace(raw)
        if not cleaned:
            continue
        return _truncate_at_word_boundary(cleaned, max_chars)
    return ""


def _collapse_whitespace(s):
    return re.sub(r"\s+", " ", s).strip()


def _truncate_at_word_boundary(s, max_chars):
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars]
    # Walk back to last whitespace so we don't cut mid-word
    last_space = cut.rfind(" ")
    if last_space > 0:
        return cut[:last_space].rstrip(" ,;:.")
    return cut.rstrip(" ,;:.")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.test_seo_helpers -v`
Expected: 6 tests, all OK.

- [ ] **Step 5: Commit**

```bash
git add seo_helpers.py tests/test_seo_helpers.py tests/__init__.py
git commit -m "seo: add generate_meta_description helper with unit tests"
```

### Task 2.2: Add `strip_markdown` and `detect_language` helpers

**Files:**
- Modify: `seo_helpers.py`
- Modify: `tests/test_seo_helpers.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_seo_helpers.py`:

```python
from seo_helpers import strip_markdown, detect_language


class TestStripMarkdown(unittest.TestCase):
    def test_removes_headings(self):
        self.assertEqual(strip_markdown("# Title\n\nBody text."), "Title Body text.")

    def test_keeps_link_text_drops_url(self):
        self.assertEqual(
            strip_markdown("See [the docs](https://example.com) for details."),
            "See the docs for details.",
        )

    def test_drops_images_entirely(self):
        self.assertEqual(strip_markdown("Before ![alt](x.png) after"), "Before after")

    def test_strips_bold_italic_code(self):
        self.assertEqual(
            strip_markdown("This is **bold**, *italic*, and `code`."),
            "This is bold, italic, and code.",
        )

    def test_strips_html_tags(self):
        self.assertEqual(strip_markdown("<p>Hello <b>world</b></p>"), "Hello world")


class TestDetectLanguage(unittest.TestCase):
    def test_english_text_returns_en(self):
        self.assertEqual(detect_language("This is an English sentence."), "en")

    def test_chinese_text_returns_zh_tw(self):
        self.assertEqual(detect_language("這是一段中文。"), "zh-TW")

    def test_mixed_majority_chinese_returns_zh_tw(self):
        # >30% CJK chars trips zh-TW
        self.assertEqual(detect_language("Project 計畫名稱 中文佔多數"), "zh-TW")

    def test_empty_input_returns_default_en(self):
        self.assertEqual(detect_language(""), "en")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.test_seo_helpers -v`
Expected: `ImportError: cannot import name 'strip_markdown'`.

- [ ] **Step 3: Implement both helpers in `seo_helpers.py`**

Append to `seo_helpers.py`:

```python
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^\)]*\)")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^\)]*\)")
_MD_CODE_RE = re.compile(r"`([^`]+)`")
_MD_BOLD_ITALIC_RE = re.compile(r"(\*{1,3}|_{1,3})(.+?)\1")
_MD_HEADING_RE = re.compile(r"^#{1,6}\s+", flags=re.MULTILINE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CJK_RE = re.compile(r"[一-鿿㐀-䶿]")


def strip_markdown(text):
    """Remove markdown syntax for use in plain-text contexts (meta descriptions).

    Drops images entirely. Keeps link/bold/italic/code text, drops their syntax.
    Strips HTML tags. Collapses whitespace.
    """
    if not text:
        return ""
    text = _MD_IMAGE_RE.sub("", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _MD_CODE_RE.sub(r"\1", text)
    text = _MD_BOLD_ITALIC_RE.sub(r"\2", text)
    text = _MD_HEADING_RE.sub("", text)
    text = _HTML_TAG_RE.sub("", text)
    return _collapse_whitespace(text)


def detect_language(text, threshold=0.3):
    """Return 'zh-TW' if CJK character ratio ≥ threshold, else 'en'."""
    if not text:
        return "en"
    total = len(text)
    cjk = len(_CJK_RE.findall(text))
    return "zh-TW" if (cjk / total) >= threshold else "en"
```

- [ ] **Step 4: Run all tests**

Run: `python -m unittest tests.test_seo_helpers -v`
Expected: all tests pass (6 + 5 + 4 = 15 tests).

- [ ] **Step 5: Commit**

```bash
git add seo_helpers.py tests/test_seo_helpers.py
git commit -m "seo: add strip_markdown and detect_language helpers with tests"
```

### Task 2.3: Wire helpers into Jinja env in `build.py`

**Files:**
- Modify: `build.py` (after the `env = Environment(...)` line near line 18)

- [ ] **Step 1: Import and register helpers**

After the existing imports in `build.py`, add:

```python
import seo_helpers
```

After the `env = Environment(...)` block (just before `def get_pub_sort_key`), add:

```python
# Register SEO helpers as Jinja globals so all templates can call them
env.globals['seo_meta_description'] = seo_helpers.generate_meta_description
env.globals['seo_strip_markdown'] = seo_helpers.strip_markdown
env.globals['seo_detect_language'] = seo_helpers.detect_language
```

- [ ] **Step 2: Verify no regression**

Run: `python build.py`
Expected: existing build succeeds (no template errors). Helpers are now available in templates but not yet used.

- [ ] **Step 3: Commit**

```bash
git add build.py
git commit -m "seo: register helper functions as Jinja globals"
```

### Task 2.4: Add `metaDescription` column to `excel_to_content.py`

**Files:**
- Modify: `excel_to_content.py`
- Modify: `contents/member-info.xlsx` (add new column header — manual step)

- [ ] **Step 1: Add the column to `member-info.xlsx`**

Open `contents/member-info.xlsx` in Excel/Numbers. Add a new column header `metaDescription` (after the existing columns; exact position doesn't matter). Leave all rows blank for now — this is just registering the schema. Save the file.

- [ ] **Step 2: Find the column-read logic in `excel_to_content.py`**

Locate where the script iterates rows and builds the per-member dict (search for `webId` or `engName` to find it). The pattern likely uses `openpyxl` cell access or pandas DataFrame.

- [ ] **Step 3: Read the new column when present**

Wherever the per-member dict is built, add a line that reads the `metaDescription` cell (using the same pattern as adjacent columns) and stores it as `meta_description` in the dict — or `None`/`""` if blank. The value flows into the per-member JSON written to `contents/structures/members/{webId}.json`.

Example pattern (adapt to actual code style — use whatever helper the script already uses to read a cell by header):

```python
member_data['metaDescription'] = read_cell(row, 'metaDescription') or None
```

- [ ] **Step 4: Build and verify**

Run: `python build.py`
Then: `python -c "import json; d=json.load(open('contents/structures/members/iyunlisahsieh.json')); print('metaDescription' in d, repr(d.get('metaDescription')))"`
Expected: `True None` (key present, value None since column is empty).

- [ ] **Step 5: Commit**

```bash
git add excel_to_content.py contents/member-info.xlsx contents/structures/members/
git commit -m "seo: propagate optional metaDescription column from xlsx to member JSON"
```

### Task 2.5: Update member subpage template

**Files:**
- Modify: `templates/pages/member/member.html`

This is a large template change — broken into substeps for clarity, single commit.

- [ ] **Step 1: Replace the meta description line**

Find the existing line:

```html
<meta name="description" content="{{ member['chiNameEng'] }} — member of E3 Center, National Taiwan University. Research in sustainable energy transition.">
```

Replace with:

```html
{% set _interest = (member.get('interest_content') or '') | striptags %}
{% set _about_first = '' %}
{% if member.get('pageContent', {}).get('aboutSection') %}
  {% for _section in member['pageContent']['aboutSection'] %}
    {% if not _about_first %}
      {% set _about_first = (about_content[_section['content']] or '') | striptags %}
    {% endif %}
  {% endfor %}
{% endif %}
{% set _auto_desc_a = (member.get('position', '') ~ '. Research interests: ' ~ _interest) if _interest else '' %}
{% set _auto_desc_b = (member.get('position', '') ~ ' at E3 Center, NTU. ' ~ _about_first) if _about_first else '' %}
{% set _auto_desc_c = member['chiNameEng'] ~ ' — member of E3 Center, National Taiwan University.' %}
{% set _meta_desc = seo_meta_description(member.get('metaDescription'), _auto_desc_a, _auto_desc_b, _auto_desc_c) %}
<meta name="description" content="{{ _meta_desc }}">
```

- [ ] **Step 2: Replace the meta keywords line**

Find:

```html
<meta name="keywords" content="{{ member['engName'] }}, {{ member['chiName'] }}{% if member['chiNameEng'] %}, {{ member['chiNameEng'] }}{% endif %}, E3 Group, e3, NTU, 台大, 台灣大學">
```

Replace with:

```html
{% set _kw_parts = [member.get('engName'), member.get('chiName'), member.get('chiNameEng'), member.get('position')] %}
{% set _big_tags = [] %}
{% for _section in member.get('pageContent', {}).get('researchSection', []) %}
  {% for _tid in _section.get('topics', []) %}
    {% set _topic = research_by_id.get(_tid) %}
    {% if _topic %}
      {% for _tag in _topic.get('bigTags', [])[:1] %}
        {% if _tag not in _big_tags %}{{ _big_tags.append(_tag) or '' }}{% endif %}
      {% endfor %}
    {% endif %}
  {% endfor %}
{% endfor %}
{% set _all_kw = (_kw_parts + _big_tags[:3]) | select | list %}
<meta name="keywords" content="{{ _all_kw | join(', ') }}">
```

- [ ] **Step 3: Strengthen Person JSON-LD**

Find the existing `<script type="application/ld+json">` block (lines ~69-84). Replace its body with:

```jinja
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": "https://e3center.caece.net{{ member['pageLink'] }}/#person",
  "name": "{{ member['chiNameEng'] }}",
  "alternateName": "{{ member['chiName'] }}",
  "url": "https://e3center.caece.net{{ member['pageLink'] }}/",
  {% if member.get('position') %}"jobTitle": "{{ member['position'] }}",
  {% endif %}"affiliation": { "@id": "https://e3center.caece.net/#organization" }{% if member.get('pageContent', {}).get('links') %}{% set ns = namespace(has_link=false) %}{% for tag in member['pageContent']['links'] %}{% if tag.get('link') and not tag['link'].startswith('mailto:') and not 'maps' in tag['link'] %}{% set ns.has_link = true %}{% endif %}{% endfor %}{% if ns.has_link %},
  "sameAs": [{% set comma = joiner() %}{% for tag in member['pageContent']['links'] %}{% if tag.get('link') and not tag['link'].startswith('mailto:') and not 'maps' in tag['link'] %}{{ comma() }}"{{ tag['link'] }}"{% endif %}{% endfor %}]{% endif %}{% endif %}
}
</script>
```

- [ ] **Step 4: Add BreadcrumbList JSON-LD**

Immediately after the Person JSON-LD `</script>` tag, add:

```jinja
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://e3center.caece.net/" },
    { "@type": "ListItem", "position": 2, "name": "Members", "item": "https://e3center.caece.net/members/" },
    { "@type": "ListItem", "position": 3, "name": {{ member['chiNameEng'] | tojson }} }
  ]
}
</script>
```

- [ ] **Step 5: Build and verify a member page**

Run: `python build.py`
Then: `grep -A1 "name=\"description\"" docs/members/iyunlisahsieh/index.html | head -2`
Expected: a description containing her position and research interests, not the old generic boilerplate.

Then: `grep "BreadcrumbList" docs/members/iyunlisahsieh/index.html`
Expected: one match.

Then: `python -c "import json,re; html=open('docs/members/iyunlisahsieh/index.html').read(); blocks=re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S); [json.loads(b) for b in blocks]; print('OK', len(blocks), 'JSON-LD blocks')"`
Expected: `OK 2 JSON-LD blocks` (Person + BreadcrumbList both parse as valid JSON).

- [ ] **Step 6: Commit**

```bash
git add templates/pages/member/member.html
git commit -m "seo: enrich member subpage description, keywords, JSON-LD; add BreadcrumbList"
```

---

## Phase 3 — News Subpages

### Task 3.1: Update news-item template — meta description, keywords, NewsArticle JSON-LD, Breadcrumb

**Files:**
- Modify: `templates/pages/news/news-item.html`
- Modify: `build.py` (`render_news_pages` to compute `dateModified`)

- [ ] **Step 1: Compute `dateModified` for each news item in `build.py`**

In `build.py`, find `render_news_pages()` (near line 282). Inside the loop where each news item is rendered, just before `output = template.render(...)`, add:

```python
slug = page_link.rstrip('/').rsplit('/', 1)[-1]
md_path = f"contents/articles/news/{slug}.md"
try:
    date_modified = datetime.fromtimestamp(os.path.getmtime(md_path)).strftime("%Y-%m-%dT%H:%M:%S")
except OSError:
    date_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
```

Then pass `date_modified=date_modified` into the `template.render(...)` call.

- [ ] **Step 2: Replace meta description in `news-item.html`**

Find:

```html
<meta name="description" content="{{ news['title'][:155] }} — E3 Center, National Taiwan University.">
```

Replace with:

```jinja
{% set _body_text = seo_strip_markdown(news.get('content', '')) %}
{% set _auto_desc = _body_text if _body_text and 'to be updated' not in _body_text|lower else (news['title'] ~ ' — E3 Center news, ' ~ news['month'] ~ ' 20' ~ news['year'][1:] ~ '.') %}
{% set _meta_desc = seo_meta_description(news.get('excerpt'), _auto_desc) %}
<meta name="description" content="{{ _meta_desc }}">
```

- [ ] **Step 3: Replace meta keywords**

Find:

```html
<meta name="keywords" content="E3 Center, e3, NTU, News, {{ news['title'][:60] }}">
```

Replace with:

```jinja
<meta name="keywords" content="E3 Center, NTU news, {{ news.get('category', 'News') }}, 20{{ news['year'][1:] }}">
```

- [ ] **Step 4: Strengthen NewsArticle JSON-LD**

Find the existing `<script type="application/ld+json">` block. Replace with:

```jinja
{% set _lang = seo_detect_language(news.get('content', '')) %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "@id": "https://e3center.caece.net{{ news['pageLink'] }}#article",
  "headline": {{ news['title'] | tojson }},
  "description": {{ _meta_desc | tojson }},
  "url": "https://e3center.caece.net{{ news['pageLink'] }}",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://e3center.caece.net{{ news['pageLink'] }}" },
  "inLanguage": "{{ _lang }}",
  {% set month_map = {'Jan.': '01', 'Feb.': '02', 'Mar.': '03', 'Apr.': '04', 'May': '05', 'Jun.': '06', 'Jul.': '07', 'Aug.': '08', 'Sep.': '09', 'Oct.': '10', 'Nov.': '11', 'Dec.': '12'} %}"datePublished": "20{{ news['year'][1:] }}-{{ month_map.get(news['month'], '01') }}",
  "dateModified": "{{ date_modified }}",
  "author": {
    "@type": "Organization",
    "name": "E3 Center",
    "url": "https://e3center.caece.net"
  },
  "publisher": { "@id": "https://e3center.caece.net/#organization" }{% if news.get('imgPath') %},
  "image": "https://e3center.caece.net{{ news['imgPath'] }}"{% endif %}
}
</script>
```

- [ ] **Step 5: Add BreadcrumbList JSON-LD**

Immediately after the NewsArticle `</script>` tag:

```jinja
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://e3center.caece.net/" },
    { "@type": "ListItem", "position": 2, "name": "News", "item": "https://e3center.caece.net/news/" },
    { "@type": "ListItem", "position": 3, "name": {{ (news.get('shortTitle') or news['title']) | tojson }} }
  ]
}
</script>
```

- [ ] **Step 6: Build and verify**

Run: `python build.py`
Then: `ls docs/news/2026-ntu-ug-joint-seminar/index.html` (or any news item that exists)
Then: `grep -E 'description|inLanguage|dateModified|BreadcrumbList' docs/news/2026-ntu-ug-joint-seminar/index.html`
Expected: all four strings present.

Then validate JSON-LD:

```bash
python -c "import json,re; html=open('docs/news/2026-ntu-ug-joint-seminar/index.html').read(); blocks=re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S); [json.loads(b) for b in blocks]; print('OK', len(blocks), 'JSON-LD blocks')"
```

Expected: `OK 2 JSON-LD blocks`.

- [ ] **Step 7: Commit**

```bash
git add build.py templates/pages/news/news-item.html
git commit -m "seo: enrich news-item description, keywords, NewsArticle JSON-LD; add Breadcrumb"
```

---

## Phase 4 — Listing Pages + Homepage Organization JSON-LD

### Task 4.1: Add description fields to pages.json for listing pages

**Files:**
- Modify: `contents/structures/pages.json`

- [ ] **Step 1: Add `description` to all three listing entries**

Edit `pages.json`. To `news`, `members-page`, and `publications-page` entries, add a `description` field. After the change:

```json
"news": {
  "path": "news",
  "title": "News | E3 Center",
  "description": "E3 Center news, awards, seminars, and announcements from National Taiwan University.",
  "subpageTitle": "News",
  "template": "pages/news"
},
"members-page": {
  "path": "members",
  "title": "Members | E3 Center",
  "description": "Members of E3 Center, NTU — researchers, students, and alumni working on sustainable energy transition, transportation electrification, and climate policy.",
  "subpageTitle": "Members",
  "template": "pages/members"
},
"publications-page": {
  "path": "publications",
  "title": "Publications | E3 Center",
  "description": "Peer-reviewed publications from E3 Center, NTU, on sustainable energy transition, transportation electrification, and climate policy.",
  "subpageTitle": "Publications",
  "template": "pages/publications"
}
```

- [ ] **Step 2: Wire `description` into `render_templates()` and `base.html`**

In `build.py` `render_templates()`, change the `template.render(...)` call (around line 116) to also pass:

```python
description=page_data.get("description"),
```

Then verify `base.html` already uses the `description` variable (it does — line 11: `{{ description if description is defined else defaultDescription }}`). No template change needed.

- [ ] **Step 3: Build and verify**

Run: `python build.py`
Then: `grep "name=\"description\"" docs/news/index.html docs/members/index.html docs/publications/index.html`
Expected: each shows the new custom description, not the homepage default.

- [ ] **Step 4: Commit**

```bash
git add contents/structures/pages.json build.py
git commit -m "seo: add per-listing meta descriptions for /members /news /publications"
```

### Task 4.2: Add CollectionPage + BreadcrumbList JSON-LD to members listing

**Files:**
- Modify: `templates/pages/members.html`

- [ ] **Step 1: Find the right insertion point**

`templates/pages/members.html` likely extends base.html via `{% extends 'base.html' %}` and defines a `{% block jsonld %}` (which `base.html:80` includes). Confirm by running:

```bash
grep -n "block jsonld\|extends" templates/pages/members.html
```

If a `{% block jsonld %}` exists, add inside it. If not, add one.

- [ ] **Step 2: Add CollectionPage + BreadcrumbList JSON-LD**

Inside (or as) the `{% block jsonld %}` of `templates/pages/members.html`:

```jinja
{% block jsonld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Members | E3 Center",
  "url": "https://e3center.caece.net/members/",
  "isPartOf": { "@id": "https://e3center.caece.net/#organization" },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {% set _pos = namespace(n=0) %}
      {% set _seen = [] %}
      {% set _comma = joiner(",") %}
      {% for _group in structures.get('members', []) %}
        {% for _m in _group.get('members', []) %}
          {% if _m.get('pageLink') and _m['pageLink'] not in _seen %}
            {% if _seen.append(_m['pageLink']) %}{% endif %}
            {% set _pos.n = _pos.n + 1 %}
            {{ _comma() }}{
              "@type": "ListItem",
              "position": {{ _pos.n }},
              "item": {
                "@type": "Person",
                "@id": "https://e3center.caece.net{{ _m['pageLink'] }}/#person",
                "name": {{ (_m.get('chiNameEng') or _m.get('engName')) | tojson }},
                "url": "https://e3center.caece.net{{ _m['pageLink'] }}/"
              }
            }
          {% endif %}
        {% endfor %}
      {% endfor %}
    ]
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://e3center.caece.net/" },
    { "@type": "ListItem", "position": 2, "name": "Members" }
  ]
}
</script>
{% endblock %}
```

- [ ] **Step 3: Build and verify**

Run: `python build.py`
Then: `grep -c "ListItem" docs/members/index.html`
Expected: at least N+2 (one ListItem per member + 2 breadcrumb items).

Validate JSON parsing:

```bash
python -c "import json,re; html=open('docs/members/index.html').read(); blocks=re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S); [json.loads(b) for b in blocks]; print('OK', len(blocks), 'JSON-LD blocks')"
```

Expected: `OK 2 JSON-LD blocks`.

- [ ] **Step 4: Commit**

```bash
git add templates/pages/members.html
git commit -m "seo: add CollectionPage + BreadcrumbList JSON-LD to members listing"
```

### Task 4.3: Add CollectionPage + BreadcrumbList JSON-LD to news listing

**Files:**
- Modify: `templates/pages/news.html`

- [ ] **Step 1: Add the JSON-LD block**

Same pattern as Task 4.2 — inside `{% block jsonld %}`:

```jinja
{% block jsonld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "News | E3 Center",
  "url": "https://e3center.caece.net/news/",
  "isPartOf": { "@id": "https://e3center.caece.net/#organization" },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {% set _pos = namespace(n=0) %}
      {% set _comma = joiner(",") %}
      {% set _month_map = {'Jan.': '01', 'Feb.': '02', 'Mar.': '03', 'Apr.': '04', 'May': '05', 'Jun.': '06', 'Jul.': '07', 'Aug.': '08', 'Sep.': '09', 'Oct.': '10', 'Nov.': '11', 'Dec.': '12'} %}
      {% for _section in structures.get('news', []) %}
        {% for _item in _section.get('items', []) %}
          {% if _item.get('pageLink') %}
            {% set _pos.n = _pos.n + 1 %}
            {{ _comma() }}{
              "@type": "ListItem",
              "position": {{ _pos.n }},
              "item": {
                "@type": "NewsArticle",
                "headline": {{ _item['title'] | tojson }},
                "datePublished": "20{{ _item['year'][1:] }}-{{ _month_map.get(_item['month'], '01') }}",
                "url": "https://e3center.caece.net{{ _item['pageLink'] }}"
              }
            }
          {% endif %}
        {% endfor %}
      {% endfor %}
    ]
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://e3center.caece.net/" },
    { "@type": "ListItem", "position": 2, "name": "News" }
  ]
}
</script>
{% endblock %}
```

- [ ] **Step 2: Build and verify**

Run: `python build.py`
Then validate as in Task 4.2:

```bash
python -c "import json,re; html=open('docs/news/index.html').read(); blocks=re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S); [json.loads(b) for b in blocks]; print('OK', len(blocks), 'JSON-LD blocks')"
```

Expected: `OK 2 JSON-LD blocks`.

- [ ] **Step 3: Commit**

```bash
git add templates/pages/news.html
git commit -m "seo: add CollectionPage + BreadcrumbList JSON-LD to news listing"
```

### Task 4.4: Add per-publication keywords + visible chips + CollectionPage JSON-LD

**Files:**
- Modify: `contents/structures/publications.json`
- Modify: `templates/pages/publications.html`
- Modify: `templates/pages/member/member.html` (mirror chips on member pub list)

- [ ] **Step 1: Add `keywords` arrays to recent publications**

Edit `contents/structures/publications.json`. For each item with `"E3": true && "status": "published"` from the last 3 years, add a `"keywords": [...]` array. Example:

```json
{
  "citationId": "...",
  "title": "...",
  "E3": true,
  "status": "published",
  "year": "'24",
  "keywords": ["hydrogen", "life cycle assessment", "transportation"]
}
```

Older entries can be left without the field. Pull keyword strings from the article's first-page metadata.

- [ ] **Step 2: Render visible keyword chips in publications listing**

In `templates/pages/publications.html`, find where each publication is rendered. Inside the per-publication block (typically after the journal/volume line), add:

```jinja
{% if item.get('keywords') %}
<div class="pub-keywords">
  {% for _kw in item['keywords'] %}
  <span class="pub-keyword-chip">{{ _kw }}</span>
  {% endfor %}
</div>
{% endif %}
```

Add minimal CSS in `static/css/style.css` (or wherever publication styles live):

```css
.pub-keywords { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.5rem; }
.pub-keyword-chip { font-size: 0.75rem; padding: 0.125rem 0.5rem; background: rgba(10, 85, 126, 0.08); border-radius: 999px; color: #0a557e; }
```

- [ ] **Step 3: Add CollectionPage + ItemList JSON-LD to publications listing**

Inside (or as) `{% block jsonld %}` of `templates/pages/publications.html`:

```jinja
{% block jsonld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Publications | E3 Center",
  "url": "https://e3center.caece.net/publications/",
  "isPartOf": { "@id": "https://e3center.caece.net/#organization" },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {% set _pos = namespace(n=0) %}
      {% set _comma = joiner(",") %}
      {% for _section in structures.get('publications', []) %}
        {% for _item in _section.get('items', []) %}
          {% if _item.get('E3') and _item.get('status', 'published') == 'published' %}
            {% set _pos.n = _pos.n + 1 %}
            {{ _comma() }}{
              "@type": "ListItem",
              "position": {{ _pos.n }},
              "item": {
                "@type": "ScholarlyArticle",
                "headline": {{ _item['title'] | tojson }},
                "datePublished": "20{{ _item['year'][1:] if _item['year'].startswith(\"'\") else _item['year'] }}",
                {% if _item.get('journal') %}"isPartOf": { "@type": "Periodical", "name": {{ _item['journal'] | tojson }} },
                {% endif %}{% if _item.get('link') %}"url": {{ _item['link'] | tojson }},
                {% endif %}{% if _item.get('keywords') %}"keywords": {{ _item['keywords'] | tojson }},
                {% endif %}"author": {{ _item.get('authors', '') | tojson }}
              }
            }
          {% endif %}
        {% endfor %}
      {% endfor %}
    ]
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://e3center.caece.net/" },
    { "@type": "ListItem", "position": 2, "name": "Publications" }
  ]
}
</script>
{% endblock %}
```

- [ ] **Step 4: Mirror chips on member pages**

In `templates/pages/member/member.html`, find the per-publication block (around line 220 or 250 — the `<div class="pub-block">` inside the loops). After `<div class="pub-subtitle">`, add:

```jinja
{% if pub.get('keywords') %}
<div class="pub-keywords">
  {% for _kw in pub['keywords'] %}
  <span class="pub-keyword-chip">{{ _kw }}</span>
  {% endfor %}
</div>
{% endif %}
```

Apply in both the manual and citation-based publication loops.

- [ ] **Step 5: Build and verify**

Run: `python build.py`
Then:

```bash
grep -c "pub-keyword-chip" docs/publications/index.html
```

Expected: ≥ 1 per publication that has keywords.

Validate JSON-LD:

```bash
python -c "import json,re; html=open('docs/publications/index.html').read(); blocks=re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S); [json.loads(b) for b in blocks]; print('OK', len(blocks), 'JSON-LD blocks')"
```

Expected: `OK 2 JSON-LD blocks`.

- [ ] **Step 6: Commit**

```bash
git add contents/structures/publications.json templates/pages/publications.html templates/pages/member/member.html static/css/style.css
git commit -m "seo: per-publication keywords with visible chips + CollectionPage JSON-LD"
```

### Task 4.5: Upgrade homepage Organization JSON-LD

**Files:**
- Modify: `templates/home/about.html` (or wherever Organization JSON-LD currently lives)

- [ ] **Step 1: Locate the existing Organization JSON-LD**

Run: `grep -rn "\"@type\": \"Organization\"\|\"@type\": \"ResearchOrganization\"" templates/ static/`
Expected: one match in `templates/home/about.html` or `templates/index.html`. Note the file and line.

- [ ] **Step 2: Replace the existing Organization block**

In the file from Step 1, replace the Organization JSON-LD with:

```jinja
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ResearchOrganization",
  "@id": "https://e3center.caece.net/#organization",
  "name": "E3 Center",
  "alternateName": "Energy, Environment, Engineering Center",
  "url": "https://e3center.caece.net/",
  "logo": "https://e3center.caece.net/assets/images/og-image-1200x630.png",
  "founder": {
    "@type": "Person",
    "@id": "https://e3center.caece.net/members/iyunlisahsieh/#person",
    "name": "I-Yun Lisa Hsieh",
    "url": "https://e3center.caece.net/members/iyunlisahsieh/"
  },
  "parentOrganization": {
    "@type": "CollegeOrUniversity",
    "name": "National Taiwan University",
    "url": "https://www.ntu.edu.tw"
  },
  "member": [
    {% set _seen = [] %}
    {% set _comma = joiner(",") %}
    {% for _group in structures.get('members', []) %}
      {% for _m in _group.get('members', []) %}
        {% if _m.get('pageLink') and _m['pageLink'] not in _seen %}
          {% if _seen.append(_m['pageLink']) %}{% endif %}
          {{ _comma() }}{
            "@type": "Person",
            "@id": "https://e3center.caece.net{{ _m['pageLink'] }}/#person",
            "name": {{ (_m.get('chiNameEng') or _m.get('engName')) | tojson }},
            "url": "https://e3center.caece.net{{ _m['pageLink'] }}/"
          }
        {% endif %}
      {% endfor %}
    {% endfor %}
  ]
}
</script>
```

- [ ] **Step 3: Build and verify**

Run: `python build.py`
Then:

```bash
python -c "import json,re; html=open('docs/index.html').read(); blocks=re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S); orgs=[json.loads(b) for b in blocks if 'Organization' in b]; assert orgs and orgs[0].get('founder',{}).get('url') == 'https://e3center.caece.net/members/iyunlisahsieh/', orgs; print('Organization JSON-LD OK, member count:', len(orgs[0].get('member', [])))"
```

Expected: `Organization JSON-LD OK, member count: N` (N matching the number of unique members).

- [ ] **Step 4: Commit**

```bash
git add templates/home/about.html  # or whichever file Step 1 found
git commit -m "seo: upgrade homepage Organization JSON-LD with founder + member graph"
```

---

## Phase 5 — Homepage Retitle

**Warning:** This phase has the highest risk of short-term ranking volatility on brand queries. Confirm Phases 1–4 are deployed and Google has had time to crawl them (check GSC) before starting Phase 5.

### Task 5.1: Update homepage `<title>` and `defaultKeywords`

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Update `defaultTitle`**

In `templates/base.html` line 1, change:

```jinja
{% set defaultTitle = 'E3 Center - Directed by I-Yun Lisa Hsieh' %}
```

to:

```jinja
{% set defaultTitle = 'E3 Center | National Taiwan University' %}
```

- [ ] **Step 2: Update `defaultKeywords`**

Line 4, change:

```jinja
{% set defaultKeywords = 'I-Yun Lisa Hsieh, 謝依芸, E3 Center, e3, NTU, 台大, 台灣大學' %}
```

to:

```jinja
{% set defaultKeywords = 'E3 Center, sustainable energy transition, NTU, 台灣大學, 台大, energy research, climate policy' %}
```

- [ ] **Step 3: Build and verify**

Run: `python build.py`
Then: `grep -E '<title>|name=\"keywords\"' docs/index.html`
Expected: title is "E3 Center | National Taiwan University"; keywords no longer mention the director's name.

- [ ] **Step 4: Commit**

```bash
git add templates/base.html
git commit -m "seo: retitle homepage to stop competing with director subpage on brand queries"
```

### Task 5.2: Wrap director name with internal links on homepage

**Files:**
- Modify: `templates/home/about.html` (and any other homepage section template that mentions her by name)

- [ ] **Step 1: Find every literal mention of her name on the homepage**

Run: `grep -rn "I-Yun Lisa Hsieh\|謝依芸" templates/home/ templates/index.html`
For each match, decide whether it's prose (wrap in link) or already an attribute/structured data (skip).

- [ ] **Step 2: Wrap each prose mention**

For each prose mention, replace:

```html
I-Yun Lisa Hsieh
```

with:

```html
<a href="/members/iyunlisahsieh/">I-Yun Lisa Hsieh</a>
```

(And same for `謝依芸` if it appears as standalone prose.) Skip mentions inside JSON-LD strings, alt text, or HTML attributes.

- [ ] **Step 3: Build and verify**

Run: `python build.py`
Then: `grep -c 'href="/members/iyunlisahsieh/"' docs/index.html`
Expected: at least 1 (one per prose mention).

- [ ] **Step 4: Commit**

```bash
git add templates/home/about.html
git commit -m "seo: link director-name mentions on homepage to her member subpage"
```

---

## Phase 6 — Build Validation + Runbook

### Task 6.1: Add beautifulsoup4 to deps and skeleton `validate_seo()`

**Files:**
- Modify: `.github/workflows/deploy.yml` (add `beautifulsoup4` to pip install line)
- Modify: `build.py` (add skeleton function + invocation)

- [ ] **Step 1: Update CI install**

In `.github/workflows/deploy.yml`, find:

```yaml
pip install markdown Pillow jinja2 openpyxl
```

Replace with:

```yaml
pip install markdown Pillow jinja2 openpyxl beautifulsoup4
```

- [ ] **Step 2: Install locally**

Run: `conda activate E3website && pip install beautifulsoup4`
Expected: `Successfully installed beautifulsoup4-4.x.x`.

- [ ] **Step 3: Add the skeleton function to `build.py`**

At the end of `build.py` (before the `if __name__ == '__main__':` block, or before any final `print()`), add:

```python
# ── SEO validation ────────────────────────────────────────────────────────────
def validate_seo():
    """Walk rendered docs/ HTML files; emit warnings for SEO regressions.
    Non-fatal — warnings print in yellow, build does not fail.
    """
    from bs4 import BeautifulSoup
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    warnings = []

    def warn(msg):
        warnings.append(msg)
        print(f"{YELLOW}[SEO] {msg}{RESET}")

    # Collected per-page descriptions for duplicate detection
    descriptions = {}  # description -> list of page paths

    for root, _dirs, files in os.walk(output_dir):
        for fname in files:
            if fname != "index.html":
                continue
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, output_dir)
            with open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            _check_page(soup, rel, warn, descriptions)

    # Duplicate-description warnings (after full walk)
    for desc, paths in descriptions.items():
        if len(paths) >= 2:
            warn(f"duplicate description on {len(paths)} pages: {paths[:3]}{'…' if len(paths) > 3 else ''}")

    print(f"\nSEO check: {len(warnings)} warnings (0 errors).")


def _check_page(soup, rel, warn, descriptions):
    """All per-page checks live here. Implemented in subsequent tasks."""
    pass  # filled in by Task 6.2
```

Then add the invocation. Find the existing `generate_sitemap()` call near line 526 and add after it:

```python
print("\nValidating SEO...")
validate_seo()
```

- [ ] **Step 4: Build and verify skeleton runs**

Run: `python build.py`
Expected: build completes; final lines include `Validating SEO...` and `SEO check: 0 warnings (0 errors).`.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/deploy.yml build.py
git commit -m "seo: add validate_seo() skeleton and beautifulsoup4 dependency"
```

### Task 6.2: Implement validation checks

**Files:**
- Modify: `build.py` (`_check_page` function)

- [ ] **Step 1: Implement all six checks**

Replace the `pass` body of `_check_page` with:

```python
def _check_page(soup, rel, warn, descriptions):
    # 1. Description length
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = (desc_tag.get("content", "") if desc_tag else "").strip()
    if not desc:
        warn(f"{rel}: missing meta description")
    else:
        n = len(desc)
        if n < 70:
            warn(f"{rel}: description too short ({n} chars, want ≥70)")
        elif n > 160:
            warn(f"{rel}: description too long ({n} chars, want ≤160)")
        descriptions.setdefault(desc, []).append(rel)

    # 2. Title length
    title_tag = soup.find("title")
    title = (title_tag.string or "").strip() if title_tag else ""
    if not title:
        warn(f"{rel}: missing <title>")
    elif len(title) < 30:
        warn(f"{rel}: title too short ({len(title)} chars, want ≥30)")
    elif len(title) > 60:
        warn(f"{rel}: title too long ({len(title)} chars, want ≤60)")

    # 3. Missing canonical
    if not soup.find("link", attrs={"rel": "canonical"}):
        warn(f"{rel}: missing <link rel=\"canonical\">")

    # 4. JSON-LD parse errors
    for i, block in enumerate(soup.find_all("script", attrs={"type": "application/ld+json"})):
        try:
            json.loads(block.string or "")
        except (json.JSONDecodeError, TypeError) as e:
            warn(f"{rel}: JSON-LD block #{i+1} invalid: {e}")

    # 5. News body word count (only for /news/{slug}/ subsubpages, not the listing)
    if rel.startswith("news/") and rel != "news/index.html":
        article = soup.find("div", class_="news-item-body")
        if article:
            words = len(article.get_text(" ", strip=True).split())
            if words < 200:
                warn(f"{rel}: thin news body ({words} words, want ≥200)")
```

- [ ] **Step 2: Build and observe warnings**

Run: `python build.py 2>&1 | grep "\[SEO\]" | head -20`
Expected: warnings for any pages that don't yet meet the bar (likely some news items with short bodies, possibly some descriptions). The build still completes.

- [ ] **Step 3: Commit**

```bash
git add build.py
git commit -m "seo: implement validate_seo checks for description/title/canonical/jsonld/thin-content"
```

### Task 6.3: Write `SEO-RUNBOOK.md`

**Files:**
- Create: `SEO-RUNBOOK.md` (repo root)

- [ ] **Step 1: Write the runbook**

Create `SEO-RUNBOOK.md`:

```markdown
# SEO Runbook — E3 Center website

Operator-facing notes for keeping the site discoverable in Google.

## One-time setup (already done — documented for future maintainers)

1. **Verify URL-prefix property** in [Google Search Console](https://search.google.com/search-console)
   for `https://e3center.caece.net/`. Verification uses the
   `<meta name="google-site-verification" content="…">` tag in `templates/base.html`.
2. **Submit the sitemap** in GSC → *Sitemaps*: `https://e3center.caece.net/sitemap.xml`.
3. **Link Google Analytics property** `G-JCJPED8JS6` to the GSC property (Admin → Associations).

## After publishing a new news item

1. Push the change. Wait for the GitHub Actions deploy to finish (~2 min).
2. Open GSC → *URL Inspection*, paste the new URL (e.g. `https://e3center.caece.net/news/2026-foo/`).
3. Click **Request Indexing**.
4. Typical lag: hours to a few days. Without this step, lag is weeks-to-never.

## After adding a new member

Same workflow as a news item, but for `https://e3center.caece.net/members/{webId}/`.

## Monthly check (optional, ~5 minutes)

1. GSC → *Performance* → filter by query (e.g. "I-Yun Lisa Hsieh"). Confirm the member subpage's
   average position is improving over time.
2. GSC → *Pages* → look for entries flagged "Discovered – currently not indexed". For each,
   open *URL Inspection* and *Request Indexing*.
3. GSC → *Sitemaps* → confirm latest sitemap fetch shows no errors.

## When the build emits SEO warnings

`python build.py` ends with `SEO check: N warnings (0 errors).` Warnings appear in the GitHub
Actions log on every push. They are non-fatal — the deploy still proceeds — but indicate
quality regressions:

| Warning | What to do |
|---|---|
| `description too short` / `too long` | Add or shorten `metaDescription` (members), `excerpt` (news.json), or `description` (pages.json) for that page. |
| `duplicate description on N pages` | Two pages have identical descriptions. Make at least one unique. |
| `thin news body (N words)` | The article markdown has < 200 words. Expand the article or accept the warning. |
| `missing canonical` / `missing <title>` | Likely a template bug — surface to a developer. |
| `JSON-LD block invalid` | A template change broke JSON syntax — surface to a developer. |

## Manually deindex a page

If a page that should never have been indexed shows up in Google:

1. Add `<meta name="robots" content="noindex, nofollow">` to its `<head>`.
2. Add `Disallow: /path/` to `static/robots.txt`.
3. GSC → *Removals* → submit the URL for temporary removal (~6 months).
```

- [ ] **Step 2: Commit**

```bash
git add SEO-RUNBOOK.md
git commit -m "docs: SEO runbook for content publishers"
```

---

## Final verification

After all phases land:

- [ ] **Step 1: Full build with no SEO warnings (or only expected ones)**

Run: `python build.py 2>&1 | tail -5`
Expected: build succeeds; `SEO check: N warnings (0 errors).` where N is small and known (any remaining warnings are accepted, e.g., a deliberately thin "to be updated" placeholder news item).

- [ ] **Step 2: Validate every JSON-LD block parses**

```bash
python -c "
import json, re, os
total = 0
for root, _, files in os.walk('docs'):
    for f in files:
        if f != 'index.html': continue
        path = os.path.join(root, f)
        html = open(path).read()
        blocks = re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', html, re.S)
        for i, b in enumerate(blocks):
            try: json.loads(b)
            except Exception as e: print(f'FAIL {path}#{i}: {e}'); raise SystemExit(1)
            total += 1
print(f'OK {total} JSON-LD blocks across all pages')
"
```

Expected: `OK N JSON-LD blocks across all pages` with no failures.

- [ ] **Step 3: Run unit tests**

Run: `python -m unittest tests.test_seo_helpers -v`
Expected: all 15 tests pass.

- [ ] **Step 4: Push and observe in GSC over the following weeks**

Push to `source`; GitHub Actions deploys to `gh-pages`. Then:

1. Within 24h: GSC → *Sitemaps* shows the latest sitemap fetched with no errors.
2. Within 1 week: GSC → *URL Inspection* on `/members/iyunlisahsieh/` shows the upgraded JSON-LD and new description.
3. Within 4 weeks: GSC → *Performance* filter "I-Yun Lisa Hsieh" — member subpage average position should improve over baseline.
