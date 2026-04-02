"""
create_member_excel.py
Generates a clean, consolidated member Excel from members.json + markdown files.
- Suggests WebIDs for all members
- One row per person (no duplicates)
- 'Also in Alumni' + 'Alumni Admission Year' columns for members active in both sections
Run: python3 create_member_excel.py
Output: contents/member-info-v2.xlsx
"""

import json, os, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ── helpers ───────────────────────────────────────────────────────────────────

def read_md(path):
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ''

def load_json(path):
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def img_to_id(img_path):
    """Extract base filename from imgPath, e.g. '/assets/members/bettyyu.jpg' -> 'bettyyu'"""
    if not img_path:
        return ''
    base = os.path.basename(img_path)
    return os.path.splitext(base)[0]

def is_student_id(s):
    """Returns True if the string looks like a student ID (r12521603, d13..., f12..., b11...)"""
    if not s:
        return False
    return (len(s) > 4 and s[0] in ('r', 'f', 'd', 'b') and s[1:3].isdigit()) or s[:2].isdigit()

# ── WebID suggestions keyed by student ID (ASCII, no encoding issues) ─────────
WEBID_BY_STUDENT_ID = {
    # Full Time / RA
    'r10521602': 'jimtseng',
    'r10521612': 'jasontam',
    'r11521602': 'seanshei',
    'r12521626': 'jianhern',
    # PhD
    'd13521023': 'garyding',
    'f12521611': 'harperlu',
    'f13521601': 'raylin',
    # MS2
    'r11521615': 'anchingchung',
    'r13521618': 'sonyayu',
    'r13521612': 'dulcineawu',
    'r13524093': 'derekchou',
    # MS1
    'r14h46003': 'yifangchang',
    'r14521603': 'leoli',
    'r14524050': 'clairekeng',
    'r14521615': 'shaoyangchuang',
    'r14521604': 'ericchen',
    'r14524113': 'yutinghuang',
    # MS DD / Exchange
    'r14521618': 'higashimasaki',
    'r13521623': 'yugoimoto',
    # Alumni only
    'r08521604': 'ayriacai',
    'r09521525': 'davidchang',
    'r10521604': 'alisonlo',
    'r10524030': 'seanchen',
    'r10521609': 'evanfeng',
    'r11524037': 'josephfu',
    'r11521605': 'jocelyntseng',
    'r11521604': 'thomaschien',
    'r12524052': 'ericchang',
    'r12524140': 'samuellee',
    'r12521605': 'sigihu',
    'r12521602': 'anitachen',
}

# Members appearing in BOTH an active section AND Alumni.
# Key = friendly img ID or student ID, value = admission year for the Alumni card
ALSO_ALUMNI_BY_ID = {
    'r10521602': "'21",   # Jim — was MS student '21, now Full Time
    'r10521612': "'21",   # Jason
    'r11521602': "'22",   # Sean
}

# ── load members.json ─────────────────────────────────────────────────────────

with open('contents/structures/members.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)

# ── collect unique members ────────────────────────────────────────────────────

seen  = {}   # file_id → row dict
order = []   # insertion order

for section in sections:
    section_title = section.get('sectionTitle', '')
    is_alumni     = section_title == 'Alumni'

    for member in section.get('members', []):
        chi        = member.get('chiName', '')
        eng        = member.get('engName', '')
        img        = member.get('imgPath', '')
        page_link  = member.get('pageLink', '')
        page_struct= member.get('pageStructure', '')
        admission  = member.get('admissionYear', '')

        # Derive a stable ID: prefer pageLink slug, then pageStructure filename, then imgPath
        file_id = ''
        if page_link:
            file_id = page_link.rstrip('/').split('/')[-1]
        elif page_struct:
            file_id = os.path.splitext(os.path.basename(page_struct))[0]
        if not file_id:
            file_id = img_to_id(img)

        if not file_id:
            file_id = chi  # last resort

        # Load detail JSON
        details      = load_json(page_struct) if page_struct else {}
        pub_name     = details.get('pubName', '')
        chi_name_eng = details.get('chiNameEng', '')
        graduated    = details.get('graduated', '')
        page_content = details.get('pageContent', {})

        # Email
        email = ''
        for lnk in page_content.get('links', []):
            if 'svg-send' in lnk.get('icon', ''):
                email = lnk.get('text', '')
                break

        # Markdown
        pos_section = page_content.get('positionSection', {})
        pos_md_path = pos_section.get('content', '') if isinstance(pos_section, dict) else ''
        position_md = read_md(pos_md_path)

        about_md = ''
        for sec in page_content.get('aboutSection', []):
            about_md = read_md(sec.get('content', ''))
            break

        # Interest markdown — try both the file_id and the student id in the path
        interest_md = read_md(f'contents/articles/members-interest/{file_id}.md')

        # Determine WebID
        img_id = img_to_id(img)
        if not is_student_id(file_id):
            webid = file_id                         # already a friendly ID
        elif file_id in WEBID_BY_STUDENT_ID:
            webid = WEBID_BY_STUDENT_ID[file_id]    # we have a suggestion
        elif not is_student_id(img_id):
            webid = img_id                          # img filename is friendly
        else:
            webid = f'(suggest: {file_id})'         # fallback — edit manually

        # Also-in-alumni check
        also_alumni     = file_id in ALSO_ALUMNI_BY_ID or img_id in ALSO_ALUMNI_BY_ID
        alumni_adm_year = ALSO_ALUMNI_BY_ID.get(file_id, ALSO_ALUMNI_BY_ID.get(img_id, ''))

        if file_id in seen:
            # Already added from active section; capture alumni admission year if needed
            if is_alumni and also_alumni:
                seen[file_id]['Alumni Admission Year'] = admission
            continue

        row = {
            'WebID':                 webid,
            'Nickname':              eng,
            'Chinese Name':          chi,
            'Full Name':             chi_name_eng,
            'pub Name':              pub_name,
            'Email':                 email,
            'Website Section':       section_title,
            'Admission Year':        admission,
            'Graduated':             str(graduated) if graduated != '' else '',
            'Also in Alumni':        'TRUE' if also_alumni else '',
            'Alumni Admission Year': alumni_adm_year if also_alumni else '',
            'About':                 about_md,
            'Position / Education':  position_md,
            'Research Interests':    interest_md,
            '_file_id':              file_id,   # internal, not written to Excel
        }
        seen[file_id] = row
        order.append(file_id)

rows = [seen[fid] for fid in order]

# ── build Excel ───────────────────────────────────────────────────────────────

HEADERS = [
    'WebID',
    'Nickname',
    'Chinese Name',
    'Full Name',
    'pub Name',
    'Email',
    'Website Section',
    'Admission Year',
    'Graduated',
    'Also in Alumni',
    'Alumni Admission Year',
    'About',
    'Position / Education',
    'Research Interests',
]

SECTION_COLORS = {
    'Principal Investigator': 'D6E4F7',
    'Full Time':              'D6F7E4',
    'Ph.D. Students':         'FFF3CC',
    'Master Students':        'FCE4D6',
    'Alumni':                 'EDEDED',
}

COL_WIDTHS = {
    'WebID': 20,
    'Nickname': 14,
    'Chinese Name': 14,
    'Full Name': 26,
    'pub Name': 20,
    'Email': 28,
    'Website Section': 20,
    'Admission Year': 14,
    'Graduated': 10,
    'Also in Alumni': 14,
    'Alumni Admission Year': 20,
    'About': 55,
    'Position / Education': 55,
    'Research Interests': 45,
}

thin   = Side(style='thin', color='CCCCCC')
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap   = Alignment(wrap_text=True, vertical='top')

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Members'

# Header row
for col, h in enumerate(HEADERS, 1):
    c = ws.cell(row=1, column=col, value=h)
    c.fill      = PatternFill('solid', fgColor='2F5496')
    c.font      = Font(bold=True, color='FFFFFF', size=11)
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border    = border
ws.row_dimensions[1].height = 22

# Track section boundaries for divider rows
section_groups = []
prev_sec = None
group_start = 2
for ri, data in enumerate(rows, 2):
    sec = data.get('Website Section', '')
    if prev_sec and sec != prev_sec:
        section_groups.append(group_start)
    prev_sec = sec
    group_start = ri + 1

# Data rows
excel_row = 2
for data in rows:
    section   = data.get('Website Section', '')
    fill      = PatternFill('solid', fgColor=SECTION_COLORS.get(section, 'FFFFFF'))

    for col, key in enumerate(HEADERS, 1):
        val = data.get(key, '')
        c = ws.cell(row=excel_row, column=col, value=val)
        c.fill      = fill
        c.alignment = wrap
        c.border    = border

        if key == 'WebID' and isinstance(val, str) and val.startswith('(suggest:'):
            c.font = Font(color='C55A11', italic=True, bold=True)
        elif key == 'Also in Alumni' and val == 'TRUE':
            c.font = Font(bold=True, color='375623')

    has_content = any(data.get(k) for k in ('About', 'Position / Education', 'Research Interests'))
    ws.row_dimensions[excel_row].height = 80 if has_content else 18

    excel_row += 1

    # Insert thin divider row when section changes
    if excel_row - 1 in section_groups:
        for col in range(1, len(HEADERS) + 1):
            c = ws.cell(row=excel_row, column=col)
            c.fill = PatternFill('solid', fgColor='AAAAAA')
        ws.row_dimensions[excel_row].height = 4
        excel_row += 1

# Column widths
for col, key in enumerate(HEADERS, 1):
    ws.column_dimensions[get_column_letter(col)].width = COL_WIDTHS.get(key, 15)

ws.freeze_panes = 'A2'

# ── save ──────────────────────────────────────────────────────────────────────

out = 'contents/member-info-v2.xlsx'
wb.save(out)

print(f"Saved {len(rows)} members → {out}")
print()
print("WebID suggestions (orange in Excel — confirm/edit before use):")
for row in rows:
    wid = row['WebID']
    if isinstance(wid, str) and wid.startswith('(suggest:'):
        print(f"  {row['Chinese Name']} ({row['Nickname']}) → {wid}")

print()
print("Members flagged 'Also in Alumni':")
for row in rows:
    if row['Also in Alumni'] == 'TRUE':
        print(f"  {row['Chinese Name']} ({row['Nickname']}) webID={row['WebID']}  alumni-year={row['Alumni Admission Year']}")
