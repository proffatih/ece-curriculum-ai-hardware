import sys, re, os, datetime, collections
sys.path.insert(0, 'raw/_scripts')
from catv2 import write_rows, RAW
from common_cl import txt
URL = 'https://courses.cornell.edu/courses/ece/'
POL = 'https://courses.cornell.edu/general-information/course-numbering/'
D = os.path.join(RAW, 'cornell')
# headless-chrome dumps (plain HTTP GET returns 202 empty bot-check); timestamps from _fetch_log.tsv
log = {l.split('\t')[2]: l.split('\t')[0] for l in open(os.path.join(D, '_fetch_log.tsv')) if l.strip()}
ts = log[URL]
t = open(os.path.join(D, 'cornell_courses_ece_headless.html')).read()
P = 'Cornell University 2026-2027 Catalog, Course Numbering System: '
RULES = {'UG': P + '"1100 level undergraduate course: introductory; 2000 level ... lower division; 3000 level ... upper division; 4000 level undergraduate course: advanced upper division".',
         'G5': P + '"5000 level graduate and professional courses" (footnote: "Advanced upper division undergraduate level for 5-year programs"); classified G.',
         'G': P + '"6000/7000 level graduate and professional courses; 8000 level master\'s level, thesis, research; 9000 level doctoral level, thesis, research".'}
parts = re.split(r'<div class="courseblock">', t)[1:]
rows = []
for b in parts:
    code = txt(re.search(r'detail-code[^>]*>(.*?)</span>', b, re.S).group(1)).rstrip(' -')
    title = txt(re.search(r'detail-title[^>]*>(.*?)</span>', b, re.S).group(1))
    cr = txt(re.search(r'detail-hours_html[^>]*>(.*?)</span>', b, re.S).group(1)).strip('()')
    m = re.search(r'<div class="courseblockextra noindent">(.*?)</div>', b, re.S)
    desc = txt(m.group(1)) if m else ''
    n = int(re.search(r'\d{4}', code).group(0))
    if n < 5000: lvl, rk = 'UG', 'UG'
    elif n < 6000: lvl, rk = 'G', 'G5'
    else: lvl, rk = 'G', 'G'
    rows.append(dict(university='Cornell', code=code, title=title, description=desc, level=lvl, level_rule=RULES[rk],
                     credits=cr, source_url=URL, retrieved_utc=ts))
# completeness cross-check against Class Roster API (FA25, SP26, FA26); add roster-only ECE courses
import json
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch
have = {r['code'] for r in rows}
for ro in ['FA25', 'SP26', 'FA26']:
    ru = f'https://classes.cornell.edu/api/2.0/search/classes.json?roster={ro}&subject=ECE'
    tt, rts = fetch('cornell', ru, f'roster_{ro}_ECE.json')
    for c in json.loads(tt)['data']['classes']:
        code = 'ECE ' + c['catalogNbr']
        if code in have: continue
        have.add(code)
        n = int(c['catalogNbr'][:4]); eg = c['enrollGroups'][0]
        lvl, rk = ('UG', 'UG') if n < 5000 else (('G', 'G5') if n < 6000 else ('G', 'G'))
        rows.append(dict(university='Cornell', code=code, title=c['titleLong'], description=c.get('description') or '',
                         level=lvl, level_rule=RULES[rk] + f' [row from Class Roster {ro}, acadCareer={c.get("acadCareer")}; not in Courses of Study listing]',
                         credits=f"{eg['unitsMinimum']:g}-{eg['unitsMaximum']:g} Credits" if eg['unitsMinimum'] != eg['unitsMaximum'] else f"{eg['unitsMinimum']:g} Credits",
                         source_url=ru, retrieved_utc=rts))
        print('added from roster', ro, code, c['titleLong'])
out = write_rows('cornell', rows)
print('nodesc', [(r['code'], r['title']) for r in out if not r['description']])
print('5000-level', sum(r['code'].startswith('ECE 5') for r in out))
off = re.findall(r'Last Four Terms Offered:</strong></span>\s*([^<]*)', t)
print('offered entries', len(off), 'never-offered-since-2023', sum(not re.search(r'202[4-6]', o) for o in off))
