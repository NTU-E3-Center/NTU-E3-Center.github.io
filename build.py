import os
import shutil
from datetime import datetime

from lib.site import (env, output_dir, pages, structures, articles,
                      _CENTER_SECTIONS)
from lib import publications
from lib import news
from lib import projects
from lib import members
from lib import assets
from lib import seo_site
from config import SITE_URL, WEBP_CACHE_DIR


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
    assets.copy_static()
    print("Copying videos...")
    assets.copy_videos()
    print("Generating sitemap...")
    seo_site.generate_sitemap()
    print("\nValidating SEO...")
    seo_site.validate_seo()
    print("Compressing images and converting to WebP format...")
    assets.compress_and_convert_images()
    members.compress_member_images()
    print("Build complete!")
