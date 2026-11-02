import sys, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
from common_cl import txt, blocks, cls
URL = 'https://catalog.mit.edu/subjects/6/'
t, ts = fetch('mit', URL, 'mit_subjects_6.html')
RULE = ('MIT Bulletin subject level line: each subject is marked "U" (undergraduate) or "G" (graduate) '
        'before the term, e.g. "U (Fall)"; alternate-year subjects list "Acad Year YYYY: U/G (term)". Value taken verbatim per subject.')
rows = []
for b in blocks(t):
    title = txt(cls(b, 'courseblocktitle'))
    m = re.match(r'(\S+)\s+(.*)$', title)
    code, name = m.group(1), m.group(2)
    terms = txt(cls(b, 'courseblockterms'))
    lv = set(re.findall(r'(?:^|:\s|\s)([UG])\s*\(', ' ' + terms))
    if lv == {'U'}: level = 'UG'
    elif lv == {'G'}: level = 'G'
    elif lv == {'U', 'G'}: level = 'UG/G'
    else: level = 'unknown'
    hours = txt(cls(b, 'courseblockhours'))
    cr = ''
    mh = re.match(r'(\d+)-(\d+)-(\d+) units', hours)
    if mh: cr = f'{sum(map(int, mh.groups()))} MIT units ({mh.group(0)})'
    elif hours: cr = hours.split('.')[0]
    rows.append(dict(university='MIT', code=code, title=name, description=txt(cls(b, 'courseblockdesc')),
                     level=level, level_rule=RULE, credits=cr, source_url=URL, retrieved_utc=ts))
# resolve "See description under subject X" using the referenced subject's own Bulletin page
deptpage = {}
def lookup(ref):
    dept = ref.split('.')[0]
    if dept not in deptpage:
        u = f'https://catalog.mit.edu/subjects/{dept.lower()}/'
        try:
            tt, tts = fetch('mit', u, f'mit_subjects_{dept.lower()}.html')
        except Exception as e:
            print('fail', u, e); deptpage[dept] = None; return None
        d = {}
        for bb in blocks(tt):
            ti = txt(cls(bb, 'courseblocktitle'))
            c = ti.split()[0]
            d[re.sub(r'\[?J\]?$', '', c)] = txt(cls(bb, 'courseblockdesc'))
        deptpage[dept] = (u, tts, d)
    if not deptpage[dept]: return None
    u, tts, d = deptpage[dept]
    desc = d.get(re.sub(r'\[?J\]?$', '', ref))
    return (u, tts, desc) if desc and 'See description under' not in desc else None
nres = 0
for r in rows:
    m = re.search(r'See description under subject (\S+?)\s*\.(?:\s|$)(.*)$', r['description'])
    if m:
        got = lookup(m.group(1))
        if got:
            u, tts, desc = got
            r['description'] = desc + ((' ' + m.group(2).strip()) if m.group(2).strip() else '')
            r['source_url'] = URL + ' ; ' + u
            r['retrieved_utc'] = ts + ' ; ' + tts
            nres += 1
        else:
            print('unresolved', r['code'], m.group(1))
print('resolved', nres)
out = write_rows('mit', rows)
import collections
print('see-under', sum('See description under' in r['description'] for r in out))
print('unknown', [(r['code'], r['title']) for r in out if r['level']=='unknown'])
print('nocredit', [(r['code']) for r in out if not r['credits']][:20])
print(collections.Counter(re.match(r'6\.(\D*\d?)', r['code']).group(1)[:2] if r['code'].startswith('6.') else r['code'][:4] for r in out))
