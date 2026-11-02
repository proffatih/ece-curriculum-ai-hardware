import sys, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
from common_cl import txt, blocks, cls
RULE_UG = ('Georgia Tech 2026-2027 Catalog lists the course under "Undergraduate-Level Courses" (/courses-undergrad/ece/); '
           'catalogue policy: "A senior with a GPA of at least 2.7 may enroll in a graduate course if the student obtains permission" (graduate courses are not dual-listed).')
RULE_G = ('Georgia Tech 2026-2027 Catalog lists the course under "Graduate-Level Courses" (/courses-grad/ece/).')
rows, skipped = [], []
for url, fn, lvl, rule in [('https://catalog.gatech.edu/courses-undergrad/ece/', 'gatech_courses_undergrad_ece.html', 'UG', RULE_UG),
                           ('https://catalog.gatech.edu/courses-grad/ece/', 'gatech_courses_grad_ece.html', 'G', RULE_G)]:
    t, ts = fetch('gatech', url, fn)
    for b in blocks(t):
        ti = txt(cls(b, 'courseblocktitle'))
        m = re.match(r'(ECE \w+)\.\s+(.*?)\.\s+([\d\-\.]+(?: to [\d\.]+)? Credit Hours?)\.?$', ti)
        if not m:
            print('NOMATCH', ti); continue
        code, title, cr = m.groups()
        if 'X' in code.split()[1]:
            skipped.append(ti); continue
        rows.append(dict(university='Georgia Tech', code=code, title=title, description=txt(cls(b, 'courseblockdesc')),
                         level=lvl, level_rule=rule, credits=cr, source_url=url, retrieved_utc=ts))
print('skipped placeholders:', skipped)
write_rows('gatech', rows)
