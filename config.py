"""Central build configuration — the single source of truth for values that
were previously hardcoded in many places across build.py and the templates.

Import from build.py (`from config import SITE_URL, OUTPUT_DIR, ...`). SITE_URL
is also injected into every Jinja render context as `base_url`, so templates
reference `{{ base_url }}` instead of hardcoding the domain.
"""

import os

# Canonical origin (no trailing slash). Used for canonical links, Open Graph
# URLs, JSON-LD, and the sitemap. The custom domain itself lives in
# static/CNAME (that file *is* the domain, by GitHub Pages design).
#
# Overridable per deploy environment. Cloudflare Pages sets SITE_URL on each
# project — https://e3center.net for production, https://beta.e3center.net for
# the internal review build — so canonicals, Open Graph URLs, JSON-LD and the
# sitemap all describe the host they are actually served from. The default is
# the domain live today, so local builds and the GitHub Pages workflow keep
# emitting what they always did until the migration completes.
SITE_URL = os.environ.get("SITE_URL", "https://e3center.caece.net").rstrip("/")

# "production" gates search indexing. Any other value (Cloudflare's beta
# project sets "preview") makes the build emit noindex on every page and a
# robots.txt that disallows everything — a public copy of the site competing
# with the real one in search results is worse than no copy at all.
DEPLOY_ENV = os.environ.get("DEPLOY_ENV", "production")
IS_PRODUCTION = DEPLOY_ENV == "production"

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
