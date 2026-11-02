import sys,re,html,os,csv,datetime; sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, write_rows, clean, RAW
LIST='https://courses.ece.cmu.edu/'
CAT='http://coursecatalog.web.cmu.edu/schools-colleges/collegeofengineering/departmentofelectricalandcomputerengineering/'
def txt(s): return re.sub(r'\s+([.,;:])',r'\1',clean(html.unescape(re.sub(r'<[^>]+>',' ',s))))
t,ts_list=fetch('cmu',LIST,'courses_ece_root.html')
tc,ts_cat=fetch('cmu',CAT,'catalog_ece_dept.html')
# official 2026-27 undergraduate catalog entries
cat={}
for code,title,dd in re.findall(r'<dt class="keepwithnext">(18-\d+)\s+(.*?)</dt>\s*<dd>(.*?)</dd>',tc,re.S):
    d=txt(dd); m=re.match(r'((?:Fall|Spring|Summer|Intermittent|All Semesters|Fall and Spring|Spring and Summer|Fall and Summer)[^:<]*?)(?::\s*([\d,\-]+(?:\s*-\s*\d+)?|Variable)\s*units)?\s*(?=[A-Z])',d)
    cat[code]=dict(title=txt(title),raw=d)
# department list sections
i_ug=t.find('Undergraduate Courses',4600); i_g=t.find('Graduate Courses',39000); i_cit=t.find('CIT Interdisciplinary',180000)
secs=[('UG',t[i_ug:i_g]),('G',t[i_g:i_cit])]
SEM=re.compile(r'(Spring|Summer|Fall)\s+(\d{4})')
def ay_start(s,y):  # academic year start
    y=int(y); return y if s=='Fall' else y-1
RULE={'UG':'Listed under "Undergraduate Courses" on the CMU ECE department Course List (https://courses.ece.cmu.edu/). CMU catalog: "xx-6xx courses may be either undergraduate senior-level or graduate-level, and xx-7xx courses and higher are graduate-level" (CMU 2026-2027 Undergraduate Catalog, ECE Course Descriptions).',
      'G':'Listed under "Graduate Courses" on the CMU ECE department Course List (https://courses.ece.cmu.edu/). CMU catalog: "xx-6xx courses may be either undergraduate senior-level or graduate-level, and xx-7xx courses and higher are graduate-level" (CMU 2026-2027 Undergraduate Catalog, ECE Course Descriptions).'}
allrows=[]; missing=[]
for lev,s in secs:
    for href,code,title,loc,units,status in re.findall(r'<tr>\s*<td><a href="([^"]+)">([^<]+)</a></td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>',s,re.S):
        p=os.path.join(RAW,'cmu','pages','course_'+href+'.html')
        desc=''; sems=[]; ts=None
        if os.path.exists(p) and os.path.getsize(p)>0:
            pg=open(p,encoding='utf-8',errors='replace').read()
            ts=datetime.datetime.fromtimestamp(os.path.getmtime(p),datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            m=re.search(r'Description:</h4>(.*?)(?:<strong>Last Modified|<h4>Semesters offered|Helpful links)',pg,re.S)
            desc=txt(m.group(1)) if m else ''
            if desc.lower().startswith('no course description available'): desc=''
            sm=re.search(r'Semesters offered:(.*?)Helpful links',txt(pg))
            sems=SEM.findall(sm.group(1)) if sm else []
        else: missing.append(href)
        last=max((ay_start(*x) for x in sems),default=None)
        allrows.append(dict(sec=lev,code=txt(code),title=txt(title),location=txt(loc),units=txt(units),status=txt(status),href=href,
                            last_ay_start=last,n_sem=len(sems),in_catalog_2026_27=txt(code) in cat,desc=desc,ts=ts))
# sidecar with everything
with open(os.path.join(RAW,'cmu','cmu_all_courses_with_offering_history.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
RECENT=2022  # offered in AY2022-23 or later
rows=[]
for a in allrows:
    keep = (a['last_ay_start'] is not None and a['last_ay_start']>=RECENT) or a['in_catalog_2026_27']
    if not keep: continue
    desc=a['desc']; src=LIST+a['href']; ts=a['ts'] or ts_list
    if not desc and a['in_catalog_2026_27']:
        desc=cat[a['code']]['raw']; src=CAT; ts=ts_cat
    rows.append(dict(university='Carnegie Mellon University',code=a['code']+(f" ({a['location']})" if a['location']!='Pittsburgh' else ''),title=a['title'],description=desc,
        level=a['sec'],level_rule=RULE[a['sec']]+' Inclusion: offered AY2022-23 or later per course page "Semesters offered", or listed in 2026-27 catalog.',credits=(a['units']+' units') if a['units'] and a['units']!='Variable' else a['units'],source_url=src,retrieved_utc=ts))
print('missing pages',len(missing),missing[:10])
print('all',len(allrows),'kept',len(rows))
cat_not_in_list=[c for c in cat if c not in {a['code'] for a in allrows}]
print('catalog codes not in dept list',cat_not_in_list)
RULE_CAT=('Course appears in the CMU 2026-2027 Undergraduate Catalog ECE Course Descriptions but not on the ECE department Course List; level assigned by numbering convention matching the department Course List split '
          '(Undergraduate Courses = 18-0xx..18-5xx; Graduate Courses = 18-6xx and higher). CMU catalog: "xx-6xx courses may be either undergraduate senior-level or graduate-level, and xx-7xx courses and higher are graduate-level".')
for code,title,dd in re.findall(r'<dt class="keepwithnext">(18-\d+)\s+(.*?)</dt>\s*<dd>(.*?)</dd>',tc,re.S):
    if code not in cat_not_in_list: continue
    first,_,rest=dd.partition('<br/>')
    um=re.search(r':\s*(.+?)\s*units',txt(first))
    lev='UG' if int(code[3])<=5 else 'G'
    rows.append(dict(university='Carnegie Mellon University',code=code,title=txt(title),description=txt(rest),level=lev,level_rule=RULE_CAT,
        credits=(um.group(1)+' units') if um else '',source_url=CAT,retrieved_utc=ts_cat))
# de-duplicate campus variants: drop non-Pittsburgh rows whose base number 18-xxx already exists among Pittsburgh/catalog rows
base=lambda c: c[:6]
pitt=[r for r in rows if '(' not in r['code']]
have={base(r['code']) for r in pitt}
other=[r for r in rows if '(' in r['code']]
kept_other=[r for r in other if base(r['code']) not in have]
print('campus-variant rows dropped (base exists):',len(other)-len(kept_other),'kept campus-only:',len(kept_other))
for r in kept_other: r['level_rule']+=' Campus-only offering (no Pittsburgh/catalog row with the same base number).'
write_rows('cmu',pitt+kept_other)
