import sys,re,html; sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, write_rows, clean
SRC={'UG':('https://catalog.tamu.edu/undergraduate/course-descriptions/ecen/','ug_ecen.html'),
     'G':('https://catalog.tamu.edu/graduate/course-descriptions/ecen/','grad_ecen.html')}
RULE={'UG':'Course listed in the Texas A&M 2026-2027 Undergraduate Catalog course descriptions (catalog.tamu.edu/undergraduate/course-descriptions/ecen/; numbers 100-499). Graduate catalog refers to these as "advanced undergraduate courses (300- or 400-level only)" (catalog.tamu.edu/graduate/academic-expectations-general-degree-requirements/).',
      'G':'Course listed in the Texas A&M 2026-2027 Graduate and Professional Catalog course descriptions (catalog.tamu.edu/graduate/course-descriptions/ecen/; numbers 600-799).'}
def txt(s): return re.sub(r'\s+([.,;:])',r'\1',clean(html.unescape(re.sub(r'<[^>]+>',' ',s))))
rows=[]
for lev,(u,f) in SRC.items():
    t,ts=fetch('tamu',u,f)
    for b in re.findall(r'<div class="courseblock">(.*?)</div>',t,re.S):
        title=txt(re.search(r'courseblocktitle">(.*?)</h2>',b,re.S).group(1))
        m=re.match(r'(ECEN\s*\d+(?:/[A-Z]+\s*\d+)?)\s+(.*)',title); code=clean(m.group(1)); ttl=m.group(2)
        cr=re.search(r'Credits?\s+([^.]+?)\.',b); cr=clean(cr.group(1)) if cr else ''
        d=re.search(r'</span>(.*?)</p>',b,re.S); desc=txt(d.group(1)) if d else ''
        rows.append(dict(university='Texas A&M University',code=code,title=ttl,description=desc,level=lev,level_rule=RULE[lev],credits=cr,source_url=u,retrieved_utc=ts))
write_rows('tamu',rows)
