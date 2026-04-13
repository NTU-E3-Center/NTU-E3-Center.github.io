# SEO & JSON-LD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-page canonical URLs, Open Graph / Twitter Card tags, JSON-LD structured data (Organization, Person, NewsArticle), and a generated sitemap.xml to improve Google Search discoverability and rich-result eligibility.

**Architecture:** Templates are Jinja2; `build.py` renders them at build time. All SEO additions are static strings baked into the HTML at build — no runtime JS. JSON-LD blocks are injected via a `{% block jsonld %}` extension point added to `base.html`; the two standalone templates (`member.html`, `news-item.html`) receive their own inline fixes since they do not extend `base.html`. Sitemap is generated in a new `generate_sitemap()` function in `build.py`.

**Tech Stack:** Python 3.9, Jinja2, standard `xml.etree.ElementTree` (stdlib) for sitemap

---

## Constants used throughout

```
BASE_URL = "https://e3center.caece.net"
```

Year stored in JSON as `'24` (apostrophe + 2-digit). Full year = `"20" + year[1:]`.

---

## Task 1: Fix hardcoded canonical + add Twitter Cards to base.html

**Files:**
- Modify: `templates/base.html:14` (canonical), `templates/base.html:21` (og:type), `templates/base.html:23–25` (after og tags)
- Modify: `build.py:112–119` (render_templates — pass canonicalLink)

- [ ] **Step 1: Replace hardcoded canonical in base.html**

In `templates/base.html`, change line 14 from:
```html
    <link href="https://e3center.caece.net" rel="canonical" />
```
to:
```html
    {% set _canonical = canonicalLink if canonicalLink is defined else defaultCanonicalLink %}
    <link rel="canonical" href="{{ _canonical }}" />
```

- [ ] **Step 2: Fix og:type to allow per-page override**

Change line 18 from:
```html
    <meta property="og:type" content="website" />
```
to:
```html
    <meta property="og:type" content="{{ ogType if ogType is defined else 'website' }}" />
```

- [ ] **Step 3: Add Twitter/X Card meta tags after the og:site_name line (after line 22)**

Add after `<meta property="og:site_name" content="E3 Center" />`:
```html
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{{ title if title is defined else defaultTitle }}" />
    <meta name="twitter:description" content="{{ description if description is defined else defaultDescription }}" />
    <meta name="twitter:image" content="https://e3center.caece.net/assets/i/og-image-1200x630.png" />
```

- [ ] **Step 4: Add JSON-LD extension block in base.html <head> (after headExtra block, line 74)**

Add before `</head>`:
```html
    {% block jsonld %}{% endblock %}
```

- [ ] **Step 5: Update render_templates() in build.py to pass per-page canonicalLink**

In `build.py`, inside `process_pages()`, change the `template.render(...)` call to add `canonicalLink`:

```python
path_segment = page_data["path"]
canonical = f"https://e3center.caece.net/{path_segment}/" if path_segment else "https://e3center.caece.net/"
output = template.render(
    pages=pages,
    title=page_data.get("title"),
    subpageTitle=page_data.get("subpageTitle"),
    canonicalLink=canonical,
    updated_time=datetime.now().strftime("%Y. %m. %d"),
    year=datetime.now().year,
    structures=structures,
    articles=articles
)
```

- [ ] **Step 6: Build and verify**

```bash
conda activate E3website && python build.py 2>&1 | tail -5
```
Expected: `Build complete!` with no errors.

Then check `docs/index.html` for the canonical and Twitter card tags:
```bash
grep -n "canonical\|twitter:card" docs/index.html | head -10
```
Expected: lines showing `<link rel="canonical" href="https://e3center.caece.net/"/>` and `<meta name="twitter:card" content="summary_large_image" />`.

Also check a subpage:
```bash
grep -n "canonical" docs/news/index.html
```
Expected: `<link rel="canonical" href="https://e3center.caece.net/news/"/>`.

- [ ] **Step 7: Commit**

```bash
cd /Users/jianhern/Desktop/Github/NTU-E3-Center.github.io
git add templates/base.html build.py
git commit -m "seo: fix per-page canonical, add Twitter cards, add jsonld block"
```

---

## Task 2: Add Organization JSON-LD to homepage

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add Organization JSON-LD block in index.html**

In `templates/index.html`, after `{% set isHomePage = True %}`, add:

```html
{% block jsonld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ResearchOrganization",
  "name": "E3 Center",
  "alternateName": "Energy, Environment, and Economy Research Center",
  "url": "https://e3center.caece.net",
  "logo": "https://e3center.caece.net/assets/i/og-image-1200x630.png",
  "description": "Housed in the Department of Civil Engineering at National Taiwan University (NTU), E3 research center, directed by Professor I-Yun Lisa Hsieh (謝依芸), is dedicated to overcoming the challenges of sustainable energy transition.",
  "parentOrganization": {
    "@type": "CollegeOrUniversity",
    "name": "National Taiwan University",
    "alternateName": "NTU",
    "url": "https://www.ntu.edu.tw"
  },
  "founder": {
    "@type": "Person",
    "name": "I-Yun Lisa Hsieh",
    "alternateName": "謝依芸",
    "url": "https://e3center.caece.net/members/lisa-hsieh/",
    "sameAs": "https://scholar.google.com.tw/citations?user=tUbPb-QAAAAJ"
  },
  "sameAs": [
    "https://github.com/NTU-E3-Center"
  ]
}
</script>
{% endblock %}
```

- [ ] **Step 2: Build and verify**

```bash
conda activate E3website && python build.py 2>&1 | tail -3
grep -A 5 'application/ld+json' docs/index.html | head -10
```
Expected: JSON-LD block with `"@type": "ResearchOrganization"` visible in `docs/index.html`.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "seo: add Organization JSON-LD to homepage"
```

---

## Task 3: Fix member.html — canonical, OG tags, Person JSON-LD

**Files:**
- Modify: `templates/pages/member/member.html`

The member template does NOT extend base.html so all additions go directly into its `<head>`.

- [ ] **Step 1: Add canonical + OG + Twitter tags to member.html head**

After line 9 (`<meta name="author" ...>`), add:

```html
    <link rel="canonical" href="https://e3center.caece.net{{ member['pageLink'] }}" />

    <meta property="og:url" content="https://e3center.caece.net{{ member['pageLink'] }}" />
    <meta property="og:title" content="{{ member['chiNameEng'] }} | E3 Center" />
    <meta property="og:type" content="profile" />
    <meta property="og:image" content="https://e3center.caece.net/assets/i/og-image-1200x630.png" />
    <meta property="og:description" content="{{ member['chiNameEng'] }} — member of E3 Center, National Taiwan University." />
    <meta property="og:locale" content="en_US" />
    <meta property="og:site_name" content="E3 Center" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{{ member['chiNameEng'] }} | E3 Center" />
    <meta name="twitter:description" content="{{ member['chiNameEng'] }} — member of E3 Center, National Taiwan University." />
    <meta name="twitter:image" content="https://e3center.caece.net/assets/i/og-image-1200x630.png" />
```

- [ ] **Step 2: Fix description meta to use member-specific text**

Change line 7 from:
```html
    <meta name="description" content="Housed in the Department of Civil Engineering at National Taiwan University (NTU), E3 research group, directed by Professor I-Yun Lisa Hsieh (謝依芸), is dedicated to overcoming the challenges of sustainable energy transition.">
```
to:
```html
    <meta name="description" content="{{ member['chiNameEng'] }} — member of E3 Center, National Taiwan University. Research in sustainable energy transition.">
```

- [ ] **Step 3: Add Person JSON-LD before </head>**

Before `</head>` (line 53), add:

```html
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Person",
      "name": "{{ member['chiNameEng'] }}",
      "alternateName": "{{ member['chiName'] }}",
      "url": "https://e3center.caece.net{{ member['pageLink'] }}",
      "jobTitle": "{{ member.get('position', '') }}",
      "worksFor": {
        "@type": "ResearchOrganization",
        "name": "E3 Center",
        "url": "https://e3center.caece.net"
      }{% if member.get('pageContent', {}).get('links') %},
      "sameAs": [{% for tag in member['pageContent']['links'] %}{% if tag.get('link') %}"{{ tag['link'] }}"{% if not loop.last %},{% endif %}{% endif %}{% endfor %}]
      {% endif %}
    }
    </script>
```

- [ ] **Step 4: Build and check a member page**

```bash
conda activate E3website && python build.py 2>&1 | tail -3
```
Find a generated member page and check it:
```bash
ls docs/members/ | head -5
```
Then (substitute actual member dir name):
```bash
grep -n "canonical\|ld+json\|twitter:card" docs/members/$(ls docs/members/ | head -1)/index.html | head -15
```
Expected: canonical, OG, Twitter card, and Person JSON-LD lines all present.

- [ ] **Step 5: Commit**

```bash
git add templates/pages/member/member.html
git commit -m "seo: add canonical, OG, Twitter card, Person JSON-LD to member pages"
```

---

## Task 4: Fix news-item.html — canonical, OG tags, NewsArticle JSON-LD

**Files:**
- Modify: `templates/pages/news/news-item.html`

Year in news JSON is stored as `'24` (apostrophe + 2-digit). Full year in Jinja2: `"20" ~ news['year'][1:]`.

- [ ] **Step 1: Fix description meta (line 7)**

Change:
```html
    <meta name="description" content="{{ news['title'] }} — E3 Center, National Taiwan University.">
```
to:
```html
    <meta name="description" content="{{ news['title'][:155] }} — E3 Center, National Taiwan University.">
```

- [ ] **Step 2: Add canonical + OG + Twitter tags after line 9 (keywords meta)**

After `<meta name="keywords" ...>`, add:

```html
    <link rel="canonical" href="https://e3center.caece.net{{ news['pageLink'] }}" />

    <meta property="og:url" content="https://e3center.caece.net{{ news['pageLink'] }}" />
    <meta property="og:title" content="{{ news.get('shortTitle', news['title']) }} | E3 Center" />
    <meta property="og:type" content="article" />
    <meta property="og:image" content="{{ 'https://e3center.caece.net' ~ news['imgPath'] if news.get('imgPath') else 'https://e3center.caece.net/assets/i/og-image-1200x630.png' }}" />
    <meta property="og:description" content="{{ news['title'][:155] }} — E3 Center, National Taiwan University." />
    <meta property="og:locale" content="en_US" />
    <meta property="og:site_name" content="E3 Center" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{{ news.get('shortTitle', news['title']) }} | E3 Center" />
    <meta name="twitter:description" content="{{ news['title'][:155] }} — E3 Center, National Taiwan University." />
    <meta name="twitter:image" content="{{ 'https://e3center.caece.net' ~ news['imgPath'] if news.get('imgPath') else 'https://e3center.caece.net/assets/i/og-image-1200x630.png' }}" />
```

- [ ] **Step 3: Pass pageLink into news-item template render in build.py**

In `build.py`, inside `render_news_pages()`, the `item` dict already contains `pageLink`. Confirm the template render call includes `news=item` (it does on line 318). No build.py change needed — `news['pageLink']` is already available in the template.

- [ ] **Step 4: Add NewsArticle JSON-LD before </head> (line 52)**

Before `</head>` add:

```html
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": {{ news['title'] | tojson }},
      "url": "https://e3center.caece.net{{ news['pageLink'] }}",
      "datePublished": "20{{ news['year'][1:] }}-{{ news['month'] }}",
      "author": {
        "@type": "Organization",
        "name": "E3 Center",
        "url": "https://e3center.caece.net"
      },
      "publisher": {
        "@type": "Organization",
        "name": "E3 Center",
        "logo": {
          "@type": "ImageObject",
          "url": "https://e3center.caece.net/assets/i/og-image-1200x630.png"
        }
      }{% if news.get('imgPath') %},
      "image": "https://e3center.caece.net{{ news['imgPath'] }}"
      {% endif %}
    }
    </script>
```

- [ ] **Step 5: Build and check a news item page**

```bash
conda activate E3website && python build.py 2>&1 | tail -3
ls docs/news/
```
Pick a news item directory and verify:
```bash
grep -n "canonical\|ld+json\|twitter:card" docs/news/$(ls docs/news/ | grep -v index | head -1)/index.html | head -15
```
Expected: canonical, OG, Twitter, NewsArticle JSON-LD all present.

- [ ] **Step 6: Commit**

```bash
git add templates/pages/news/news-item.html
git commit -m "seo: add canonical, OG, Twitter card, NewsArticle JSON-LD to news item pages"
```

---

## Task 5: Generate sitemap.xml in build.py

**Files:**
- Modify: `build.py` — add `generate_sitemap()` function and call it in `__main__`

The sitemap lists every indexable URL with `<lastmod>` set to today's date and appropriate `<changefreq>` + `<priority>`.

- [ ] **Step 1: Add generate_sitemap() function to build.py**

Add this function after `render_news_pages()` (before `copy_static`):

```python
def generate_sitemap():
    from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
    today = datetime.now().strftime("%Y-%m-%d")
    BASE = "https://e3center.caece.net"

    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    def add_url(loc, changefreq="monthly", priority="0.7", lastmod=today):
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = loc
        SubElement(url_el, "lastmod").text = lastmod
        SubElement(url_el, "changefreq").text = changefreq
        SubElement(url_el, "priority").text = priority

    # Static pages
    add_url(f"{BASE}/", changefreq="weekly", priority="1.0")
    add_url(f"{BASE}/members/", changefreq="monthly", priority="0.8")
    add_url(f"{BASE}/publications/", changefreq="monthly", priority="0.8")
    add_url(f"{BASE}/news/", changefreq="weekly", priority="0.8")

    # Member pages
    for group in structures.get('members', []):
        for member in group.get('members', []):
            link = member.get('pageLink')
            if link:
                add_url(f"{BASE}{link}", changefreq="monthly", priority="0.6")

    # News item pages
    for section in structures.get('news', []):
        for item in section.get('items', []):
            link = item.get('pageLink')
            if link:
                add_url(f"{BASE}{link}", changefreq="yearly", priority="0.5")

    tree = ElementTree(urlset)
    indent(tree, space="  ")
    sitemap_path = os.path.join(output_dir, "sitemap.xml")
    with open(sitemap_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="unicode", xml_declaration=False)
    print(f"Sitemap written to {sitemap_path}")
```

Note: `xml.etree.ElementTree.indent` requires Python 3.9+ — the project already uses 3.9.

- [ ] **Step 2: Call generate_sitemap() in __main__ block**

In `build.py`, in the `if __name__ == "__main__":` block, add after `copy_videos()` call:

```python
    print("Generating sitemap...")
    generate_sitemap()
```

- [ ] **Step 3: Build and verify sitemap**

```bash
conda activate E3website && python build.py 2>&1 | grep -E "Sitemap|error|Error"
```
Expected: `Sitemap written to docs/sitemap.xml`

```bash
head -30 docs/sitemap.xml
```
Expected: valid XML with `<urlset>`, `<url>` entries for `/`, `/members/`, `/news/`, `/publications/`, and individual member/news URLs.

```bash
grep -c "<url>" docs/sitemap.xml
```
Expected: at least 10 URLs (4 static + members + news items).

- [ ] **Step 4: Commit**

```bash
git add build.py
git commit -m "seo: generate sitemap.xml with all pages, members, and news items"
```

---

## Self-Review

- **Spec coverage:** All 7 priority items from audit covered: canonical (Task 1), JSON-LD block (Task 1), Organization (Task 2), Person (Task 3), NewsArticle (Task 4), sitemap (Task 5), Twitter cards (Tasks 1/3/4). ✓
- **Placeholder scan:** No TBD/TODO. All code blocks are complete. ✓
- **Type consistency:** `news['pageLink']`, `member['pageLink']`, `member['chiNameEng']` used consistently. `news['year'][1:]` used in both Task 4 description and JSON-LD code. ✓
- **Ambiguity:** `news['pageLink']` is available in the template because `item` (which contains it) is passed as `news=item` in `render_news_pages()` — confirmed in build.py:318. ✓
