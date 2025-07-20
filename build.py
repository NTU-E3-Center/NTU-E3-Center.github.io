import os
import json
import shutil
import markdown
from PIL import Image
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(['templates', 'contents']),
                  trim_blocks=True,
                  lstrip_blocks=True)

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

articles_path = 'contents/articles'
articles = {}
for filename in os.listdir(articles_path):
    if filename.endswith('.md'):
        file_path = os.path.join(articles_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            # Load md content
            md_text = f.read()
            html_content = markdown.markdown(md_text, extensions=['md_in_html'])
        # Create a key based on the file name (without the .json extension)
        var_name = os.path.splitext(filename)[0]
        articles[var_name] = html_content

# Function to render templates into correct directories
def render_templates():
    def process_pages(pages, base_path=""):
        for template_name, page_data in pages.items():
            if isinstance(page_data, dict) and "path" in page_data:
                template = env.get_template(f"{template_name}.html")
                output = template.render(
                    title=page_data.get("title"),
                    updated_time=datetime.now().strftime("%Y. %m. %d"),
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


# Function to copy static assets directly into docs/
def copy_static():
    static_src = "static"
    if os.path.exists(static_src):
        for item in os.listdir(static_src):
            src_path = os.path.join(static_src, item)
            dst_path = os.path.join(output_dir, item)
            
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

    print("Static assets copied directly into docs/")


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
        print(f"--- Images found in '{folder}' ---")
        dst_path = f"docs/assets/{folder}"
        os.makedirs(dst_path, exist_ok=True)
        for path in paths:
            shutil.copy2(path, dst_path)
            convert_to_webp(path, dst_path, globals()[f'{folder}_img_sizes'], compression_quality=70)
            convert_to_webp(path, dst_path, lazy_img_sizes, compression_quality=10)
            print(f"{path} copied and converted to WebP")
        

# Run the build process
if __name__ == "__main__":
    print("Rendering templates...")
    render_templates()
    print("Copying static assets...")
    copy_static()
    print("Compressing images and converting to WebP format...")
    compress_and_convert_images()
    print("Build complete!")
