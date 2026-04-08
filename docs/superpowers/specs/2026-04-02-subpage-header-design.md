# Subpage Header & Template Restructure

**Date:** 2026-04-02
**Status:** Approved

## Context

The site has two page tiers:
- **Homepage** (`/`) — standalone, animated, hero layout
- **Subpages** (`/members/`, `/news/`, and future `/publications/` etc.) — content pages that need consistent branding and navigation
- **Sub-subpages** (individual member profiles) — to be redesigned separately

Currently `members-page.html` carries an inline `<style>` block for its logo bar, and there is no shared header component for subpages. This design extracts that into a reusable sticky header, restructures the template folder, and sets up a clean foundation for future subpages.

---

## 1. Sticky Subpage Header

A slim sticky header rendered on all subpages. Shows the E3 logo (links to `/`) and the current page name as a breadcrumb. The existing floating `.menu-btn` is unchanged.

**Renders when:** `subpageTitle` is defined in the Jinja2 context. The homepage has no `subpageTitle` key so the header is absent there automatically.

**Markup added to `base.html`** (before `{% block content %}`):

```html
{% if subpageTitle is defined %}
<header class="subpage-header">
    <a class="subpage-header-logo" href="/">
        <img src="/assets/images/e3-logo-text.svg" alt="E3 Center">
    </a>
    <span class="subpage-header-title">{{ subpageTitle }}</span>
</header>
{% endif %}
```

---

## 2. New CSS File: `static/css/subpage.css`

Scoped entirely to `.subpage-header`. Linked in `base.html` alongside `general.css` and `style.css`.

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

The inline `<style>` block in `members-page.html` is deleted (fully superseded).

---

## 3. `pages.json` Changes

Add `subpageTitle` to each non-home page. The template path is updated to reflect the new folder structure.

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

No Python changes to `build.py` needed — the full page dict is already passed to Jinja2, so `subpageTitle` becomes available in `base.html` automatically.

---

## 4. Template Folder Restructure

```
templates/
├── base.html                     (unchanged)
├── index.html                    (unchanged)
├── pages/                        ← new subfolder
│   ├── members.html              ← renamed from members-page.html
│   ├── news.html                 ← moved from root
│   └── member/
│       └── member.html           ← moved from root, isolated for future redesign
├── home/                         (unchanged)
└── partials/                     (unchanged)
```

**`build.py` update required:**
- `render_member_pages()` hardcodes the template path — update from `"member.html"` to `"pages/member/member.html"`

---

## 5. Files Changed

| Action | File |
|--------|------|
| Edit | `templates/base.html` — add header block + link subpage.css |
| Create | `static/css/subpage.css` |
| Edit | `contents/structures/pages.json` — add `subpageTitle` + update template paths |
| Move + rename | `templates/members-page.html` → `templates/pages/members.html` |
| Move | `templates/news.html` → `templates/pages/news.html` |
| Move | `templates/member.html` → `templates/pages/member/member.html` |
| Edit | `build.py` — update `render_member_pages()` template path |
| Delete | Inline `<style>` block from `members-page.html` (now `members.html`) |

---

## 6. Verification

1. Run `python build.py` — should complete without errors
2. Open `http://localhost:8000/members/` — sticky header appears with E3 logo + "Members"
3. Open `http://localhost:8000/news/` — sticky header appears with "News"
4. Open `http://localhost:8000` — no subpage header, homepage unchanged
5. Open any member profile page — no subpage header (handled later)
6. Resize to mobile — header padding and logo size reduce correctly
