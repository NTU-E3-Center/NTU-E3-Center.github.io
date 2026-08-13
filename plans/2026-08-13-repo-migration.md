# Repo migration → NTU-E3Center

**Date:** 2026-08-13
**From:** `NTU-E3-Center/NTU-E3-Center.github.io`
**To:** `NTU-E3Center/website` (name TBC)
**Live site:** https://e3center.caece.net — **this migration can take the site down**, see step 4.

## Rights check (done, 2026-08-13)

| Requirement | Status |
|---|---|
| Admin on the source repo (authorises transfer out) | ✅ `permissions.admin: true` |
| Create repos in `NTU-E3Center` (authorises transfer in) | ✅ `members_can_create_repositories: true` |
| Org role | "member" in **both** orgs — this does **not** block the transfer |

GitHub requires repo-admin on the source plus create-rights on the destination, not
org ownership. Both are satisfied.

## What does NOT need changing

- `.github/workflows/deploy.yml` — repo-agnostic: `actions/checkout` + `GITHUB_TOKEN`,
  no hardcoded owner or URL. It rebuilds and pushes `gh-pages` wherever it lives.
- `config.py` `SITE_URL` — already the custom domain (`https://e3center.caece.net`),
  not the `*.github.io` host.
- `static/CNAME` — contains `e3center.caece.net`; travels with the repo and keeps
  the custom domain attached after transfer.
- Only stale mentions of the old name are in `plans/*.md` and `STRUCTURE.md`
  (old local paths). Cosmetic.

## Current production facts

- Default branch: `source`. Pages builds from the **`gh-pages`** branch (status: built).
- DNS: `e3center.caece.net` → CNAME → `ntu-e3-center.github.io` → GitHub Pages IPs
  (185.199.108–111.153).
- Repo is public, 467 MB on disk (heavy media in history: a 25 MB image, a 17 MB
  member photo, a 16 MB video, several ~10 MB PDFs).

## Steps, in order

1. **Transfer** — old repo → Settings → General → Danger Zone → *Transfer ownership* →
   target `NTU-E3Center`. GitHub sets up automatic redirects from the old URL, so
   existing clones and links keep working.
2. **Rename** to `website` (new repo → Settings → General → Repository name).
   Note this turns it from an *org site* (`<org>.github.io`) into a *project site*.
   Harmless because the custom domain overrides the Pages URL either way.
3. **Re-check Pages** — new repo → Settings → Pages. Confirm source is still branch
   `gh-pages` and the custom domain still reads `e3center.caece.net`. Re-enter the
   domain if it was cleared by the transfer, and let the HTTPS certificate re-issue
   (can take up to an hour; "Enforce HTTPS" may be greyed out until then).
4. **DNS** — update the CNAME record for `e3center.caece.net`:
   `ntu-e3-center.github.io` → `ntu-e3center.github.io` (no hyphen before "Center").
   In practice all `*.github.io` hosts resolve to the same Pages IPs and GitHub routes
   by Host header, so the site may keep working on the stale target — but GitHub
   documents pointing it at the new owner, and domain verification can depend on it.
   Update it. **`caece.net` is the department's domain, so this likely goes through
   NTU IT — start it early, it is the long pole.**
5. **Local remote** — after the transfer:
   `git remote set-url origin https://github.com/NTU-E3Center/website.git`
   then `git fetch origin` to confirm.
6. **Re-apply what does not transfer** — branch protection rules and any repository
   secrets or variables (none apparent in this repo), plus the Pages environment if
   the deploy workflow ever gains one.

## Verify after cutover

```bash
curl -sI https://e3center.caece.net | head -3          # expect 200 from GitHub.com
git remote -v && git fetch origin && git status -sb    # remote points at the new org
```

Then push a trivial commit to `source` and confirm the Actions run appears in the
**new** repo and republishes `gh-pages`.

## Optional, separate from the move

The 467 MB history is large for a static site. It pushes fine and GitHub only warns
above ~1 GB, but if it ever becomes a problem the fix is rewriting history to drop
the large blobs (`git filter-repo`) — which rewrites every commit SHA and breaks
existing clones. Do it as its own deliberate exercise, never bundled with a move.
