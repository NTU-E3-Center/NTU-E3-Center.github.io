import os
import json
import shutil
from datetime import datetime

from lib.site import (env, output_dir, pages, structures, articles,
                      _CENTER_SECTIONS)
from lib import publications
from lib import news
from lib import projects
from lib import members
from lib.assets import convert_to_webp
from lib.members import lazy_img_sizes
from lib.publications import pub_slug, get_pub_sort_key
from lib.news import news_slug_from_pagelink
from config import (SITE_URL, SUBPAGE_IMG_WIDTHS,
                    WEBP_QUALITY, WEBP_LAZY_QUALITY, WEBP_CACHE_DIR)


# Function to render templates into correct directories
def render_templates():
    def process_pages(pages, base_path=""):
        for template_name, page_data in pages.items():
            if isinstance(page_data, dict) and "path" in page_data:
                template_file = page_data.get("template", template_name)
                template = env.get_template(f"{template_file}.html")
                path_segment = page_data["path"]
                canonical = f"{SITE_URL}/{path_segment}/" if path_segment else f"{SITE_URL}/"
                render_args = {
                    "pages": pages,
                    "title": page_data.get("title"),
                    "subpageTitle": page_data.get("subpageTitle"),
                    "suppressSrH1": page_data.get("suppressSrH1", False),
                    "canonicalLink": canonical,
                    "updated_time": datetime.now().strftime("%Y. %m. %d"),
                    "year": datetime.now().year,
                    "structures": structures,
                    "articles": articles
                }
                if "description" in page_data:
                    render_args["description"] = page_data["description"]
                output = template.render(**render_args)
                
                # Define full output path (subdirectories)
                page_dir = os.path.join(output_dir, base_path, page_data["path"])
                os.makedirs(page_dir, exist_ok=True)
                
                # Save the rendered HTML inside index.html
                with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
                    f.write(output)
            elif isinstance(page_data, dict):  # If it's a nested structure without "path"
                process_pages(page_data, os.path.join(base_path, template_name))
    
    process_pages(pages)
    print("Templates rendered successfully!")


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


# Function to copy static assets directly into docs/
def copy_static():
    static_src = "static"
    if os.path.exists(static_src):
        for item in os.listdir(static_src):
            src_path = os.path.join(static_src, item)
            dst_path = os.path.join(output_dir, item)

            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

    print("Static assets copied directly into docs/")


# Function to copy videos directly into docs/
def copy_videos():
    videos_src = "contents/videos"
    video_output_dir = os.path.join(output_dir, "assets/videos")
    if os.path.exists(videos_src):
        os.makedirs(video_output_dir, exist_ok=True)
        for item in os.listdir(videos_src):
            # videos.json is data, not an asset — skip it.
            if item == 'videos.json':
                continue
            src_path = os.path.join(videos_src, item)
            dst_path = os.path.join(video_output_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

    print("Videos copied directly into docs/")


# Compress images and convert to WebP format. Each subpage's image source
# folder is now self-contained; the (source_root, output_folder, sizes) tuples
# describe what to process.

# SUBPAGE_IMG_WIDTHS / MEMBER_IMG_WIDTHS / LAZY_IMG_WIDTHS live in config.py —
# a single source of truth kept in sync with the srcset ladders in templates.
_SUBPAGE_IMAGE_SOURCES = [
    # (source_root,                  docs/assets/<folder>, sizes)
    ('contents/news/images',         'news',               SUBPAGE_IMG_WIDTHS),
    ('contents/group-life/images',   'group-life',         SUBPAGE_IMG_WIDTHS),
    # Projects: walks contents/projects/<slug>/images/* → docs/assets/projects/<slug>/images/*
    ('contents/projects',            'projects',           SUBPAGE_IMG_WIDTHS),
]


def compress_and_convert_images():
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

    for src_root, dst_folder, sizes in _SUBPAGE_IMAGE_SOURCES:
        if not os.path.isdir(src_root):
            continue
        print(f"--- Images found in '{dst_folder}' ---")
        dst_root = os.path.join(output_dir, "assets", dst_folder)
        for root, _, files in os.walk(src_root):
            for fname in files:
                lower = fname.lower()
                path = os.path.join(root, fname)
                # Preserve subdirectory layout under src_root (e.g.
                # contents/news/images/{slug}/0.jpg → docs/assets/news/{slug}/0-Nw.webp).
                rel_dir = os.path.relpath(os.path.dirname(path), src_root)
                dst_subdir = dst_root if rel_dir == '.' else os.path.join(dst_root, rel_dir)
                # SVGs (e.g. partner logos) are vector — copy verbatim instead of
                # rasterising to WebP, so they stay crisp at any size.
                if lower.endswith('.svg'):
                    os.makedirs(dst_subdir, exist_ok=True)
                    shutil.copy2(path, dst_subdir)
                    print(f"{path} → {dst_subdir}/ (svg)")
                    continue
                if not any(lower.endswith(ext) for ext in image_extensions):
                    continue
                os.makedirs(dst_subdir, exist_ok=True)
                convert_to_webp(path, dst_subdir, sizes, compression_quality=WEBP_QUALITY)
                convert_to_webp(path, dst_subdir, lazy_img_sizes, compression_quality=WEBP_LAZY_QUALITY)
                print(f"{path} → {dst_subdir}/")


# Run the build process
if __name__ == "__main__":
    import sys
    # --force-images: drop the encode cache so every variant re-encodes.
    if "--force-images" in sys.argv and os.path.isdir(WEBP_CACHE_DIR):
        shutil.rmtree(WEBP_CACHE_DIR)
    # Start from a clean output dir so content removed from contents/ (a deleted
    # article, a dropped abstract, a renamed slug) can't leave a stale page or a
    # dangling sitemap entry behind. docs/ is gitignored and fully regenerated
    # by the steps below.
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    news.prepare()
    publications.prepare()
    projects.prepare()

    print("Rendering templates...")
    render_templates()
    print("Rendering member pages...")
    members.render_member_pages()
    print("Rendering news item pages...")
    news.render_news_pages()
    print("Rendering publication detail pages...")
    publications.render_publication_pages()
    print("Rendering project detail pages...")
    projects.render_project_pages()
    print("Copying static assets...")
    copy_static()
    print("Copying videos...")
    copy_videos()
    print("Generating sitemap...")
    generate_sitemap()
    print("\nValidating SEO...")
    validate_seo()
    print("Compressing images and converting to WebP format...")
    compress_and_convert_images()
    members.compress_member_images()
    print("Build complete!")
