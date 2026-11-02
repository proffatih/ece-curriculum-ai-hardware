import sys, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
from common_cl import txt
URL = 'https://catalog.ucsd.edu/courses/ECE.html'
t, ts = fetch('ucsd', URL, 'ucsd_ECE.html')
fetch('ucsd', 'https://catalog.ucsd.edu/front/courses.html', 'ucsd_front_courses.html')
P = 'UC San Diego General Catalog 2026-27, "Courses, Curricula, and Programs of Instruction": '
RULES = {'LD': P + '"Courses numbered 1 through 99 are lower-division courses"; listed under ECE "Lower Division" heading.',
         'UD': P + '"Courses numbered 100 through 199 are upper-division courses"; listed under ECE "Upper Division" heading.',
         'GR': P + '"Courses numbered 200 through 299 are graduate courses"; listed under ECE "Graduate" heading.'}
# tokenise in document order
toks = re.findall(r'<h2 class="course-subhead-1">(.*?)</h2>|<p class="course-name">(.*?)</p>|<(?:p|span) class="course-descriptions">(.*?)</(?:p|span)>', t, re.S)
rows = []; sect = None; cur = None; bad = []
for h, name, desc in toks:
    if h:
        sect = txt(h); continue
    if name:
        nm = txt(name)
        m = re.match(r'(ECE\s+[\w\-–/, ]+?)\.\s+(.*?)\s*\(([^()]*)\)\s*$', nm)
        if not m:
            m2 = re.match(r'(ECE\s+[\w\-–/, ]+?)\.\s+(.*)$', nm)
            if not m2: bad.append(nm); cur = None; continue
            code, title, cr = m2.group(1), m2.group(2), ''
        else:
            code, title, cr = m.groups()
        n = int(re.search(r'\d+', code).group(0))
        sec = {'Lower Division': 'LD', 'Upper Division': 'UD', 'Graduate': 'GR'}[sect]
        exp = 'LD' if n < 100 else ('UD' if n < 200 else 'GR')
        if sec != exp: print('SECTION MISMATCH', code, sect)
        cur = dict(university='UC San Diego', code=code, title=title, description='', level='G' if sec == 'GR' else 'UG',
                   level_rule=RULES[sec], credits=(cr + ' quarter units') if cr else '', source_url=URL, retrieved_utc=ts)
        rows.append(cur); continue
    if desc and cur is not None:
        cur['description'] = (cur['description'] + ' ' + txt(desc)).strip()
print('unparsed names:', bad)
out = write_rows('ucsd', rows)
print([ (r['code'],r['title'],r['credits']) for r in out if not re.fullmatch(r'ECE \d+[A-Z]*', r['code']) or not r['credits']])
