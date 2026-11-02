import sys, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
from common_cl import txt, blocks, cls
UG = 'https://academiccatalog.umd.edu/undergraduate/approved-courses/enee/'
GR = 'https://academiccatalog.umd.edu/graduate/courses/enee/'
POL = 'https://academiccatalog.umd.edu/undergraduate/approved-courses/'
fetch('umd', POL, 'umd_ug_approved_courses_index.html')
P = 'UMD 2026-2027 Academic Catalog, Approved Courses numbering key: '
RULES = {'UG': P + '"100-199: Courses primarily for first-year students; 200-299: primarily for sophomore students; 300-399: Junior/Senior courses (not acceptable for credit toward graduate degrees)"; course appears only in the undergraduate catalog.',
         'UG/G': P + '"400-499: Junior/Senior courses (acceptable for credit toward some graduate degrees)"; course appears in both the undergraduate approved-courses and graduate catalog ENEE listings.',
         'G': P + '"600-898: Courses restricted to graduate students; 799: Master\'s Thesis credit; 899: Doctoral Dissertation credit"; course appears in the graduate catalog.'}
def parse(url, fn):
    t, ts = fetch('umd', url, fn)
    d = {}
    for b in blocks(t):
        ti = txt(cls(b, 'courseblocktitle'))
        m = re.match(r'(ENEE\w+)\s+(.*?)\s*\(([^()]*Credits?)\)\s*$', ti)
        if not m: print('NOMATCH', ti); continue
        d[m.group(1)] = (m.group(2), m.group(3), txt(cls(b, 'courseblockdesc')), ts)
    return d
u, g = parse(UG, 'umd_ug_enee.html'), parse(GR, 'umd_grad_enee.html')
rows = []
for code in sorted(set(u) | set(g)):
    inu, ing = code in u, code in g
    n = int(re.match(r'ENEE(\d+)', code).group(1))
    lvl = 'UG/G' if (inu and ing) else ('UG' if inu else 'G')
    rec = u[code] if inu else g[code]
    src = ' ; '.join(x for x, f in [(UG, inu), (GR, ing)] if f)
    rts = ' ; '.join(d[code][3] for d, f in [(u, inu), (g, ing)] if f)
    if inu and ing and u[code][:3] != g[code][:3]: print('DIFF', code)
    # sanity vs numbering
    exp = 'UG' if n < 400 else ('UG/G' if n < 500 else 'G')
    if exp != lvl: print('LEVEL MISMATCH', code, lvl, exp)
    rows.append(dict(university='UMD College Park', code=code, title=rec[0], description=rec[2], level=lvl,
                     level_rule=RULES[lvl], credits=rec[1], source_url=src, retrieved_utc=rts))
write_rows('umd', rows)
