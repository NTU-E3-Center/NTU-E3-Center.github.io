# Subpage Header & Template Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sticky branded header to all subpages, move inline styles to static CSS, and reorganise the templates folder into a clean `pages/` subfolder.

**Architecture:** A `subpageTitle` variable passed via `pages.json` triggers a shared header in `base.html`. Template files move to `templates/pages/` with `build.py` reading a new `template` field from `pages.json` to find them. All subpage-specific styles live in a new `static/css/subpage.css`.

**Tech Stack:** Jinja2, Python 3.x, CSS custom properties (already in use)

---

## File Map

| Action | Path |
|--------|------|
| Create | `static/css/subpage.css` |
| Modify | `templates/base.html` |
| Modify | `contents/structures/pages.json` |
| Modify | `build.py` |
| Move + edit | `templates/members-page.html` → `templates/pages/members.html` |
| Move | `templates/news.html` → `templates/pages/news.html` |
| Move | `templates/member.html` → `templates/pages/member/member.html` |

---

### Task 1: Create `static/css/subpage.css`

**Files:**
- Create: `static/css/subpage.css`

- [ ] **Create the file with the sticky header styles**

```css
.subpage-header {
    position: sticky;
    top: 0;
    z-index: 100;
    width: 100%;
    padding: 1rem 2rem;
    background-color: var(--main-bg-color);
    border-bottom: 0.125rem solid var(--main-color);

    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.subpage-header-logo img {
    height: 2.5rem;
    width: auto;
    display: block;
    transition: var(--hover-transition-time);
}

.subpage-header-logo:hover {
    opacity: 0.8;
    translate: var(--block-hover-translate) var(--block-hover-translate);
}

.subpage-header-title {
    font-size: 1.25rem;
    letter-spacing: -0.02em;
    color: var(--main-color);
    opacity: 0.6;
}

@media (width <= 48rem) {
    .subpage-header {
        padding: 0.75rem 1.5rem;
    }

    .subpage-header-logo img {
        height: 2rem;
    }
}
```

- [ ] **Commit**

```bash
git add static/css/subpage.css
git commit -m "feat: add subpage.css with sticky header styles"
```

---

### Task 2: Update `base.html`

**Files:**
- Modify: `templates/base.html`

- [ ] **Add the `subpage.css` link** after the `style.css` link (line 56):

```html
    <!-- css -->
    <link rel="stylesheet" href="/css/general.css?v=2">
    <link rel="stylesheet" href="/css/style.css?v=2">
    <link rel="stylesheet" href="/css/subpage.css?v=1">
```

- [ ] **Add the sticky header block** between the GTM noscript tag and `{% block content %}` (after line 78):

```html
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-M3L6SMNZ" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager (noscript) -->

    {% if subpageTitle %}
    <header class="subpage-header">
        <a class="subpage-header-logo" href="/">
            <img src="/assets/images/e3-logo-text.svg" alt="E3 Center">
        </a>
        <span class="subpage-header-title">{{ subpageTitle }}</span>
    </header>
    {% endif %}

    {% block content %}{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/base.html
git commit -m "feat: add conditional subpage header to base.html"
```

---

### Task 3: Update `pages.json`

**Files:**
- Modify: `contents/structures/pages.json`

- [ ] **Add `subpageTitle` and `template` fields** to the `news` and `members-page` entries. The `index` entry gets no changes (no `subpageTitle` = no header on homepage).

Replace the current `news` and `members-page` entries:

```json
    "news": {
        "path": "news",
        "title": "News | E3 Center",
        "subpageTitle": "News",
        "template": "pages/news"
    },
    "members-page": {
        "path": "members",
        "title": "Members | E3 Center",
        "subpageTitle": "Members",
        "template": "pages/members"
    }
```

- [ ] **Commit**

```bash
git add contents/structures/pages.json
git commit -m "feat: add subpageTitle and template path to pages.json"
```

---

### Task 4: Restructure `templates/` folder

**Files:**
- Move + edit: `templates/members-page.html` → `templates/pages/members.html`
- Move: `templates/news.html` → `templates/pages/news.html`
- Move: `templates/member.html` → `templates/pages/member/member.html`

- [ ] **Create the new directories**

```bash
mkdir -p templates/pages/member
```

- [ ] **Move `news.html`**

```bash
mv templates/news.html templates/pages/news.html
```

- [ ] **Move and rename `members-page.html`, then remove its inline `<style>` block**

```bash
mv templates/members-page.html templates/pages/members.html
```

Open `templates/pages/members.html` and delete the entire `{% block headExtra %}` block (lines 2–22):

```html
{% block headExtra %}
<style>
    .members-logo-bar {
        width: min(calc(100% - 4rem), 75rem);
        margin-inline: auto;
        padding-block-start: 6rem;
    }
    .members-logo-bar a {
        display: inline-block;
        transition: var(--hover-transition-time);
    }
    .members-logo-bar img {
        height: 6rem;
        width: auto;
    }
    .members-logo-bar a:hover {
        opacity: 0.8;
        translate: var(--block-hover-translate) var(--block-hover-translate);
    }
</style>
{% endblock %}
```

Also remove the old logo bar `<div>` from `{% block content %}` (the first element in the block):

```html
<div class="members-logo-bar">
    <a href="/">
        <img src="/assets/images/e3-logo-text.svg" alt="E3 Center logo">
    </a>
</div>
```

The resulting `templates/pages/members.html` starts with:

```html
{% extends "base.html" %}
{% block content %}
<section id="members">
    ...
```

- [ ] **Move `member.html`**

```bash
mv templates/member.html templates/pages/member/member.html
```

- [ ] **Commit**

```bash
git add templates/
git commit -m "refactor: move templates into pages/ subfolder, remove inline styles from members.html"
```

---

### Task 5: Update `build.py`

**Files:**
- Modify: `build.py`

Two changes needed:

1. `render_templates()` currently uses the `pages.json` key as the template filename. Update it to read the optional `template` field, falling back to the key name for backwards compatibility (the `index` page has no `template` field).

2. `render_member_pages()` hardcodes `'member.html'` — update to `'pages/member/member.html'`.

- [ ] **Update `render_templates()` in `build.py`** — change line 95 from:

```python
template = env.get_template(f"{template_name}.html")
```

to:

```python
template_file = page_data.get("template", template_name)
template = env.get_template(f"{template_file}.html")
```

Also pass `subpageTitle` through to the render context — add it to the `template.render(...)` call (line 96–103):

```python
output = template.render(
    pages=pages,
    title=page_data.get("title"),
    subpageTitle=page_data.get("subpageTitle"),
    updated_time=datetime.now().strftime("%Y. %m. %d"),
    year=datetime.now().year,
    structures=structures,
    articles=articles
)
```

- [ ] **Update `render_member_pages()` in `build.py`** — change line 138 from:

```python
template = env.get_template('member.html')
```

to:

```python
template = env.get_template('pages/member/member.html')
```

- [ ] **Commit**

```bash
git add build.py
git commit -m "feat: update build.py to use template field from pages.json and new member template path"
```

---

### Task 6: Verify the build

- [ ] **Run the build**

```bash
conda activate E3website && python build.py
```

Expected output (no errors):
```
Templates rendered successfully!
...
Build complete!
```

- [ ] **Serve locally and check each page**

```bash
cd docs && python -m http.server 8000
```

Check:
1. `http://localhost:8000/` — no subpage header, homepage unchanged
2. `http://localhost:8000/members/` — sticky header with E3 logo + "Members" label visible at top
3. `http://localhost:8000/news/` — sticky header with E3 logo + "News" label visible at top
4. Any member profile (e.g. `http://localhost:8000/members/chihyilu/`) — no subpage header
5. Resize browser to mobile (< 768px) — header padding and logo shrink correctly
6. Scroll down on `/members/` — header stays fixed at top

- [ ] **Commit if any final fixes were needed, otherwise done**
