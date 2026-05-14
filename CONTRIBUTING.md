# Contributing Content

This guide covers how to add or update content on the NTU E3 Center website. You do not need to touch HTML or Python — all content is driven by JSON and Markdown files.

After making changes, [build and preview locally](README.md#local-development) before pushing.

---

## Adding or Updating a Member

Member data is managed entirely through `contents/member-info.xlsx`. Do **not** manually edit `members.json`, per-member JSON files, or member Markdown files — they are auto-generated and will be overwritten on every build.

### 1. Edit the member spreadsheet

Open `contents/member-info.xlsx` and add or update a row for the member. Key columns:

- **WebID** — unique identifier used for file names, page URLs, and image paths (e.g. `firstnamelastname`)
- **pubName** — the name as it appears in publication author lists (e.g. `F. Lastname`); used to auto-populate their publications page
- **Section** — which group they belong to (e.g. `PhD Students`, `Full-time`, `Alumni`)
- **About / Position / Interests** — bio text, education/experience, and research interest bullet points

### 2. Add the member's photo

Place the photo (JPG or PNG) in `contents/images/members/` named `{webId}.jpg` (or `.png`).

The build script will automatically compress and convert it to WebP at multiple sizes.

### 3. Run the build

```bash
python build.py
```

`lib/excel_to_content.py` runs first and auto-generates:
- `contents/structures/members.json`
- `contents/structures/members/{webId}.json`
- `contents/articles/members-{about,position,interest}/{webId}.md`

---

## Adding a Publication

Open `contents/structures/publications.json`. Find the correct section (e.g., `"Journal Articles"`, `"Conference Papers"`) and add an entry to its `items` array:

```json
{
  "citationId": "lastname2025title",
  "authors": "F. Lastname, A. Coauthor",
  "title": "Publication Title",
  "journal": "Journal Name",
  "year": 2025,
  "month": "Jan.",
  "E3": true
}
```

- `citationId` — unique identifier; used to reference this publication from member pages
- `E3: true` — set this to show the publication in the home page publications section
- `authors` — must include the member's `pubName` exactly for it to appear on their profile page automatically

---

## Adding a News Item

Open `contents/structures/news.json` and add an entry:

```json
{
  "date": "2025-06-01",
  "title": "News headline here",
  "content": "Short description of the news item."
}
```

Keep entries sorted with the most recent first.

---

## Adding Group Life Photos

### 1. Add the image

Place the photo (JPG or PNG) in `contents/images/group-life/`. The build script will generate WebP versions at sizes: 200w, 400w, 600w, 800w, 1200w, 1600w, 2000w.

### 2. Register it in `group-life.json`

Open `contents/structures/group-life.json` and add an entry:

```json
{
  "image": "filename-without-extension",
  "caption": "Event name or short description",
  "date": "2025-06"
}
```

---

## Editing Page Text

For the **About** and **Contact** sections, edit the corresponding Markdown files:

- `contents/articles/about.md`
- `contents/articles/contact.md`

Standard Markdown is supported. HTML inside Markdown blocks is also supported via the `md_in_html` extension.

---

## Workflow Summary

```
Edit JSON / Markdown / images
        ↓
python build.py
        ↓
Preview at http://localhost:8000
        ↓
git add + commit + push to source branch
        ↓
GitHub Actions builds and deploys automatically
```
