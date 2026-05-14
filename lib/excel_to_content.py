#!/usr/bin/env python3
"""
excel_to_content.py

Merges the admin roster (contents/member-info.xlsx — 11 admin columns) with
the per-member content folders (contents/members/{webId}/) and regenerates
the build's intermediate member files:
  - contents/structures/members.json                  (section-grouped listing)
  - contents/structures/members/{webId}.json          (per-member page data)
  - contents/articles/members-about/{webId}.md
  - contents/articles/members-position/{webId}.md
  - contents/articles/members-interest/{webId}.md

SOURCE OF TRUTH:
  - admin fields  → contents/member-info.xlsx
  - content fields → contents/members/{webId}/member.json + about.md

The per-member JSON/MD files written under contents/structures/members/ and
contents/articles/members-*/ are TRANSIENT BUILD ARTIFACTS (gitignored) —
build.py consumes them unchanged, so templates need no changes.

WebID is the formula-derived key (lowercase, hyphens/spaces removed from
Full Name). It is used for filenames, page URLs, image paths, and as the
join key to the per-member content folder.

Run: conda run -n E3website python excel_to_content.py
"""

import json, os, re
from pathlib import Path
import openpyxl

from validate_member import validate_member_folder

SECTION_ORDER = ['Principal Investigator', 'Full Time', 'Ph.D. Students', 'Master Students', 'Alumni']

SECTION_META = {
    'Principal Investigator': {'form': 'L'},
    'Full Time':              {'form': 'M'},
    'Ph.D. Students':         {'form': 'M'},
    'Master Students':        {'form': 'M'},
    'Alumni': {
        'form': 'S',
        'filter': True,
        'filterId': 'lum',
        'filterTitle': 'Filter by Admission Year:',
        'filterDefaultCheck': 5,
    },
}

PI_DESCRIPTION = (
    'Associate Professor<br>'
    'Department of Civil Engineering<br>'
    'Department of Chemical Engineering (Joint Appointment)<br>'
    'National Taiwan University'
)

MEMBERS_CONTENT_ROOT = 'contents/members'


def normalize_orcid(value):
    """Accept either a bare ORCID iD (0000-0002-XXXX-XXXX) or a full URL.
    Returns (display_text, full_url) or (None, None) if empty."""
    if not value:
        return None, None
    s = str(value).strip()
    if not s:
        return None, None
    if '://' in s:
        # Full URL — extract the iD for display
        oid = s.rstrip('/').rsplit('/', 1)[-1]
        return oid, s
    return s, f'https://orcid.org/{s}'


def build_profile_links_from_dict(links: dict):
    """Given a member.json `links` dict, return (visible_links, seo_links).

    Visible (rendered as chips): Google Scholar, ORCID, LinkedIn.
    SEO-only (sameAs, not rendered): ResearchGate, NTU Scholars, Facebook.
    The `office` key is handled separately by the caller."""
    visible = []
    seo = []

    gs = (links.get('scholar') or '').strip()
    if gs:
        visible.append({
            'icon': '/assets/sprite.svg#svg-scholar',
            'text': 'Google Scholar',
            'link': gs,
        })

    orcid_text, orcid_url = normalize_orcid(links.get('orcid'))
    if orcid_url:
        visible.append({
            'icon': '/assets/sprite.svg#svg-orcid',
            'text': orcid_text,
            'link': orcid_url,
        })

    li = (links.get('linkedin') or '').strip()
    if li:
        visible.append({
            'icon': '/assets/sprite.svg#svg-linkedin',
            'text': 'LinkedIn',
            'link': li,
        })

    for key in ('researchgate', 'ntu_scholars', 'facebook'):
        url = (links.get(key) or '').strip()
        if url:
            seo.append(url)

    return visible, seo


# ── helpers ───────────────────────────────────────────────────────────────────

def display_name(full_name: str, nickname: str) -> str:
    """Return 'Full Name (Nickname)' if nickname adds info not already in the
    full name, otherwise return 'Full Name' as-is.

    Logic: normalise both to lowercase letters only, then skip the bracket if
    either string starts with the other (covers cases like nickname='Jianhern'
    vs full='Jian Hern Yeoh', or nickname='I-Yun Lisa Hsieh, PhD' vs full='I-Yun Lisa Hsieh').
    """
    if not nickname or not full_name:
        return full_name or nickname
    fn = re.sub(r'[^a-z]', '', full_name.lower())
    nk = re.sub(r'[^a-z]', '', nickname.lower())
    # Also skip bracket if the nickname (≥3 chars) appears anywhere inside the full name
    if fn.startswith(nk) or nk.startswith(fn) or (len(nk) >= 3 and nk in fn):
        return full_name
    return f'{full_name} ({nickname})'


def find_image(web_id: str) -> str:
    """Return /assets/… path for a member's image, or nobody.svg.

    Reads the per-member content folder: contents/members/{webId}/photo.{ext}.
    The output path keeps the {webId}.{ext} naming so docs/assets/members/
    references stay identical to the legacy pipeline."""
    folder = os.path.join(MEMBERS_CONTENT_ROOT, web_id)
    if os.path.isdir(folder):
        for fname in sorted(os.listdir(folder)):
            stem, ext = os.path.splitext(fname)
            if stem == 'photo' and ext.lower() in ('.jpg', '.jpeg', '.png') and not fname.startswith('.'):
                return f'/assets/members/{web_id}{ext.lower()}'
    return '/assets/members/nobody.svg'


def get_icon(current_position: str, batch: str) -> str:
    pos = (current_position or '').strip()
    b   = (batch or '').strip()
    if pos == 'RA':
        return '/assets/sprite.svg#svg-assistant'
    if pos.startswith('PHD'):
        return '/assets/sprite.svg#svg-doctor-2' if b.startswith('D') else '/assets/sprite.svg#svg-doctor-1'
    if pos == 'MS 2':
        return '/assets/sprite.svg#svg-master-2'
    if pos in ('MS 1', 'MS 0', 'MS DD'):
        return '/assets/sprite.svg#svg-master-1'
    return '/assets/sprite.svg#svg-master-2'  # Grad / Alumni fallback


def adm_year_sort_key(entry: dict) -> int:
    y = entry.get('admissionYear', '')
    m = re.search(r'\d+', str(y))
    return int(m.group()) if m else 0


def write_text(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# ── per-member content folder loader ──────────────────────────────────────────

_EMPTY_CONTENT = {
    'position': '',
    'email': {'ntu': '', 'preferred': ''},
    'interests': [],
    'links': {
        'scholar': '', 'orcid': '', 'linkedin': '',
        'researchgate': '', 'ntu_scholars': '', 'facebook': '',
        'office': {'text': '', 'url': ''},
    },
    'metaDescription': '',
}


def load_member_content(web_id: str):
    """Read contents/members/{webId}/member.json + about.md.

    Returns (content_dict, about_text). content_dict always has every key
    present (folder values merged over _EMPTY_CONTENT defaults).

    Validates the folder first: build FAILS (SystemExit 2) on any error-level
    issue (invalid JSON, schema mismatch); warn-level issues are printed but
    the build proceeds with defaults."""
    folder = os.path.join(MEMBERS_CONTENT_ROOT, web_id)

    issues = validate_member_folder(web_id, Path(folder))
    errors = [i for i in issues if i.severity == 'error']
    if errors:
        for e in errors:
            print(f'  ✗ {e.message}')
        raise SystemExit(2)
    for i in issues:
        if i.severity == 'warn':
            print(f'  ⚠ {i.message}')

    # Deep-copy defaults so each member gets a fresh dict.
    content = json.loads(json.dumps(_EMPTY_CONTENT))

    member_json = os.path.join(folder, 'member.json')
    if os.path.exists(member_json):
        with open(member_json, encoding='utf-8') as f:
            loaded = json.load(f)
        # Shallow-merge top level, then patch nested dicts so a member.json
        # that omits a nested key still ends up fully-formed.
        for key, val in loaded.items():
            if key in ('email', 'links') and isinstance(val, dict):
                content[key].update(val)
                if key == 'links' and isinstance(val.get('office'), dict):
                    content['links']['office'].update(val['office'])
            else:
                content[key] = val

    about_text = ''
    about_md = os.path.join(folder, 'about.md')
    if os.path.exists(about_md):
        with open(about_md, encoding='utf-8') as f:
            about_text = f.read().strip()

    return content, about_text


# ── read Excel (data_only to resolve WebID formula values) ───────────────────

wb = openpyxl.load_workbook('contents/member-info.xlsx', data_only=True)
ws = wb['Members']
headers = [c.value for c in ws[1]]


def col(row, name):
    """Read an admin column by name. Raises if the column is absent — the
    slim Excel must have all 11 admin columns."""
    idx = headers.index(name)
    val = row[idx]
    return val if val is not None else ''


# ── process rows ──────────────────────────────────────────────────────────────

members_by_section = {s: [] for s in SECTION_ORDER}
extra_alumni = []

json_written = []
md_written   = []

for row in ws.iter_rows(min_row=2, values_only=True):
    web_id = row[headers.index('WebID')]
    if not web_id:
        continue  # blank / divider row

    web_id    = str(web_id).strip()
    nickname  = str(col(row, 'Nickname')             or '').strip()
    chi_name  = str(col(row, 'Chinese Name')         or '').strip()
    full_name = str(col(row, 'Full Name')            or '').strip()
    section   = str(col(row, 'Website Section')      or '').strip()
    adm_year  = col(row, 'Admission Year')
    graduated = str(col(row, 'Graduated')            or '').strip()
    also_alumni = str(col(row, 'Also in Alumni')     or '').strip().upper() == 'TRUE'
    alumni_year = col(row, 'Alumni Admission Year')
    curr_pos  = str(col(row, 'Current Position')     or '').strip()
    batch     = str(col(row, 'Batch')                or '').strip()

    # Content fields come from contents/members/{webId}/ (not Excel).
    content, about = load_member_content(web_id)
    position  = str(content['position'] or '').strip()
    interests = list(content.get('interests') or [])
    email     = str(content['email']['preferred'] or '').strip()
    ntu_email = str(content['email']['ntu'] or '').strip()
    meta_description = (str(content.get('metaDescription') or '').strip()) or None

    has_page      = bool(about or position)
    display_email = email or ntu_email
    img_path      = find_image(web_id)
    icon          = get_icon(curr_pos, batch)
    is_pi         = (section == 'Principal Investigator')

    # ── per-member JSON ───────────────────────────────────────────────────────
    if has_page:
        if section == 'Principal Investigator':
            position_for_seo = 'Director of E3 Center, NTU'
        else:
            position_for_seo = position or None

        member_json = {
            'chiNameEng':      display_name(full_name, nickname),
            'pubName':         full_name,   # plain Full Name for publication matching
            'metaDescription': meta_description,
            'position':        position_for_seo,
        }
        if not is_pi:
            member_json['graduated'] = (graduated.lower() == 'true')

        links = []
        if display_email:
            links.append({
                'icon': '/assets/sprite.svg#svg-send',
                'text': display_email,
                'link': f'mailto:{display_email}',
            })

        # Office link (previously hardcoded as PI_EXTRA_LINKS; now sourced
        # from member.json links.office — populated for the PI by the
        # migration, empty for everyone else).
        office = content['links'].get('office') or {}
        office_text = str(office.get('text') or '').strip()
        office_url  = str(office.get('url') or '').strip()
        if office_text or office_url:
            office_link = {
                'icon': '/assets/sprite.svg#svg-location',
                'text': office_text,
            }
            if office_url:
                office_link['link'] = office_url
            links.append(office_link)

        # Per-member profile links (Scholar, ORCID, LinkedIn = visible;
        # ResearchGate, NTU Scholars, Facebook = hidden / sameAs only)
        profile_visible, profile_seo = build_profile_links_from_dict(content['links'])
        links.extend(profile_visible)

        page_content = {'links': links}
        if profile_seo:
            page_content['seoLinks'] = profile_seo
        if position:
            page_content['positionSection'] = {
                'content': f'contents/articles/members-position/{web_id}.md'
            }
        if about:
            page_content['aboutSection'] = [
                {'sectionTitle': 'About',
                 'content': f'contents/articles/members-about/{web_id}.md'}
            ]
        if is_pi:
            page_content['PublicationSection'] = [
                {'sectionTitle': 'Journal Publications', 'publications': []}
            ]
        member_json['pageContent'] = page_content

        json_path = f'contents/structures/members/{web_id}.json'
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(member_json, f, ensure_ascii=False, indent=4)
        json_written.append(json_path)

        if about:
            p = f'contents/articles/members-about/{web_id}.md'
            write_text(p, about)
            md_written.append(p)
        if position:
            p = f'contents/articles/members-position/{web_id}.md'
            write_text(p, position)
            md_written.append(p)
        if interests:
            p = f'contents/articles/members-interest/{web_id}.md'
            write_text(p, '\n\n'.join(f'/{topic}' for topic in interests))
            md_written.append(p)

    # ── members.json entry ────────────────────────────────────────────────────
    if section not in members_by_section:
        print(f'  WARNING: unknown section "{section}" for {web_id}, skipping')
        continue

    if is_pi:
        entry = {
            'engName':     full_name,
            'chiName':     chi_name,
            'description': PI_DESCRIPTION,
            'imgPath':     img_path,
            'links':       [],
        }
        if display_email:
            entry['links'].append({
                'icon': '/assets/sprite.svg#svg-send',
                'text': display_email,
                'link': f'mailto:{display_email}',
            })
        # PI office link for the listing-card entry (mirrors the per-member
        # JSON office link built above).
        _pi_office = content['links'].get('office') or {}
        _pi_office_text = str(_pi_office.get('text') or '').strip()
        _pi_office_url  = str(_pi_office.get('url') or '').strip()
        if _pi_office_text or _pi_office_url:
            _entry_office = {
                'icon': '/assets/sprite.svg#svg-location',
                'text': _pi_office_text,
            }
            if _pi_office_url:
                _entry_office['link'] = _pi_office_url
            entry['links'].append(_entry_office)
        if has_page:
            entry['pageLink']      = f'/members/{web_id}'
            entry['pageStructure'] = f'contents/structures/members/{web_id}.json'
    else:
        entry = {
            'engName': nickname or full_name,
            'chiName': chi_name,
            'imgPath': img_path,
            'icon':    icon,
        }
        if adm_year:
            entry['admissionYear'] = str(adm_year)
        if has_page:
            entry['pageLink']      = f'/members/{web_id}'
            entry['pageStructure'] = f'contents/structures/members/{web_id}.json'

    members_by_section[section].append(entry)

    if also_alumni and section != 'Alumni':
        alumni_entry = {
            'engName': nickname or full_name,
            'chiName': chi_name,
            'imgPath': img_path,
            'icon':    '/assets/sprite.svg#svg-master-2',
        }
        if alumni_year:
            alumni_entry['admissionYear'] = str(alumni_year)
        if has_page:
            alumni_entry['pageLink']      = f'/members/{web_id}'
            alumni_entry['pageStructure'] = f'contents/structures/members/{web_id}.json'
        extra_alumni.append(alumni_entry)

members_by_section['Alumni'].extend(extra_alumni)
members_by_section['Alumni'].sort(key=adm_year_sort_key)

# ── write members.json ────────────────────────────────────────────────────────

output = []
for section_title in SECTION_ORDER:
    members_list = members_by_section[section_title]
    if not members_list:
        continue
    section_obj = {'sectionTitle': section_title}
    section_obj.update(SECTION_META[section_title])
    section_obj['members'] = members_list
    output.append(section_obj)

members_json_path = 'contents/structures/members.json'
with open(members_json_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

# ── summary ───────────────────────────────────────────────────────────────────

print(f'Written: {members_json_path}')
print(f'Written: {len(json_written)} member JSON files')
print(f'Written: {len(md_written)} markdown files')
print()
for s in SECTION_ORDER:
    print(f'  {s}: {len(members_by_section[s])} members')
