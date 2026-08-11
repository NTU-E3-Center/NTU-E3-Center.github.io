import os
import json
import markdown
from datetime import datetime

from lib.site import env, output_dir, pages, structures, members_by_id
from lib.slugs import slugify_title


def proj_slug(item):
    """Suggest a project slug `<startYear>-<title-slug>` (parallel to pub_slug).

    The opt-in trigger is the explicit `slug` field in projects.json; this helper
    only generates a candidate value to paste in. An explicit `slug` always wins."""
    if item.get('slug'):
        return item['slug']
    year = (item.get('startDate') or '')[:4] or 'na'
    return f"{year}-{slugify_title(item.get('titleEn', ''))}".strip('-')


# A project earns a detail page once its listing entry has a non-empty `slug`
# AND a matching contents/projects/<slug>/project.json exists (opt-in, mirroring
# publications-by-abstract). Annotate those entries with a pageLink so the
# listing + homepage rows link to /projects/<slug>/.
#
# Bucket the distinct funder strings down to 5 readable categories driven by
# the /projects filter bar — fine-grained enough to be useful, coarse enough to
# scan. An entry can pin its category with an explicit `funderBucket` field in
# projects.json; the string heuristic only runs when no override is present.
# Active-year ranges (the years each project spans) are pre-computed here
# too so the template doesn't recompute on every row.
def _funder_bucket(item):
    """Return one of: NSTC, Gov, NTU, Foundation, Industry.

    Categories follow the funder, not the collaboration mode: bilateral
    NSTC programs (NSTC-ICSSR, NSTC-NWO) stay in NSTC and the TUKUC entry
    folds into Gov under the Ministry of Education. Taipei City Public
    Transportation Office reads as a municipal/government counterpart and
    lands in Gov rather than Industry. Foundation covers 財團法人 sponsors
    that are not companies (MIRDC, Wego private school)."""
    if item.get('funderBucket'):
        return item['funderBucket']
    fz = item.get('fundingAgency') or ''
    fe = item.get('fundingAgencyEn') or ''
    if item.get('grantNumber'):
        return 'NSTC'
    if fz.startswith('國科會') or 'National Science and Technology Council' in fe:
        return 'NSTC'
    if fz.startswith('環境部') or fz.startswith('教育部') \
            or fz.startswith('臺北市') or 'Ministry of' in fe \
            or 'Taipei City' in fe:
        return 'Gov'
    if fz.startswith('國立臺灣大學') or 'National Taiwan University' in fe \
            or fe.startswith('NTU '):
        return 'NTU'
    if fz.startswith('財團法人'):
        return 'Foundation'
    return 'Industry'


def prepare():
    """Module-level projects preprocessing moved verbatim from build.py.
    Mutates the shared structures dict in place."""
    if 'projects' in structures:
        for _section in structures['projects']:
            for _item in _section.get('items', []):
                _pslug = _item.get('slug')
                if _pslug and os.path.isfile(
                        os.path.join('contents', 'projects', _pslug, 'project.json')):
                    _item['pageLink'] = f"/projects/{_pslug}/"
                _item['funderBucket'] = _funder_bucket(_item)
                _start_yr = (_item.get('startDate') or '')[:4]
                _end_yr   = (_item.get('endDate')   or '')[:4]
                if _start_yr and _end_yr and _start_yr.isdigit() and _end_yr.isdigit():
                    _item['activeYears'] = [str(y) for y in
                                            range(int(_start_yr), int(_end_yr) + 1)]
                elif _start_yr:
                    _item['activeYears'] = [_start_yr]
                else:
                    _item['activeYears'] = []


# Function to render individual project detail pages from projects.json + the
# per-slug folder under contents/projects/<slug>/. A page is generated for every
# listing entry whose `slug` is set AND whose folder has a project.json (detail
# pages are opt-in). Core metadata comes from the listing entry; rich fields come
# from project.json; narrative from about.md / about.zh.md. relatedPublications
# resolve by citationId, team by webId.
def render_project_pages():
    template = env.get_template('pages/projects/project-item.html')

    # Publication lookup by citationId (published only) — mirrors render_member_pages.
    pub_by_id = {}
    for section in structures.get('publications', []):
        for item in section.get('items', []):
            if item.get('citationId') and item.get('status') == 'published':
                pub_by_id[item['citationId']] = item

    count = 0
    for section in structures.get('projects', []):
        for item in section.get('items', []):
            slug = item.get('slug')
            if not slug:
                continue
            folder = os.path.join('contents', 'projects', slug)
            detail_path = os.path.join(folder, 'project.json')
            if not os.path.isfile(detail_path):
                continue

            try:
                with open(detail_path, 'r', encoding='utf-8') as f:
                    detail = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                # A malformed detail file is treated like a missing one: skip
                # this project's page with a loud, located warning rather than
                # crashing the entire build on a single content typo.
                print(f"  ⚠ Skipping project '{slug}': cannot read {detail_path} ({e})")
                continue

            proj = dict(item)
            proj.update(detail)
            proj['slug'] = slug
            proj['pageLink'] = item.get('pageLink') or f"/projects/{slug}/"

            # Narrative bodies (EN + optional ZH) → HTML
            proj['narrativeHtml'] = ''
            proj['narrativeZhHtml'] = ''
            about_en = os.path.join(folder, 'about.md')
            about_zh = os.path.join(folder, 'about.zh.md')
            if os.path.isfile(about_en):
                with open(about_en, 'r', encoding='utf-8') as f:
                    proj['narrativeHtml'] = markdown.markdown(f.read(), extensions=['md_in_html'])
            if os.path.isfile(about_zh):
                with open(about_zh, 'r', encoding='utf-8') as f:
                    proj['narrativeZhHtml'] = markdown.markdown(f.read(), extensions=['md_in_html'])

            # Resolve related publications by citationId (skip unknown/unpublished).
            resolved_pubs = []
            for ref in detail.get('relatedPublications', []):
                cid = ref.get('citationId')
                if cid and cid in pub_by_id:
                    resolved_pubs.append(pub_by_id[cid])
            proj['relatedPubsResolved'] = resolved_pubs

            # Resolve team → link to member pages where webId matches a member.
            resolved_team = []
            for person in detail.get('team', []):
                wid = person.get('webId')
                resolved_team.append({
                    'name': person.get('name', ''),
                    'role': person.get('role', ''),
                    'pageLink': f"/members/{wid}/" if (wid and wid in members_by_id) else '',
                })
            proj['teamResolved'] = resolved_team

            # Gallery: keep only entries whose source file exists; build asset stem.
            resolved_gallery = []
            img_folder = os.path.join(folder, 'images')
            for shot in detail.get('gallery', []):
                fname = shot.get('file')
                if fname and os.path.isfile(os.path.join(img_folder, fname)):
                    stem = os.path.splitext(fname)[0]
                    resolved_gallery.append({
                        'stem': f"/assets/projects/{slug}/images/{stem}",
                        'caption': shot.get('caption', ''),
                        'captionZh': shot.get('captionZh', ''),
                    })
            proj['galleryResolved'] = resolved_gallery

            output = template.render(
                proj=proj,
                pages=pages,
                structures=structures,
                year=datetime.now().year,
            )

            page_dir = os.path.join(output_dir, proj['pageLink'].lstrip('/'))
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(output)
            count += 1
            print(f"Project page generated: {proj['pageLink']}")

    print(f"Project detail pages rendered successfully! ({count})")
