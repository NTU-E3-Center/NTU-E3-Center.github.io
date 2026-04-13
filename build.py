import os
import re
import json
import shutil
import markdown
import importlib.util
from PIL import Image
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# ── Sync content from Excel before building ───────────────────────────────────
_spec = importlib.util.spec_from_file_location("excel_to_content", "excel_to_content.py")
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
# ─────────────────────────────────────────────────────────────────────────────

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(['templates', 'contents']),
                  trim_blocks=True,
                  lstrip_blocks=True)

# Helper function to get sortable date from publication item
def get_pub_sort_key(item):
    # Extract year and handle 'YY format
    year_str = item.get('year', '0')
    if isinstance(year_str, str) and year_str.startswith("'"):
        year = int("20" + year_str[1:])
    else:
        try:
            year = int(year_str)
        except (ValueError, TypeError):
            year = 2000 # Fallback
            
    # Heuristic for month
    month_str = item.get('month', '')
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    month_num = 0
    for i, m in enumerate(months):
        if m in month_str.lower():
            month_num = i + 1
            break
            
    return (year, month_num)

# Load page structure from an external JSON file
with open("contents/structures/pages.json", "r") as f:
    pages = json.load(f)

# Output directory
output_dir = "docs"

# Load JSON files from contents/structures
structures_path = 'contents/structures'
structures = {}
for filename in os.listdir(structures_path):
    if filename.endswith('.json'):
        file_path = os.path.join(structures_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            # Load JSON content
            data = json.load(f)
        # Create a key based on the file name (without the .json extension)
        var_name = os.path.splitext(filename)[0]
        structures[var_name] = data

# Build in-memory per-member detail lookup (webId -> data) so templates can
# access chiNameEng (full name + optional nickname) without touching any JSON.
_members_detail_path = os.path.join(structures_path, 'members')
members_by_id = {}
if os.path.exists(_members_detail_path):
    for _fname in os.listdir(_members_detail_path):
        if _fname.endswith('.json'):
            _web_id = _fname[:-5]  # strip .json
            with open(os.path.join(_members_detail_path, _fname), 'r', encoding='utf-8') as _f:
                members_by_id[_web_id] = json.load(_f)
structures['members_by_id'] = members_by_id

# Filter and sort publications for home page
if 'publications' in structures:
    home_publications = []
    for section in structures['publications']:
        new_section = section.copy()
        # Filter items with E3: true
        filtered_items = [item for item in section.get('items', []) if item.get('E3') is True]
        # Sort items descending by date
        filtered_items.sort(key=get_pub_sort_key, reverse=True)
        new_section['items'] = filtered_items
        home_publications.append(new_section)
    structures['home_publications'] = home_publications

articles_path = 'contents/articles'
articles = {}
for root, dirs, files in os.walk(articles_path):
    for filename in files:
        if filename.endswith('.md'):
            file_path = os.path.join(root, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
                html_content = markdown.markdown(md_text, extensions=['md_in_html'])
            # Key is relative path from articles_path, without extension, using forward slashes
            rel_path = os.path.relpath(file_path, articles_path)
            var_name = os.path.splitext(rel_path)[0].replace(os.sep, '/')
            articles[var_name] = html_content

# Function to render templates into correct directories
def render_templates():
    def process_pages(pages, base_path=""):
        for template_name, page_data in pages.items():
            if isinstance(page_data, dict) and "path" in page_data:
                template_file = page_data.get("template", template_name)
                template = env.get_template(f"{template_file}.html")
                path_segment = page_data["path"]
                canonical = f"https://e3center.caece.net/{path_segment}/" if path_segment else "https://e3center.caece.net/"
                output = template.render(
                    pages=pages,
                    title=page_data.get("title"),
                    subpageTitle=page_data.get("subpageTitle"),
                    canonicalLink=canonical,
                    updated_time=datetime.now().strftime("%Y. %m. %d"),
                    year=datetime.now().year,
                    structures=structures,
                    articles=articles
                )
                
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


# Function to render individual member pages from contents/structures/members/*.json
def render_member_pages():
    members_structures_path = 'contents/structures/members'
    if not os.path.exists(members_structures_path):
        print("No member structures directory found, skipping member pages.")
        return

    # Build research lookup dict: researchId -> topic data
    research_by_id = {}
    for section in structures.get('research', []):
        for topic in section.get('topics', []):
            research_by_id[topic['researchId']] = topic

    # Build publication lookup dict: citationId -> publication data (skip items under review)
    pub_by_id = {}
    for section in structures.get('publications', []):
        for item in section.get('items', []):
            if 'citationId' in item:
                pub_by_id[item['citationId']] = item

    template = env.get_template('pages/member/member.html')

    for group in structures.get('members', []):
        for member_base in group.get('members', []):
            page_structure_path = member_base.get('pageStructure')
            if not page_structure_path:
                continue

            if os.path.exists(page_structure_path):
                with open(page_structure_path, 'r', encoding='utf-8') as f:
                    try:
                        member_details = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON from {page_structure_path}")
                        member_details = {}
            else:
                print(f"Warning: pageStructure file not found: {page_structure_path}")
                member_details = {}

            # Merge member details, using base data as defaults
            member = member_details.copy()
            member.update(member_base)

            if 'pageLink' not in member:
                continue

            # Pre-render any markdown files referenced in aboutSection and positionSection
            about_content = {}
            page_content = member.get('pageContent', {})
        
            for section in page_content.get('aboutSection', []):
                md_path = section.get('content', '')
                if md_path and os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    about_content[md_path] = markdown.markdown(md_text, extensions=['md_in_html'])
            pos_section = page_content.get('positionSection', {})
        
            if pos_section:
                md_path = pos_section.get('content', '')
                if md_path and os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    about_content[md_path] = markdown.markdown(md_text, extensions=['md_in_html'])
        
            # Load specific member interest
            member_id = None
            if page_structure_path:
                member_id = os.path.splitext(os.path.basename(page_structure_path))[0]
            else:
                member_id = member.get('studentId')

            if member_id:
                interest_path = f"contents/articles/members-interest/{member_id}.md"
                if os.path.exists(interest_path):
                    with open(interest_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    member['interest_content'] = markdown.markdown(md_text, extensions=['md_in_html'])

            # Auto-populate Journal Publications if pubName is set
            pub_name = member.get('pubName')
            if pub_name:
                matching_items = []
                for pub_section in structures.get('publications', []):
                    for item in pub_section.get('items', []):
                        if 'citationId' in item and pub_name in item.get('authors', ''):
                            # Extract year and month for sorting
                            year = item.get('year', 0)
                            month_str = item.get('month', '')
                        
                            # Very basic heuristic for month to help sorting (e.g. "Jan." -> 1, "Feb." -> 2)
                            months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
                            month_num = 0
                            for i, m in enumerate(months):
                                if m in month_str.lower():
                                    month_num = i + 1
                                    break
                                
                            matching_items.append({
                                'id': item['citationId'],
                                'year': year,
                                'month': month_num
                            })
            
                # Sort descending by year, then descending by month
                matching_items.sort(key=lambda x: (x['year'], x['month']), reverse=True)
            
                matching_citations = [item['id'] for item in matching_items]
            
                pub_sections = page_content.setdefault('PublicationSection', [])
                journal_section = next((s for s in pub_sections if s.get('sectionTitle') == 'Journal Publications'), None)
            
                if not journal_section:
                    journal_section = {
                        "sectionTitle": "Journal Publications",
                        "publications": []
                    }
                    pub_sections.insert(0, journal_section)
                
                journal_section['publications'] = matching_citations

            output = template.render(
                pages=pages,
                member=member,
                research_by_id=research_by_id,
                pub_by_id=pub_by_id,
                about_content=about_content,
                structures=structures,
                year=datetime.now().year,
            )

            page_dir = os.path.join(output_dir, member['pageLink'].lstrip('/'))
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Member page generated: {member['pageLink']}")

    print("Member pages rendered successfully!")


# Function to render individual news item pages from news.json
def render_news_pages():
    template = env.get_template('pages/news/news-item.html')
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    for section in structures.get('news', []):
        for item in section.get('items', []):
            page_link = item.get('pageLink')
            if not page_link:
                continue

            # Derive slug from pageLink (e.g. /news/2026-foo/ → 2026-foo)
            slug = page_link.strip('/').split('/')[-1]

            # Load markdown article content
            article_key = f'news/{slug}'
            news_content = articles.get(article_key)

            # Discover images from contents/images/news/{slug}/
            img_folder = os.path.join('contents', 'images', 'news', slug)
            news_images = []
            if os.path.exists(img_folder):
                files = sorted(
                    [f for f in os.listdir(img_folder)
                     if not f.startswith('.') and
                     any(f.lower().endswith(ext) for ext in image_extensions)],
                    key=lambda x: (0, int(x.rsplit('.', 1)[0])) if x.rsplit('.', 1)[0].isdigit() else (1, x)
                )
                news_images = [f'/assets/news/{slug}/{f}' for f in files]

            item = dict(item)
            if news_content:
                item['content'] = news_content

            # Use 0.jpg (or 0.png etc.) as the hero image if present
            if not item.get('imgPath') and os.path.exists(img_folder):
                for ext in image_extensions:
                    hero_candidate = os.path.join(img_folder, f'0{ext}')
                    if os.path.exists(hero_candidate):
                        item['imgPath'] = f'/assets/news/{slug}/0{ext}'
                        news_images = [img for img in news_images
                                       if img.split('/')[-1] != f'0{ext}']
                        break

            output = template.render(
                news=item,
                news_images=news_images,
                pages=pages,
                structures=structures,
                year=datetime.now().year,
            )

            page_dir = os.path.join(output_dir, page_link.lstrip('/'))
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"News item page generated: {page_link}")

    print("News item pages rendered successfully!")


# Function to generate sitemap.xml with all indexable pages
def generate_sitemap():
    from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
    today = datetime.now().strftime("%Y-%m-%d")
    BASE = "https://e3center.caece.net"

    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    def add_url(loc, changefreq="monthly", priority="0.7", lastmod=today):
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = loc
        SubElement(url_el, "lastmod").text = lastmod
        SubElement(url_el, "changefreq").text = changefreq
        SubElement(url_el, "priority").text = priority

    # Static pages
    add_url(f"{BASE}/", changefreq="weekly", priority="1.0")
    add_url(f"{BASE}/members/", changefreq="monthly", priority="0.8")
    add_url(f"{BASE}/publications/", changefreq="monthly", priority="0.8")
    add_url(f"{BASE}/news/", changefreq="weekly", priority="0.8")

    # Member pages (deduplicated — some members appear in multiple groups)
    seen_member_links = set()
    for group in structures.get('members', []):
        for member in group.get('members', []):
            link = member.get('pageLink')
            if link and link not in seen_member_links:
                seen_member_links.add(link)
                add_url(f"{BASE}{link}/", changefreq="monthly", priority="0.6")

    # News item pages
    for section in structures.get('news', []):
        for item in section.get('items', []):
            link = item.get('pageLink')
            if link:
                add_url(f"{BASE}{link}", changefreq="yearly", priority="0.5")

    tree = ElementTree(urlset)
    indent(tree, space="  ")
    sitemap_path = os.path.join(output_dir, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="unicode", xml_declaration=False)
    print(f"Sitemap written to {sitemap_path}")


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


# Function to copy news images preserving subfolder structure
def copy_news_images():
    src = os.path.join('contents', 'images', 'news')
    dst = os.path.join(output_dir, 'assets', 'news')
    if os.path.exists(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    print("News images copied.")


# Function to copy videos directly into docs/
def copy_videos():
    videos_src = "contents/videos"
    video_output_dir = os.path.join(output_dir, "assets/videos")
    if os.path.exists(videos_src):
        os.makedirs(video_output_dir, exist_ok=True)
        for item in os.listdir(videos_src):
            src_path = os.path.join(videos_src, item)
            dst_path = os.path.join(video_output_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

    print("Videos copied directly into docs/")


# Compress images and convert to WebP format
images_path = 'contents/images'
members_img_sizes = [200, 400, 600, 800]
globals()[r'group-life_img_sizes'] = [200, 400, 600, 800, 1200, 1600, 2000]
lazy_img_sizes = [20]

def get_separated_image_paths(directory):
    """
    Finds image paths and separates them by their top-level subdirectory.

    Args:
        directory (str): The path to the main directory (e.g., 'contents/images').

    Returns:
        dict: A dictionary where keys are folder names and values are lists of
              image file paths within those folders.
    """
    separated_paths = {}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

    # First, find all top-level subdirectories
    try:
        # List items in the base directory and filter for directories
        subdirectories = [item for item in os.listdir(directory)
                          if os.path.isdir(os.path.join(directory, item))]
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' was not found.")
        return {}

    # Now, walk through each subdirectory to find images
    for subdir in subdirectories:
        image_list = []
        subdir_path = os.path.join(directory, subdir)
        for root, _, files in os.walk(subdir_path):
            for file in files:
                # Check for valid, non-SVG image extensions
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_list.append(os.path.join(root, file))

        # Only add the folder to the dictionary if it contains images
        if image_list:
            separated_paths[subdir] = image_list

    return separated_paths

def convert_to_webp(path, dst_path, sizes, compression_quality=100):
    basename = os.path.splitext(os.path.basename(path))[0]
    with Image.open(path) as img:
        for size in sizes:
            img_resized = img.resize((size, int(size * img.height / img.width)))
            webp_output_path = f"{dst_path}/{basename}-{size}w.webp"
            img_resized.save(webp_output_path, "WEBP", quality=compression_quality)


def compress_and_convert_images():
    image_paths_by_folder = get_separated_image_paths(images_path)

    for folder, paths in image_paths_by_folder.items():
        sizes_key = f'{folder}_img_sizes'
        if sizes_key not in globals():
            print(f"--- Skipping '{folder}' (no size config — handled separately) ---")
            continue
        print(f"--- Images found in '{folder}' ---")
        dst_path = f"docs/assets/{folder}"
        os.makedirs(dst_path, exist_ok=True)
        for path in paths:
            convert_to_webp(path, dst_path, globals()[sizes_key], compression_quality=70)
            convert_to_webp(path, dst_path, lazy_img_sizes, compression_quality=10)
            print(f"{path} converted to WebP")
        

# Run the build process
if __name__ == "__main__":
    print("Rendering templates...")
    render_templates()
    print("Rendering member pages...")
    render_member_pages()
    print("Rendering news item pages...")
    render_news_pages()
    print("Copying static assets...")
    copy_static()
    print("Copying news images...")
    copy_news_images()
    print("Copying videos...")
    copy_videos()
    print("Generating sitemap...")
    generate_sitemap()
    print("Compressing images and converting to WebP format...")
    compress_and_convert_images()
    print("Build complete!")
