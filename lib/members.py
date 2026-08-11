import os
from datetime import datetime

from lib.site import env, output_dir, pages, structures, members_by_id, _member_data
from lib.publications import get_pub_sort_key
from lib.assets import convert_to_webp, members_img_sizes, lazy_img_sizes
from config import WEBP_QUALITY, WEBP_LAZY_QUALITY


# Function to render individual member pages from the in-memory members_by_id dict
def render_member_pages():
    if not members_by_id:
        print("No member data in memory, skipping member pages.")
        return

    # Build research lookup dict: researchId -> topic data
    research_by_id = {}
    for section in structures.get('research', []):
        for topic in section.get('topics', []):
            research_by_id[topic['researchId']] = topic

    # Build publication lookup dict: citationId -> publication data.
    # Require a non-empty citationId AND status == 'published' — working /
    # in-review entries (which often share an empty citationId) would otherwise
    # all collide on the same dict key and pollute member pages.
    pub_by_id = {}
    for section in structures.get('publications', []):
        for item in section.get('items', []):
            if item.get('citationId') and item.get('status') == 'published':
                pub_by_id[item['citationId']] = item

    template = env.get_template('pages/member/member.html')

    for group in structures.get('members', []) + structures.get('students', []):
        for member_base in group.get('members', []):
            page_link = member_base.get('pageLink', '')
            if not page_link:
                continue
            # webId is the last path segment of /members/{web_id}
            web_id = page_link.rstrip('/').rsplit('/', 1)[-1]
            if not web_id:
                continue

            member_details = members_by_id.get(web_id)
            if member_details is None:
                continue

            # Merge member details, using base data as defaults
            member = member_details.copy()
            member.update(member_base)

            if 'pageLink' not in member:
                continue

            # Place pre-rendered HTML directly onto pageContent so the template
            # can render it without a path-keyed lookup.
            md_for_member = _member_data['members_md'].get(web_id, {})
            page_content = member.get('pageContent', {})

            for section in page_content.get('aboutSection', []):
                section['content'] = md_for_member.get('about', '')
            if page_content.get('positionSection'):
                page_content['positionSection']['content'] = md_for_member.get('position', '')

            # Member interest (pre-rendered HTML from members_md)
            interest_html = md_for_member.get('interest', '')
            if interest_html:
                member['interest_content'] = interest_html

            # Auto-populate Journal Publications by matching authorList[].webId
            matching_items = []
            for pub_section in structures.get('publications', []):
                for item in pub_section.get('items', []):
                    author_web_ids = {a.get('webId') for a in item.get('authorList', []) if a.get('webId')}
                    if (item.get('citationId')
                            and item.get('status') == 'published'
                            and web_id in author_web_ids):
                        matching_items.append(item)

            # Sort by issue date, newest first, via the shared sort key. Routing
            # through get_pub_sort_key (instead of re-parsing year/month here)
            # keeps a single source of truth and normalizes the "'YY" string,
            # plain int, and missing-date forms to a uniform (int, int) tuple.
            # A raw (year, month) sort would raise TypeError the moment a str
            # year and an int-default year were compared.
            matching_items.sort(key=get_pub_sort_key, reverse=True)
            matching_citations = [item['citationId'] for item in matching_items]

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
                structures=structures,
                year=datetime.now().year,
            )

            page_dir = os.path.join(output_dir, member['pageLink'].lstrip('/'))
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Member page generated: {member['pageLink']}")

    print("Member pages rendered successfully!")


def compress_member_images():
    """Convert per-member photos to WebP variants.

    Source: contents/members/{webId}/photo.{jpg,jpeg,png}
    Output: docs/assets/members/{webId}-{size}w.webp

    The output keeps the {webId} basename so member templates' srcset
    references are byte-identical to the legacy contents/images/members/
    pipeline — only the SOURCE location moved into the per-member folder."""
    members_root = 'contents/members'
    dst_root = os.path.join(output_dir, "assets", "members")
    photo_exts = ('.jpg', '.jpeg', '.png')

    if not os.path.isdir(members_root):
        return
    os.makedirs(dst_root, exist_ok=True)
    print("--- Member photos in 'contents/members/*/' ---")

    for web_id in sorted(os.listdir(members_root)):
        member_dir = os.path.join(members_root, web_id)
        if not os.path.isdir(member_dir):
            continue
        photo = None
        for fname in sorted(os.listdir(member_dir)):
            stem, ext = os.path.splitext(fname)
            if stem == 'photo' and ext.lower() in photo_exts and not fname.startswith('.'):
                photo = os.path.join(member_dir, fname)
                break
        if not photo:
            continue
        convert_to_webp(photo, dst_root, members_img_sizes, compression_quality=WEBP_QUALITY, basename=web_id, target_aspect=(3, 4))
        convert_to_webp(photo, dst_root, lazy_img_sizes, compression_quality=WEBP_LAZY_QUALITY, basename=web_id, target_aspect=(3, 4))
        print(f"{photo} → {dst_root}/{web_id}-*.webp")
