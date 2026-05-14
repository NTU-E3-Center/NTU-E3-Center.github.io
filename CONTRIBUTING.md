# Contributing Content

This guide covers how to add or update content on the NTU E3 Center website. You do not need to touch HTML or Python — all content is driven by JSON and Markdown files.

After making changes, [build and preview locally](README.md#local-development) before pushing.

---

## Adding or Updating a Member

Member data has **two halves**:

- **Admin fields** live in `contents/member-info.xlsx` (11 columns: WebID,
  Full Name, Nickname, Chinese Name, Website Section, Admission Year,
  Graduated, Also in Alumni, Alumni Admission Year, Current Position, Batch).
  You control these.
- **Content fields** live in `contents/members/{webId}/` — `member.json`
  (position, emails, interests, profile links), `about.md` (bio prose),
  and `photo.{jpg,png}`. Members supply these.

Do **not** manually edit `contents/structures/members.json` or anything under
`contents/structures/members/` or `contents/articles/members-*/` — those are
gitignored build artifacts regenerated on every build. `contents/member-info.legacy.xlsx`
is a read-only archive of the original spreadsheet — never edit it.

### Updating an existing member

1. Send the member their folder + the instructions:
   ```bash
   cp -r contents/members/{webId} /tmp/pkg/
   cp contents/MEMBER_TEMPLATE/README.md /tmp/pkg/
   # zip /tmp/pkg/ and email it
   ```
2. They edit `member.json` + `about.md` and send the folder back.
3. Drop the returned files into `contents/members/{webId}/`, overwriting.
4. `python build.py` — review `git diff`, commit, push.

### Adding a new member

1. Add a row to `contents/member-info.xlsx` with the 11 admin columns.
2. Seed their folder from the template:
   ```bash
   cp -r contents/MEMBER_TEMPLATE contents/members/{webId}
   ```
3. Send the new folder + `README.md` to the member to fill in.
4. When returned, overwrite `contents/members/{webId}/` with their files
   and drop their `photo.{jpg,png}` into the same folder.
5. `python build.py` — the build **fails** if `member.json` has invalid
   JSON or a schema mismatch, and **warns** about a missing `about.md` or
   photo. Fix any errors, then commit.

`pubName` (used to auto-populate a member's publications) is derived from
the `Full Name` admin column — no separate field to maintain.

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
