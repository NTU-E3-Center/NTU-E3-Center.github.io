import os
import json
import markdown
from jinja2 import Environment, FileSystemLoader

# ── Sync content from Excel before building ───────────────────────────────────
from lib.excel_to_content import build_member_data
from lib import seo_helpers
from config import OUTPUT_DIR
_member_data = build_member_data()
# ─────────────────────────────────────────────────────────────────────────────

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(['templates']),
                  trim_blocks=True,
                  lstrip_blocks=True)

# Register SEO helpers as Jinja globals so all templates can call them
env.globals['seo_meta_description'] = seo_helpers.generate_meta_description
env.globals['seo_strip_markdown'] = seo_helpers.strip_markdown
env.globals['seo_detect_language'] = seo_helpers.detect_language

# Load page structure from an external JSON file
with open("contents/pages.json", "r") as f:
    pages = json.load(f)

# Output directory
output_dir = OUTPUT_DIR

# Load JSON for each subpage from its dedicated folder. Each entry is
# (key_in_structures, path).
structures = {}
_SUBPAGE_JSON_SOURCES = [
    ('publications', 'contents/publications/publications.json'),
    ('news',         'contents/news/news.json'),
    ('research',     'contents/research/research.json'),
    ('group-life',   'contents/group-life/group-life.json'),
    ('about',        'contents/about/about.json'),
    ('contact',      'contents/contact/contact.json'),
    ('videos',       'contents/videos/videos.json'),
    ('projects',     'contents/projects/projects.json'),
]
for _key, _path in _SUBPAGE_JSON_SOURCES:
    with open(_path, 'r', encoding='utf-8') as _f:
        structures[_key] = json.load(_f)

# Use the in-memory members data returned by build_member_data() instead of
# re-reading the gitignored on-disk artifacts. The listing replaces the
# members.json the glob just loaded; members_by_id replaces the
# contents/structures/members/{webId}.json reads.
# Center members (PI + staff) vs. Prof. Hsieh's research-group students
# (Ph.D., Master, Alumni) — split once here so every template and JSON-LD
# block consumes the right roster without per-template filtering.
# Spec: specs/2026-08-05-students-split-design.md
_CENTER_SECTIONS = ('Principal Investigator', 'Staff')
structures['members'] = [
    g for g in _member_data['members_listing']
    if g['sectionTitle'] in _CENTER_SECTIONS]
structures['students'] = [
    g for g in _member_data['members_listing']
    if g['sectionTitle'] not in _CENTER_SECTIONS]
members_by_id = _member_data['members_by_id']
structures['members_by_id'] = members_by_id

# Load page-body markdown for each subpage that has one.
articles = {}
_PAGE_BODY_MD = [
    ('about',   'contents/about/about.md'),
    ('contact', 'contents/contact/contact.md'),
]
for _key, _md_path in _PAGE_BODY_MD:
    with open(_md_path, 'r', encoding='utf-8') as _f:
        _md = _f.read()
    articles[_key] = markdown.markdown(_md, extensions=['md_in_html'])
# News article markdown (keyed as 'news/<slug>' — render_news_pages reads
# articles[f'news/{slug}']).
_news_articles_dir = 'contents/news/articles'
if os.path.isdir(_news_articles_dir):
    for _fname in os.listdir(_news_articles_dir):
        if _fname.endswith('.md'):
            _slug = _fname[:-3]
            with open(os.path.join(_news_articles_dir, _fname), 'r', encoding='utf-8') as _f:
                _md = _f.read()
            articles[f'news/{_slug}'] = markdown.markdown(_md, extensions=['md_in_html'])

# Inject the in-memory member markdown (replaces what previously came from the
# disk artifacts under contents/articles/members-{about,position,interest}/).
# The members listing template reads `articles['members-position/<webId>']`.
for _wid, _mds in _member_data['members_md'].items():
    if _mds.get('about'):
        articles[f'members-about/{_wid}'] = _mds['about']
    if _mds.get('position'):
        articles[f'members-position/{_wid}'] = _mds['position']
    if _mds.get('interest'):
        articles[f'members-interest/{_wid}'] = _mds['interest']
