# Repo migration → NTU-E3Center/E3-Center-Website, deployed by Cloudflare Pages

**Date:** 2026-08-13
**From:** `NTU-E3-Center/NTU-E3-Center.github.io` (GitHub Pages, `gh-pages` branch)
**To:** `NTU-E3Center/E3-Center-Website` (Cloudflare Pages, built from `source`)
**Live site:** https://e3center.caece.net — the DNS cutover is the only step that
can take it down; everything else is reversible.

## Rights check (verified 2026-08-13)

| Requirement | Status |
|---|---|
| Admin on the source repo (authorises transfer out) | ✅ `permissions.admin: true` |
| Create repos in `NTU-E3Center` (authorises transfer in) | ✅ `members_can_create_repositories: true` |
| Org role | "member" in **both** orgs — does **not** block the transfer |

GitHub requires repo-admin on the source plus create-rights on the destination,
not org ownership.

## Cloudflare Pages build settings

| Setting | Value |
|---|---|
| Production branch | `source` |
| Build command | `pip install -r requirements.txt && python build.py && python validate_design_tokens.py && python validate_site.py` |
| Build output directory | `docs` |
| Environment variable | `PYTHON_VERSION` = `3.12` (matches `.python-version`) |

The two validators are appended deliberately: on GitHub Actions they gate the
deploy, so a token regression or a dead link blocks publishing. Cloudflare treats
a non-zero exit as a failed build, which preserves exactly that safety net. Drop
them from the command and broken output ships silently.

### Pre-flight against Cloudflare's limits (checked 2026-08-13)

| Limit | This site | Verdict |
|---|---|---|
| 20,000 files per deployment | 956 | fine |
| 25 MiB per served file | largest is `assets/videos/2025-1.mp4` at 17 MB | fine, but close-ish |
| Build timeout (20 min) | ~2 min locally, image reprocessing dominates | fine |

Dependencies are pure Python with manylinux wheels (Pillow ships WebP support),
so no system packages are needed in the build image.

**Slow-build note:** `build.py` regenerates every WebP variant on every run and
Cloudflare clones a 470 MB repo each time. Expect multi-minute builds. If it ever
becomes painful the fix is caching or skipping unchanged images, not trimming the
build command.

## Steps, in order

1. **Transfer** — old repo → Settings → General → Danger Zone → *Transfer ownership*
   → `NTU-E3Center`. GitHub auto-redirects the old URL, so existing clones keep working.
2. **Rename** to `E3-Center-Website` (Settings → General → Repository name).
3. **Create the Cloudflare Pages project** — Workers & Pages → Create → Pages →
   Connect to Git → pick `NTU-E3Center/E3-Center-Website` → enter the build settings
   above. Let the first build finish and check the `*.pages.dev` preview URL renders
   before touching DNS. **The live site is still on GitHub Pages at this point.**
4. **Custom domain in Cloudflare** — Pages project → Custom domains → add
   `e3center.caece.net`. Cloudflare shows the DNS record it wants.
5. **DNS** — repoint `e3center.caece.net`:
   from CNAME → `ntu-e3-center.github.io`
   to   CNAME → `<project>.pages.dev`
   `caece.net` is the department's domain, so this likely goes through NTU IT —
   **start the request early, it is the long pole.** A subdomain CNAME to
   `pages.dev` works even though the zone is not on Cloudflare nameservers.
6. **Local remote** — after the transfer:
   ```
   git remote set-url origin https://github.com/NTU-E3Center/E3-Center-Website.git
   git fetch origin
   ```
7. **Retire the GitHub Pages deploy** — once Cloudflare serves the live domain:
   - strip the `Deploy to GitHub Pages` step from `.github/workflows/deploy.yml`,
     keeping checkout → install → build → validate as a PR/CI check (still worth
     having: it catches breakage before Cloudflare builds it),
   - delete the `gh-pages` branch,
   - turn off Pages in the repo settings so two systems aren't claiming the domain.
   Do this **after** cutover, not before — `gh-pages` is the rollback.

## Rollback

Until step 7, GitHub Pages is still building and `gh-pages` still holds a good
build. Reverting DNS to `ntu-e3-center.github.io` restores the old deploy.

## Verify after cutover

```bash
curl -sI https://e3center.caece.net | head -5     # expect 200; server should be cloudflare
git remote -v && git fetch origin                 # remote points at the new org
```

Then push a trivial commit to `source` and confirm Cloudflare builds and publishes it.

## Optional, separate from the move

The 467 MB history is large for a static site — it slows every Cloudflare clone.
Rewriting it (`git filter-repo`) to drop the biggest blobs (a 25 MB image, a 17 MB
member photo, a 16 MB video, several ~10 MB PDFs) would shrink it a lot, but
rewrites every commit SHA and breaks existing clones. Do it as its own deliberate
exercise, never bundled with a move.
