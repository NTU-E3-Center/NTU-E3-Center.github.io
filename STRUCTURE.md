# Website Structure

This repository uses a static site generator script (`build.py`) to build the website. Below is an overview of the directory structure and the role of each component.

## Key Directories

### [contents/](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/contents/)
Contains all the source data and assets that are processed by the build script.
- `structures/`: JSON files defining the site structure, member profiles, research topics, and publications.
- `articles/`: Markdown files for news, research interests, and other textual content.
- `images/`: Source images for members and site content (automatically compressed and converted to WebP).
- `videos/`: Video assets copied to the output directory.

### [templates/](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/templates/)
HTML templates (using Jinja2 syntax) that define the layout and design of the website.
- `base.html`: The main layout file shared by all pages.
- `home/`, `member.html`, `news.html`: Specific templates for different page types.
- `partials/`: Reusable HTML fragments.

### [static/](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/static/)
A directory for static assets that are copied **directly** to the output directory without processing.
- Includes `css/`, `js/`, `assets/`, and the `editor/` tool.

### [docs/](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/docs/)
The deployment directory. This is where the generated static site is stored. **Do not edit files here directly**, as they will be overwritten during the next build. This directory is served by GitHub Pages.

### [website/](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/website/)
A local Python virtual environment directory used for development and running the build script. It is excluded from the build output.

### [.github/](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/.github/)
Contains GitHub Actions workflows, specifically `deploy.yml`, which automates the build and deployment to GitHub Pages when changes are pushed to the `source` branch.

## Build Process
The [build.py](file:///Users/jianhern/Desktop/Github/NTU-E3-Center.github.io/build.py) script orchestrates the following:
1.  **Renders HTML**: Combines JSON data from `contents/structures/` and Markdown from `contents/articles/` with Jinja2 templates in `templates/`.
2.  **Generates Pages**: Creates the folder structure in `docs/` and saves `index.html` files for SEO-friendly URLs.
3.  **Processes Images**: Compresses source images from `contents/images/` and generates WebP versions in multiple sizes for performance.
4.  **Copies Assets**: Moves files from `static/` and `contents/videos/` into the `docs/` directory.
    