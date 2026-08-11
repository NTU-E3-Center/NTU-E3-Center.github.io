import os
import json
from datetime import datetime

from config import SITE_URL
from lib.site import output_dir, structures
from lib.publications import pub_slug
from lib.news import news_slug_from_pagelink


# Function to generate sitemap.xml with all indexable pages
def generate_sitemap():
    from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
    today = datetime.now().strftime("%Y-%m-%d")

    def file_mtime(path):
        """Return ISO date of file's last modification, or today if file is missing.
        Logs a warning for non-FileNotFoundError OSErrors so real issues surface."""
        try:
            return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
        except FileNotFoundError:
            return today
        except OSError as e:
            print(f"Warning: cannot stat {path}: {e}")
            return today

    def latest_mtime(*paths):
        """Return ISO date of the most recent mtime across the given files/dirs.
        Directories are walked recursively. Missing paths are silently skipped.
        Falls back to today if nothing is found."""
        latest = 0.0
        for p in paths:
            if not os.path.exists(p):
                continue
            if os.path.isfile(p):
                latest = max(latest, os.path.getmtime(p))
            else:
                for root, _, files in os.walk(p):
                    for name in files:
                        try:
                            latest = max(latest, os.path.getmtime(os.path.join(root, name)))
                        except OSError:
                            pass
        if latest == 0.0:
            return today
        return datetime.fromtimestamp(latest).strftime("%Y-%m-%d")

    BASE = SITE_URL

    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    def add_url(loc, changefreq="monthly", priority="0.7", lastmod=today):
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = loc
        SubElement(url_el, "lastmod").text = lastmod
        SubElement(url_el, "changefreq").text = changefreq
        SubElement(url_el, "priority").text = priority

    # Static pages — lastmod reflects the most recent change to that page's
    # actual sources (data files + templates), not the build date.
    add_url(f"{BASE}/", changefreq="weekly", priority="1.0",
            lastmod=latest_mtime("contents/about", "contents/contact", "contents/group-life",
                                 "contents/news", "contents/publications", "contents/research",
                                 "contents/videos", "contents/projects",
                                 "templates/home", "templates/index.html", "templates/base.html"))
    add_url(f"{BASE}/about/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/about", "templates/pages/about.html"))
    add_url(f"{BASE}/members/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/members/member-info.xlsx", "contents/members",
                                 "templates/pages/members.html"))
    add_url(f"{BASE}/students/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/members/member-info.xlsx", "contents/members",
                                 "templates/pages/students.html"))
    add_url(f"{BASE}/publications/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/publications/publications.json",
                                 "templates/pages/publications.html"))
    add_url(f"{BASE}/news/", changefreq="weekly", priority="0.8",
            lastmod=latest_mtime("contents/news/news.json",
                                 "templates/pages/news.html"))
    add_url(f"{BASE}/research/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/research/research.json",
                                 "templates/pages/research.html"))
    add_url(f"{BASE}/projects/", changefreq="monthly", priority="0.8",
            lastmod=latest_mtime("contents/projects/projects.json",
                                 "templates/pages/projects.html"))
    add_url(f"{BASE}/contact/", changefreq="yearly", priority="0.6",
            lastmod=latest_mtime("contents/contact", "templates/pages/contact.html"))
    add_url(f"{BASE}/group-life/", changefreq="monthly", priority="0.6",
            lastmod=latest_mtime("contents/group-life/group-life.json"))

    # Member pages — lastmod reflects the most recent change to that member's
    # own folder, the roster spreadsheet, or the publications list (since pubs
    # auto-populate onto the member page).
    seen_member_links = set()
    for group in structures.get('members', []) + structures.get('students', []):
        for member in group.get('members', []):
            link = member.get('pageLink')
            if link and link not in seen_member_links:
                seen_member_links.add(link)
                web_id = link.rstrip('/').split('/')[-1]
                add_url(f"{BASE}{link}/", changefreq="monthly", priority="0.7",
                        lastmod=latest_mtime(f"contents/members/{web_id}",
                                             "contents/members/member-info.xlsx",
                                             "contents/publications/publications.json"))

    # News item pages — lastmod reflects the article body, its images, and the
    # news.json entry (which supplies title/date shown on the page).
    for section in structures.get('news', []):
        for item in section.get('items', []):
            link = item.get('pageLink')
            if link:
                slug = news_slug_from_pagelink(link)
                add_url(f"{BASE}{link}", changefreq="yearly", priority="0.6",
                        lastmod=latest_mtime(f"contents/news/articles/{slug}.md",
                                             f"contents/news/images/{slug}",
                                             "contents/news/news.json"))

    # Publication detail pages — one per entry with an abstract. lastmod tracks
    # the publications data file (the page is rendered entirely from it).
    for section in structures.get('publications', []):
        for item in section.get('items', []):
            if item.get('abstract'):
                add_url(f"{BASE}/publications/{item.get('slug') or pub_slug(item)}/",
                        changefreq="yearly", priority="0.6",
                        lastmod=latest_mtime("contents/publications/publications.json"))

    # Project detail pages — one per flagship entry (slug + folder). lastmod tracks
    # the project's own folder and the projects listing data file.
    for section in structures.get('projects', []):
        for item in section.get('items', []):
            if item.get('pageLink'):
                slug = item['slug']
                add_url(f"{BASE}{item['pageLink']}", changefreq="monthly", priority="0.6",
                        lastmod=latest_mtime(f"contents/projects/{slug}",
                                             "contents/projects/projects.json"))

    tree = ElementTree(urlset)
    indent(tree, space="  ")
    sitemap_path = os.path.join(output_dir, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="unicode", xml_declaration=False)
    print(f"Sitemap written to {sitemap_path}")


# ── SEO validation ────────────────────────────────────────────────────────────
def validate_seo():
    """Walk rendered docs/ HTML files; emit warnings for SEO regressions.

    Non-fatal — warnings print in yellow, build does not fail. Implemented as
    a skeleton in Task 6.1; checks added in Task 6.2.
    """
    from bs4 import BeautifulSoup
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    warnings = []

    def warn(msg):
        warnings.append(msg)
        print(f"{YELLOW}[SEO] {msg}{RESET}")

    # Collected per-page descriptions for duplicate detection (used in Task 6.2)
    descriptions = {}  # description -> list of page paths

    for root, _dirs, files in os.walk(output_dir):
        for fname in files:
            if fname != "index.html":
                continue
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, output_dir)
            with open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            _check_page(soup, rel, warn, descriptions)

    # Duplicate-description warnings (after full walk; populated in Task 6.2)
    for desc, paths in descriptions.items():
        if len(paths) >= 2:
            warn(f"duplicate description on {len(paths)} pages: {paths[:3]}{'…' if len(paths) > 3 else ''}")

    print(f"\nSEO check: {len(warnings)} warnings (0 errors).")


def _check_page(soup, rel, warn, descriptions):
    """All per-page checks live here. Implemented in Task 6.2."""
    # 0. Pages marked noindex (e.g. the /editor dashboard) are invisible to
    # search engines, so none of the SEO checks below apply to them.
    robots = soup.find("meta", attrs={"name": "robots"})
    if robots and "noindex" in (robots.get("content") or "").lower():
        return

    # 1. Description length + duplicate detection
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = (desc_tag.get("content", "") if desc_tag else "").strip()
    if not desc:
        warn(f"{rel}: missing meta description")
    else:
        n = len(desc)
        if n < 70:
            warn(f"{rel}: description too short ({n} chars, want ≥70)")
        elif n > 160:
            warn(f"{rel}: description too long ({n} chars, want ≤160)")
        descriptions.setdefault(desc, []).append(rel)

    # 2. Title length
    title_tag = soup.find("title")
    title = (title_tag.string or "").strip() if title_tag else ""
    if not title:
        warn(f"{rel}: missing <title>")
    elif len(title) < 30:
        warn(f"{rel}: title too short ({len(title)} chars, want ≥30)")
    elif len(title) > 60:
        warn(f"{rel}: title too long ({len(title)} chars, want ≤60)")

    # 3. Missing canonical
    if not soup.find("link", attrs={"rel": "canonical"}):
        warn(f"{rel}: missing <link rel=\"canonical\">")

    # 4. JSON-LD parse errors
    for i, block in enumerate(soup.find_all("script", attrs={"type": "application/ld+json"})):
        try:
            json.loads(block.string or "")
        except (json.JSONDecodeError, TypeError) as e:
            warn(f"{rel}: JSON-LD block #{i+1} invalid: {e}")

    # 5. News body word count (only for /news/{slug}/ subsubpages, not the listing)
    if rel.startswith("news/") and rel != "news/index.html":
        article = soup.find("div", class_="news-item-body")
        if article:
            words = len(article.get_text(" ", strip=True).split())
            if words < 200:
                warn(f"{rel}: thin news body ({words} words, want ≥200)")
