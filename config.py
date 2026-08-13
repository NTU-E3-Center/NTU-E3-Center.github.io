"""Central build configuration — the single source of truth for values that
were previously hardcoded in many places across build.py and the templates.

Import from build.py (`from config import SITE_URL, OUTPUT_DIR, ...`). SITE_URL
is also injected into every Jinja render context as `base_url`, so templates
reference `{{ base_url }}` instead of hardcoding the domain.
"""

# Canonical origin (no trailing slash). Used for canonical links, Open Graph
# URLs, JSON-LD, and the sitemap. The custom domain itself lives in
# static/CNAME (that file *is* the domain, by GitHub Pages design).
SITE_URL = "https://e3center.caece.net"

# Compiled-site output directory (served by GitHub Pages). Gitignored.
OUTPUT_DIR = "docs"

# Responsive WebP widths emitted per image class. Templates build their srcset
# from the same ladders, so keep the two in sync when changing these.
SUBPAGE_IMG_WIDTHS = [200, 400, 600, 800, 1200, 1600, 2000]  # news / group-life / projects
MEMBER_IMG_WIDTHS = [200, 400, 600, 800]                     # member headshots (3:4)
# Homepage research-pillar photos (3:2). Capped at 1200: the frames render
# ~370 px wide in the three-column row, so 1200 covers 3x DPI, and the ladder
# stops below the source files' own width so no variant is ever upscaled.
RESEARCH_IMG_WIDTHS = [200, 400, 600, 800, 1200]
LAZY_IMG_WIDTHS = [20]                                       # blur-up placeholder

# WebP encode quality.
WEBP_QUALITY = 70        # real variants
WEBP_LAZY_QUALITY = 10   # 20w blur-up placeholder
