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
