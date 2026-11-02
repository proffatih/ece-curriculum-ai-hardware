"""HKUST ECE catalogue, AY2026-27, prog-crs.hkust.edu.hk.
Scope: ELEC (Electronic & Computer Engineering) UG + PG, CPEG (Computer Engineering programme, UG), EESM (MSc Electronic Engineering, PG).
Level: course on ugcourse catalogue -> UG; on pgcourse catalogue -> G; both -> UG/G.
"""
import sys, re, html
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows
Y='2026-27'
SRC=[('ugcourse','ELEC'),('ugcourse','CPEG'),('pgcourse','ELEC'),('pgcourse','EESM')]
def T(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
recs={}
for cat,subj in SRC:
    u=f'https://prog-crs.hkust.edu.hk/{cat}/{Y}/{subj}'
    t,ts=fetch('hkust',u,f'{cat}_{Y}_{subj}.html')
    items=re.split(r'<li class="crse accordion-item">', t)[1:]
    n=0
    for it in items:
        code=T(re.search(r'<div class="crse-code">(.*?)</div>',it,re.S).group(1))
        title=T(re.search(r'<div class="crse-title">(.*?)</div>',it,re.S).group(1))
        um=re.search(r"<div class=\"crse-(?:unit|vector)\">(.*?)</div>",it,re.S); unit=T(um.group(1)).strip('[]') if um else ""
        dm=re.search(r'<div class="header">Description</div><div class="data">(.*?)</div>',it,re.S)
        desc=T(dm.group(1)) if dm else ''
        lv='UG' if cat=='ugcourse' else 'G'
        if code in recs:
            r=recs[code]
            if r['level']!=lv: r['level']='UG/G'; r['source_url']+=' ; '+u
            continue
        recs[code]=dict(university='Hong Kong University of Science and Technology',code=code,title=title,description=desc,level=lv,
            credits=unit,source_url=u,retrieved_utc=ts); n+=1
    print(cat,subj,len(items),n)
LR={'UG':'Listed in HKUST Undergraduate Course Catalog; first digit = level: 1 introductory, 2 intermediate, 3/4 advanced (https://prog-crs.hkust.edu.hk/ugcourse/2026-27)',
    'G':'Listed in HKUST Postgraduate Course Catalog; first digit = level: 5/6/7 = postgraduate (https://prog-crs.hkust.edu.hk/pgcourse/2026-27)',
    'UG/G':'Listed in both HKUST UG and PG course catalogs'}
rows=[]
for r in recs.values(): r['level_rule']=LR[r['level']]; rows.append(r)
write_rows('hkust', rows)
import collections; print(collections.Counter((r['code'].split()[0], r['code'].split()[1][0], r['level']) for r in rows))
