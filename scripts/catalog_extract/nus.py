"""NUS ECE catalogue from NUSMods API (AY2026-2027).
Scope: modules whose 'department' == 'Electrical and Computer Engineering' (any prefix: EE, CEG, CS..DE, ME, IND, TDEE, GET)
       + all CG-prefix modules (department 'Computing and Engineering Programme' = B.Eng. Computer Engineering, jointly run by ECE & SoC).
Excluded: EX2022 (exchange-credit placeholder, not a course); EE*E SCALE Dean's Office modules (continuing-education legacy, dept != ECE);
          EE5106 (Mechanical Engineering dept).
"""
import sys, json, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
YEAR='2026-2027'
URL=f'https://api.nusmods.com/v2/{YEAR}/moduleInfo.json'
LR_URL='https://nus.edu.sg/registrar/docs/info/prospective-students---non-graduating/non-graduating-course-restrictions.pdf'
txt, ts = fetch('nus', URL, f'moduleInfo_{YEAR}.json')
data=json.loads(txt)
rows=[]; noffer=0
for m in data:
    c=m['moduleCode']; dep=m.get('department','')
    if c=='EX2022': continue
    if not (dep=='Electrical and Computer Engineering' or c.startswith('CG')): continue
    d=re.search(r'\d', c); lvl_digit=int(c[d.start()])
    level='UG' if 1<=lvl_digit<=4 else ('G' if lvl_digit>=5 else 'unknown')
    if not m.get('semesterData'): noffer+=1
    rows.append(dict(university='National University of Singapore', code=c, title=m.get('title',''),
        description=m.get('description',''), level=level,
        level_rule=f'NUS Registrar: first digit of 4-digit course number = level; Level 1000-4000 undergraduate, 5000-6000 graduate ({LR_URL})',
        credits=f"{m.get('moduleCredit','')} Units", source_url=URL, retrieved_utc=ts))
print('not offered in any semester this AY:', noffer)
write_rows('nus', rows)
