import sys, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
from common_cl import txt, blocks, cls
URL = 'https://catalog.illinois.edu/courses-of-instruction/ece/'
POL = 'https://catalog.illinois.edu/general-information/'
t, ts = fetch('uiuc', URL, 'uiuc_ece.html')
fetch('uiuc', POL, 'uiuc_general_information.html')
RULES = {'UG': 'UIUC 2026-2027 Catalog, General Information: "Courses numbered 100-199/200-299 are lower level undergraduate courses. Courses numbered 300-399 are upper level undergraduate courses."',
         'UG/G': 'UIUC 2026-2027 Catalog, General Information: "Courses numbered 400-499 are upper level undergraduate and graduate courses."',
         'G': 'UIUC 2026-2027 Catalog, General Information: "Courses numbered 500-599 are graduate level courses."'}
def parse(tt):
    out = {}
    for b in blocks(tt):
        ti = txt(cls(b, 'courseblocktitle'))
        m = re.match(r'([A-Z]+) (\d+)\s+(.*?)\s+credit:\s*(.*?)\.?$', ti)
        if not m: print('NOMATCH', ti); continue
        out[f'{m.group(1)} {m.group(2)}'] = (m.group(3), m.group(4), txt(cls(b, 'courseblockdesc')))
    return out
other = {}
def lookup(code):
    subj = code.split()[0]
    if subj not in other:
        u = f'https://catalog.illinois.edu/courses-of-instruction/{subj.lower()}/'
        tt, tts = fetch('uiuc', u, f'uiuc_{subj.lower()}.html')
        other[subj] = (u, tts, parse(tt))
    u, tts, d = other[subj]
    return (u, tts, d.get(code))
rows = []; nres = 0
for code, (title, cr, desc) in parse(t).items():
    n = int(code.split()[1])
    lvl = 'UG' if n < 400 else ('UG/G' if n < 500 else 'G')
    src, rts = URL, ts
    m = re.search(r'See ([A-Z]+ \d+)\s*\.\s*$', desc)
    if m and len(desc) < 200:
        u, tts, got = lookup(m.group(1))
        if got and not re.search(r'See [A-Z]+ \d+\s*\.\s*$', got[2]):
            desc = got[2] + ' [' + desc + ']'
            src, rts = URL + ' ; ' + u, ts + ' ; ' + tts; nres += 1
        else: print('unresolved', code, m.group(1))
    rows.append(dict(university='UIUC', code=code, title=title, description=desc, level=lvl,
                     level_rule=RULES[lvl], credits=cr + ' (credit hours)', source_url=src, retrieved_utc=rts))
print('resolved cross-listed descriptions:', nres)
write_rows('uiuc', rows)
