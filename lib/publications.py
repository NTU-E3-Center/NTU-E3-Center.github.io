import os
import re
from datetime import datetime
from markupsafe import Markup, escape

from lib.site import env, output_dir, pages, structures, members_by_id
from lib.slugs import slugify_title


def bold_author(authors_str, name):
    """Wrap occurrences of `name` in an authors string with <strong>.
    Both inputs are HTML-escaped first; the search uses non-word/non-hyphen
    boundaries so "I-Yun Hsieh" does not match "I-Yun Hsieh-Chen". Also
    matches the collapsed-hyphen romanization variant ("Wan-Ting Hsu" ↔
    "Wanting Hsu") — papers print whichever form they like, and the bolded
    text keeps the paper's spelling. Returns Markup so the result is
    rendered as HTML, not as literal tags."""
    if not authors_str:
        return Markup('')
    escaped = str(escape(authors_str))
    if not name:
        return Markup(escaped)
    variants = {str(escape(name))}
    collapsed = re.sub(r'-(\w)', lambda m: m.group(1).lower(), name)
    variants.add(str(escape(collapsed)))
    alternation = '|'.join(re.escape(v) for v in sorted(variants, key=len, reverse=True))
    pattern = re.compile(r'(?<![\w\-])(?:' + alternation + r')(?![\w\-])')
    return Markup(pattern.sub(lambda m: f'<strong>{m.group(0)}</strong>', escaped))


env.filters['bold_author'] = bold_author

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


# ── Publication detail-page helpers: slug + derived BibTeX ────────────────────
# A publication earns a detail page once it has an `abstract`. Its URL slug and
# its BibTeX are derived from the structured fields so there is a single source
# of truth (no duplicated blob to drift). An explicit `slug` or `bibtex` field,
# if present, overrides the derived value.

_BIBTEX_STOPWORDS = {"a", "an", "the", "on", "of", "in", "for", "and", "to", "with"}
_MONTHS3 = {"jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"}


def pub_year4(item):
    """4-digit year string from a publication's `year` (handles the "'YY" form)."""
    y = str(item.get('year', '') or '')
    return ('20' + y[1:]) if y.startswith("'") else y


def pub_slug(item):
    """Explicit `slug` wins; otherwise derive `<year>-<title-slug>`."""
    if item.get('slug'):
        return item['slug']
    return f"{pub_year4(item) or 'na'}-{slugify_title(item.get('title', ''))}".strip('-')


def _bibtex_authors(item):
    """'Last, First and Last, First'. Prefers structured authorList; falls back
    to the comma-separated `authors` string."""
    if item.get('authorList'):
        names = [a.get('name', '') for a in item['authorList'] if a.get('name')]
    else:
        names = [n.strip() for n in (item.get('authors') or '').split(',') if n.strip()]
    out = []
    for n in names:
        parts = n.split()
        out.append(f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) >= 2 else n)
    return ' and '.join(out)


def _bibtex_key(item):
    """Scholar-style key: <firstAuthorLastname><year><firstSignificantTitleWord>."""
    if item.get('authorList') and item['authorList']:
        first = item['authorList'][0].get('name', '')
    else:
        first = (item.get('authors') or '').split(',')[0]
    parts = first.split()
    last = re.sub(r'[^a-z0-9]', '', parts[-1].lower()) if parts else 'anon'
    word = ''
    for w in re.sub(r'[^a-z0-9\s-]', '', item.get('title', '').lower()).split():
        if w not in _BIBTEX_STOPWORDS:
            word = w.split('-')[0]
            break
    return f"{last}{pub_year4(item)}{word}"


def generate_bibtex(item):
    """Assemble a BibTeX entry from structured fields. An explicit `bibtex` field
    overrides the derived output verbatim."""
    if item.get('bibtex'):
        return item['bibtex']
    fields = [
        ('title', item.get('title')),
        ('author', _bibtex_authors(item)),
        ('journal', (item.get('journal') or '').replace('&', r'\&')),
        ('volume', item.get('volume')),
        ('number', item.get('issue')),
        ('pages', item.get('articleNo') or item.get('pages')),
        ('year', pub_year4(item)),
        ('month', (item.get('month') or '').strip('.').lower()[:3]),
        ('doi', item.get('doi')),
    ]
    rendered = []
    for k, v in fields:
        if not v:
            continue
        if k == 'month':
            if v in _MONTHS3:           # bare macro, no braces (per house style)
                rendered.append(f"  month={v}")
        else:
            rendered.append(f"  {k}={{{v}}}")
    if not rendered:
        return ''
    return "@article{" + _bibtex_key(item) + ",\n" + ',\n'.join(rendered) + "\n}"


def prepare():
    """Module-level publications preprocessing moved verbatim from build.py.
    Mutates the shared structures dict in place."""
    # Filter and sort publications for home page
    if 'publications' in structures:
        home_publications = []
        for section in structures['publications']:
            new_section = section.copy()
            # Filter items with E3: true and published status (exclude submitted/under review and books)
            filtered_items = [
                item for item in section.get('items', [])
                if item.get('E3') is True
                and item.get('status', 'published') == 'published'
                and item.get('type') != 'book'
            ]
            # Sort items descending by date
            filtered_items.sort(key=get_pub_sort_key, reverse=True)
            new_section['items'] = filtered_items
            home_publications.append(new_section)
        structures['home_publications'] = home_publications

    # A publication earns a detail page once it has an `abstract`. Annotate those
    # with their slug + pageLink (derived if not set explicitly) so the listing
    # template links each such row to /publications/<slug>/. Mutates the shared
    # structures dict before any template renders. Publications without an abstract
    # are left untouched — they keep the original whole-row publisher link.
    if 'publications' in structures:
        for _section in structures['publications']:
            for _item in _section.get('items', []):
                if _item.get('abstract'):
                    _item['slug'] = pub_slug(_item)
                    _item['pageLink'] = f"/publications/{_item['slug']}/"


# Function to render individual publication detail pages from publications.json.
# A page is generated for every entry with an `abstract` (detail pages are
# opt-in). The slug and BibTeX are derived from the structured fields. Authors
# in `authorList` whose webId matches an E3 member are linked to that member's
# page by the template (member_ids gates the link).
def render_publication_pages():
    template = env.get_template('pages/publications/publication-item.html')
    member_ids = set(members_by_id.keys())

    count = 0
    for section in structures.get('publications', []):
        for item in section.get('items', []):
            if not item.get('abstract'):
                continue

            pub = dict(item)
            slug = pub.get('slug') or pub_slug(pub)
            pub['slug'] = slug
            pub['pageLink'] = pub.get('pageLink') or f"/publications/{slug}/"
            # BibTeX is derived from the structured fields (single source of
            # truth); an explicit `bibtex` field, if present, overrides it.
            pub['bibtex'] = generate_bibtex(pub)

            output = template.render(
                pub=pub,
                member_ids=member_ids,
                pages=pages,
                structures=structures,
                year=datetime.now().year,
            )

            page_dir = os.path.join(output_dir, pub['pageLink'].lstrip('/'))
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(output)
            count += 1
            print(f"Publication page generated: {pub['pageLink']}")

    print(f"Publication detail pages rendered successfully! ({count})")
