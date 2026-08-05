# Students & Alumni Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate students + alumni from "E3 Center members": `/members/` = PI + Staff, new `/students/` = Ph.D. + Master + Alumni, homepage drops Ph.D. students.

**Architecture:** Partition the roster once in `build.py` into `structures['members']` (center) and `structures['students']` (research group). Templates consume their own list with no filtering. Profile URLs `/members/{id}/` are untouched.

**Tech Stack:** Python 3.12 (`~/miniconda3/envs/E3website/bin/python`), Jinja2 via custom `build.py`, static output in `docs/` (gitignored).

**Spec:** `specs/2026-08-05-students-split-design.md`

## Global Constraints

- Build command: `~/miniconda3/envs/E3website/bin/python build.py` — must end `Build complete!` with **0 SEO warnings** in output.
- Preview only on port **8001** (or another free port ≥8001). Port 8000 is a production backend — NEVER bind or kill it. Check with `ss -tlnp | grep :8001` before serving; a stale `python3 -m http.server 8001` from this repo may already be running and can be reused or killed, but never touch other processes.
- `lib/excel_to_content.py` must NOT be modified.
- Individual profile URLs stay `/members/{id}/` for every person. No redirects.
- Meta descriptions ≤160 characters (build audit enforces this).
- If any CSS file changes, bump its `?v=N` query in **all five** templates that link it: `templates/base.html` plus the four standalone detail templates (`templates/pages/member/member.html`, `templates/pages/news/news-item.html`, `templates/pages/publications/publication.html`, `templates/pages/projects/project.html` — verify exact list with `grep -rln 'subpage.css?v=' templates/`).
- Commits: conventional prefix, stage files by explicit name, never `git add .`, no Co-Authored-By trailers.
- All work on branch `students-split` (already created, spec committed).

---

### Task 1: Partition the roster in build.py

**Files:**
- Modify: `build.py` (near line 211, plus consumer loops near lines 422 and 821, plus sitemap near line 800)
- Modify: `templates/pages/about.html` (line 28 — live counts need the full roster)

**Interfaces:**
- Produces: `structures['members']` = list of section groups whose `sectionTitle` is `'Principal Investigator'` or `'Staff'`; `structures['students']` = the remaining groups (`'Ph.D. Students'`, `'Master Students'`, `'Alumni'`), in original order. Group dict shape is unchanged (`sectionTitle`, `form`, `members`, and for Alumni: `filter`, `filterId`, `filterTitle`, `filterDefaultCheck`).
- Consumed by: Tasks 2–4 templates.

- [ ] **Step 1: Split the structures assignment**

In `build.py`, replace the single assignment at line 211:

```python
structures['members'] = _member_data['members_listing']
```

with:

```python
# Center members (PI + staff) vs. Prof. Hsieh's research-group students
# (Ph.D., Master, Alumni) — split once here so every template and JSON-LD
# block consumes the right roster without per-template filtering.
# Spec: specs/2026-08-05-students-split-design.md
_CENTER_SECTIONS = ('Principal Investigator', 'Staff')
structures['members'] = [
    g for g in _member_data['members_listing']
    if g['sectionTitle'] in _CENTER_SECTIONS]
structures['students'] = [
    g for g in _member_data['members_listing']
    if g['sectionTitle'] not in _CENTER_SECTIONS]
```

- [ ] **Step 2: Repoint the two full-roster loops in build.py**

Both loops must cover everyone (students still get profile pages and sitemap entries):

Near line 422 (member detail page generation):
```python
    for group in structures.get('members', []) + structures.get('students', []):
```

Near line 821 (sitemap member-pages loop):
```python
    for group in structures.get('members', []) + structures.get('students', []):
```

- [ ] **Step 3: Fix the about-page live counts**

`templates/pages/about.html` line 28 counts Ph.D./Master/Staff/Alumni from `structures['members']` — now missing students. Change:

```jinja
{% for group in structures['members'] %}
```

to:

```jinja
{% for group in structures['members'] + structures['students'] %}
```

- [ ] **Step 4: Build and verify the partition**

```bash
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | tail -3
```
Expected: `Build complete!`, no SEO warnings. (Templates still render: members.html/home members iterate `structures['members']` and simply show fewer groups; index.html org JSON-LD likewise.)

Then verify output:

```bash
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re, sys
h = open('docs/index.html', encoding='utf-8').read()
s = h.index('<section id="members"'); e = h.index('<section id="publications"')
eyebrows = re.findall(r'section-eyebrow">([^<]+)', h[s:e])
assert eyebrows == ['Principal Investigator', 'Staff'], eyebrows
m = open('docs/members/index.html', encoding='utf-8').read()
titles = re.findall(r'mem-group-title">([^<]+)', m)
assert titles == ['Principal Investigator', 'Staff'], titles
import os
assert os.path.exists('docs/members/chihyilu/index.html'), 'student profile page missing!'
sm = open('docs/sitemap.xml', encoding='utf-8').read()
assert '/members/chihyilu/' in sm, 'student profile missing from sitemap'
about = open('docs/about/index.html', encoding='utf-8').read()
print('OK — partition verified')
EOF
```
Expected: `OK — partition verified`. Also manually open `docs/about/index.html` and confirm the Ph.D./Master/Alumni counts are non-zero (grep the numbers near "Ph.D." in the stats block).

- [ ] **Step 5: Commit**

```bash
git add build.py templates/pages/about.html
git commit -m "feat(build): partition roster into center members and students"
```

---

### Task 2: /students/ page + navigation

**Files:**
- Create: `templates/pages/students.html`
- Modify: `contents/pages.json` (pages registry + index nav structure)

**Interfaces:**
- Consumes: `structures['students']` from Task 1.
- Produces: `/students/` page with group anchors `#phd-students`, `#master-students`, `#alumni` (slug scheme: `sectionTitle|lower|replace('.','')|replace(' ','-')`).

- [ ] **Step 1: Create templates/pages/students.html**

Copy `templates/pages/members.html` as the starting point, then apply ALL of these changes (the body loop, M-form rows, and Alumni S-form grid/filter markup are reused verbatim — only the list and page identity change):

1. Meta block at top:
```jinja
{% extends "base.html" %}
{% set title = 'Students & Alumni · E3 Center · NTU 台大' %}
{% set description = 'Ph.D. and Master students, and alumni of Prof. I-Yun Lisa Hsieh\'s research group at National Taiwan University, working on the energy transition.' %}
{% set keywords = 'E3 Center students, Hsieh research group, NTU PhD students, NTU Master students, E3 alumni, I-Yun Lisa Hsieh, 謝依芸, 台大, 國立臺灣大學, sustainable energy researchers' %}
{% set canonicalLink = 'https://e3center.caece.net/students/' %}
```
(description above is 156 chars — keep under 160 if edited.)

2. JSON-LD CollectionPage: change `"name"` to `"Students & Alumni | E3 Center"`, `"url"` to `https://e3center.caece.net/students/`, and iterate `structures.get('students', [])` in the ItemList.

3. JSON-LD BreadcrumbList: position 2 name `"Students & Alumni"`.

4. Body: `{% set subpageTitle = 'Students & Alumni' %}` if members.html sets one (mirror whatever heading mechanism members.html uses — check its `section-title` / `subpageTitle` usage and replicate with the new title). The content loop becomes:
```jinja
{% for group in structures['students'] %}
```
Everything inside the loop (mem-group rows for form != 'S', Alumni grid + year filter for form == 'S') stays identical to members.html.

- [ ] **Step 2: Register the page in contents/pages.json**

In the top-level pages map (sibling of `"members-page"`), add:

```json
    "students-page": {
        "path": "students",
        "title": "Students & Alumni · E3 Center · NTU 台大",
        "template": "pages/students"
    },
```
(Mirror the exact key set of `"members-page"` — open it and copy its shape, only changing path/title/template.)

- [ ] **Step 3: Restructure the People nav**

In `contents/pages.json` `index.structure`, replace the members entry's subnav and add a students entry after it:

```json
        {
            "id": "members",
            "title": "Members",
            "link": "/members",
            "icon": "/assets/sprite.svg#svg-members",
            "navGroup": "People"
        },
        {
            "id": "students",
            "title": "Students & Alumni",
            "link": "/students",
            "icon": "/assets/sprite.svg#svg-members",
            "navGroup": "People",
            "subnav": [
                { "title": "Ph.D. Students", "link": "/students/#phd-students" },
                { "title": "Master Students", "link": "/students/#master-students" },
                { "title": "Alumni", "link": "/students/#alumni" }
            ]
        },
```

Notes: the members entry loses its subnav entirely (two anchors is too thin for a dropdown — spec decision). The homepage section loop uses `{% include 'home/' ~ section.id ~ '.html' ignore missing %}` — there is no `home/students.html`, and `ignore missing` makes that a no-op by design. 

- [ ] **Step 4: Add /students/ to the sitemap**

In `build.py`, directly after the `/members/` `add_url` call (near line 800):

```python
    add_url(f"{BASE}/students/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/members/member-info.xlsx", "contents/members",
                                 "templates/pages/students.html"))
```

- [ ] **Step 5: Build and verify**

```bash
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | tail -3
```
Expected: `Build complete!`, 0 SEO warnings (the audit checks the new page's description length).

```bash
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re
s = open('docs/students/index.html', encoding='utf-8').read()
titles = re.findall(r'mem-group-title">([^<]+)', s)
assert titles == ['Ph.D. Students', 'Master Students', 'Alumni'], titles
for anchor in ('id="phd-students"', 'id="master-students"', 'id="alumni"'):
    assert anchor in s, anchor
assert 'filter-checkbox' in s, 'alumni year filter missing'
assert 'https://e3center.caece.net/students/' in s, 'canonical missing'
sm = open('docs/sitemap.xml', encoding='utf-8').read()
assert '<loc>https://e3center.caece.net/students/</loc>' in sm
h = open('docs/index.html', encoding='utf-8').read()
assert '/students/' in h, 'nav link missing on homepage'
print('OK — students page verified')
EOF
```
Expected: `OK — students page verified`.

- [ ] **Step 6: Commit**

```bash
git add templates/pages/students.html contents/pages.json build.py
git commit -m "feat(students): add /students/ listing page and People nav split"
```

---

### Task 3: Slim down /members/

**Files:**
- Modify: `templates/pages/members.html`

**Interfaces:**
- Consumes: `structures['members']` (center-only after Task 1).

- [ ] **Step 1: Prune the dead Alumni branch**

The `{% else %}` branch (`form == 'S'`, the Alumni grid + filter, roughly lines 127–190) can never match a center-only list. Delete the `{% else %}` branch so the loop keeps only the `form != 'S'` row rendering, and keep the loop's `{% if %}`→`{% endif %}` structure valid. Build must still pass (Step 4 verifies).

- [ ] **Step 2: Rewrite meta description and keywords**

Replace lines 2–3:

```jinja
{% set description = 'The E3 Center team at National Taiwan University — Director Prof. I-Yun Lisa Hsieh (謝依芸) and center staff driving research on the energy transition.' %}
{% set keywords = 'E3 Center members, E3 Center staff, NTU sustainable energy lab, NTU civil engineering, I-Yun Lisa Hsieh, 謝依芸, 台大, 國立臺灣大學, research center team' %}
```
(description above is 149 chars.)

- [ ] **Step 3: Add the students link-card**

After the closing `{% endfor %}` of the group loop, before the section's closing tag, add:

```jinja
    <div class="section-cta">
        <a class="section-cta-btn skewed-block" href="/students/" b-role="btn" b-hoverable>
            <span>Looking for Prof. Hsieh's students &amp; alumni?</span>
            <svg><use href="/assets/sprite.svg#svg-arrow-right"></use></svg>
        </a>
    </div>
```

(`.section-cta` / `.section-cta-btn` are the existing homepage CTA classes and are styled globally — verify visually in Step 4; if the subpage context needs spacing, scope a rule under `.members-subpage .section-cta` in `static/css/subpage.css` and bump `?v=` in all five templates per Global Constraints.)

- [ ] **Step 4: Build and verify**

```bash
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | tail -3
```

```bash
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re
m = open('docs/members/index.html', encoding='utf-8').read()
titles = re.findall(r'mem-group-title">([^<]+)', m)
assert titles == ['Principal Investigator', 'Staff'], titles
assert 'mem-alum-grid' not in m, 'alumni branch not fully pruned'
assert '/students/' in m, 'students link-card missing'
d = re.search(r'name="description" content="([^"]+)"', m).group(1)
assert len(d) <= 160, (len(d), d)
print('OK — members page verified')
EOF
```
Expected: `OK — members page verified`.

- [ ] **Step 5: Commit**

```bash
git add templates/pages/members.html
git commit -m "feat(members): restrict /members/ to PI and staff, link to /students/"
```

---

### Task 4: Homepage — PI + Staff, two CTAs

**Files:**
- Modify: `templates/home/members.html`
- Verify only (no expected change): `templates/index.html`

**Interfaces:**
- Consumes: `structures['members']` (center-only).

- [ ] **Step 1: Remove the dead homepage exclusion**

In `templates/home/members.html` line 7, remove the now-dead condition:

```jinja
{% if not (isHomePage and members['sectionTitle'] in ['Master Students', 'Alumni']) %}
```
and its matching `{% endif %}` (the second-to-last `{% endif %}` before the `{% endfor %}` at line 153 — re-indent the block or leave indentation as-is to keep the diff readable; Jinja is whitespace-insensitive here). The `form == 'S'` branch (lines 93–151) is also now dead — delete it, keeping the `L` and `M` branches.

- [ ] **Step 2: Two CTAs**

Replace the existing `section-cta` block (lines 155–162):

```jinja
    {% if isHomePage %}
    <div class="section-cta">
        <a class="section-cta-btn skewed-block" href="/members/" b-role="btn" b-hoverable>
            <span>View center members</span>
            <svg><use href="/assets/sprite.svg#svg-arrow-right"></use></svg>
        </a>
        <a class="section-cta-btn skewed-block" href="/students/" b-role="btn" b-hoverable>
            <span>Meet the students</span>
            <svg><use href="/assets/sprite.svg#svg-arrow-right"></use></svg>
        </a>
    </div>
    {% endif %}
```

Check `.section-cta` in `static/css/style.css` — if it isn't already a flex row with a gap that handles two buttons (wrapping on phone), add:

```css
#members .section-cta {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-3);
}
```
in the homepage stylesheet where `.section-cta` is defined, and bump that stylesheet's `?v=` in all five templates per Global Constraints. Skip entirely if the existing rule already renders both buttons cleanly.

- [ ] **Step 3: Verify index.html JSON-LD needs no change**

`templates/index.html:27` iterates `structures.get('members', [])` for the Organization `member` array — after Task 1 this is already center-only, which is the desired end state. Confirm in the build output (next step) that no student appears; make no edit.

- [ ] **Step 4: Build and verify**

```bash
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | tail -3
```

```bash
~/miniconda3/envs/E3website/bin/python - <<'EOF'
import re, json
h = open('docs/index.html', encoding='utf-8').read()
s = h.index('<section id="members"'); e = h.index('<section id="publications"')
seg = h[s:e]
eyebrows = re.findall(r'section-eyebrow">([^<]+)', seg)
assert eyebrows == ['Principal Investigator', 'Staff'], eyebrows
assert seg.count('section-cta-btn') == 2, 'expected two CTAs'
assert '/students/' in seg and '/members/' in seg
ld = re.search(r'"@type": "ResearchOrganization".*?</script>', h, re.S).group(0)
assert 'chihyilu' not in ld, 'student still listed as org member in JSON-LD'
assert 'iyunlisahsieh' in ld
print('OK — homepage verified')
EOF
```
Expected: `OK — homepage verified`.

- [ ] **Step 5: Commit**

```bash
git add templates/home/members.html
git commit -m "feat(home): show only PI and staff with members/students CTAs"
```
(Include any CSS file + the five cache-bust template edits in the same commit if Step 2 needed them.)

---

### Task 5: Full local verification (user gate before push)

**Files:** none (verification only)

- [ ] **Step 1: Clean rebuild + validators**

```bash
~/miniconda3/envs/E3website/bin/python build.py 2>&1 | tail -5
~/miniconda3/envs/E3website/bin/python validate_design_tokens.py
```
Expected: `Build complete!`, 0 SEO warnings, `Design token check: 0 failures.`

- [ ] **Step 2: Serve the preview**

```bash
ss -tlnp 2>/dev/null | grep ':8001' || (cd docs && nohup python3 -m http.server 8001 >/dev/null 2>&1 &)
```
If 8001 is held by a non-repo process, use 8002+ and say so.

- [ ] **Step 3: Report for user visual check — do NOT push**

Ask the user to verify at the preview URL: homepage members section (PI + Staff + two CTAs, desktop/tablet/phone), `/members/`, `/students/` (including the alumni year filter and the three nav anchors), and the People dropdown in the desktop header + mobile drawer. Wait for explicit approval before any push. After approval, push branch `students-split` and open a PR against `source` (git-commit-push skill rules apply).
