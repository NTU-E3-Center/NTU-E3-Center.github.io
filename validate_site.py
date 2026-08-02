"""Post-build site audit for the E3 Center build output (docs/).

Mirrors validate_member.py / validate_design_tokens.py: run standalone after
`python build.py`, exit non-zero on failure. Guards the invariants the
2026-08 site audit checked by hand:

  1. Every internal link resolves to a built page, and every fragment link
     points at an id that exists on the target page.
  2. Every public page has exactly one <h1>.
  3. Every public page has a meta description and a canonical link.
  4. Every <img> carries an alt attribute.

Paths served by sibling GitHub Pages repos (valid on the live domain but
absent from this build) go in EXTERNAL_REPO_PATHS. /editor/ is an internal
tool (robots-disallowed) and is exempt from page-shape checks.
"""
import html
import re
import sys
from pathlib import Path

DOCS = Path("docs")

# Live-domain paths served by OTHER repositories in the GitHub org —
# unverifiable from this build output, known to resolve in production.
EXTERNAL_REPO_PATHS = {
    "/Solar-PV-on-Bus-Shelter/",
}

# Pages exempt from the public page-shape checks (not from link checks).
EXEMPT_PAGES = {"/editor/"}

ASSET_PREFIXES = ("/assets", "/css", "/js")


def page_route(index_html: Path) -> str:
    rel = index_html.parent.relative_to(DOCS)
    return "/" if str(rel) == "." else f"/{rel}/"


def main() -> int:
    pages = sorted(DOCS.rglob("index.html"))
    if not pages:
        print("validate_site: no built pages found — run `python build.py` first.")
        return 1

    failures = []
    ids_by_route = {}
    links = []  # (source_route, path, fragment)

    for page in pages:
        route = page_route(page)
        text = page.read_text(encoding="utf-8", errors="replace")
        ids_by_route[route] = set(re.findall(r'\bid="([^"]+)"', text))

        for path, frag in re.findall(r'href="(/[^"#?]*)(#[^"]*)?"', text):
            links.append((route, path, frag))

        if route in EXEMPT_PAGES:
            continue

        h1s = len(re.findall(r"<h1[\s>]", text))
        if h1s != 1:
            failures.append(f"{route}: {h1s} <h1> tags (must be exactly 1)")
        if not re.search(r'<meta name="description"', text):
            failures.append(f"{route}: missing meta description")
        if not re.search(r'rel="canonical"', text):
            failures.append(f"{route}: missing canonical link")
        for img in re.findall(r"<img(?![^>]*\balt=)[^>]*>", text):
            failures.append(f"{route}: <img> without alt ({html.unescape(img)[:60]}…)")

    seen = set()
    for source, path, frag in links:
        if path.startswith(ASSET_PREFIXES):
            continue
        route = path if path.endswith("/") else path + "/"
        if route in EXTERNAL_REPO_PATHS:
            continue
        key = (path, frag)
        if key in seen:
            continue
        target = DOCS / route.strip("/") / "index.html" if route != "/" else DOCS / "index.html"
        if not target.exists() and not (DOCS / path.strip("/")).exists():
            seen.add(key)
            failures.append(f"{source}: dead internal link {path}{frag}")
        elif frag and frag != "#":
            frag_id = frag[1:]
            if frag_id and frag_id not in ids_by_route.get(route, set()):
                seen.add(key)
                failures.append(f"{source}: anchor {path}{frag} — id '{frag_id}' not on target page")

    print(f"validate_site: {len(pages)} pages checked")
    if failures:
        for failure in failures:
            print(f"    {failure}")
        print(f"Site check: {len(failures)} failure(s).")
        return 1
    print("Site check: 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
