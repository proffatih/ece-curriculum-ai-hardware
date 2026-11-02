"""NTU School of EEE catalogue.
UG: 'Content of Courses' (wis.ntu.edu.sg AUS_SUBJ_CONT, undergraduate system) programme-year lists for EEE-school programmes
    (EEE Y1-4, EESJ, IEM Y1-4, EEE/IEM+Economics double degrees, Renaissance Eng (EEE/IEM)) plus the EEE 'Broadening and
    Deepening/Unrestricted Electives' list (GLOAD;EEE), for AY2025 Sem1, Sem2, Special Term and AY2026 Sem1.
    Scope: codes with School-of-EEE prefixes EE, IE (Information Engineering), IM (IEM).
G:  MSc curriculum tables on the five NTU EEE MSc programme pages (CoE graduate programme detail pages).
Level: UG if listed in the undergraduate Content of Courses; G if listed in an MSc curriculum; UG/G if in both.
"""
import sys, os, re, html, glob, csv
sys.path.insert(0, 'raw/_scripts')
from catv2 import write_rows, RAW
D=os.path.join(RAW,'ntu')
POST='https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1'
log={}
for line in open(os.path.join(D,'_fetch_log.tsv')):
    ts,st,u,fn=line.rstrip('\n').split('\t'); log[fn]=(ts,u)
def T(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).replace('\xa0',' ').strip()
PFX=('EE','IE','IM')
ug={}  # code -> dict
order={'2025_1':1,'2025_2':2,'2025_S':3,'2026_1':4}
files=sorted(glob.glob(D+'/20*.html'), key=lambda p:order[os.path.basename(p)[:6]])
src_count={}
for p in files:
    fn=os.path.basename(p); t=open(p,encoding='utf-8',errors='replace').read()
    parts=re.split(r'(?=<TD WIDTH="100"><B><FONT SIZE=2 COLOR=#0000FF>[A-Z]{2,4}\d{4}[A-Z]?</FONT>)', t)
    for ch in parts[1:]:
        blue=re.findall(r'COLOR=#0000FF>(.*?)</FONT>', ch, re.S)
        code=blue[0].strip(); title=T(blue[1]); au=re.sub(r'\s*AU','',T(blue[2]))
        if not code.startswith(PFX): continue
        dm=re.search(r'<TD WIDTH="650" colspan="[34]"><FONT SIZE=2>(.*?)</TD>', ch, re.S|re.I)
        desc=T(dm.group(1)) if dm else ''
        ts,u=log[fn]
        src_count.setdefault(code,set()).add(fn)
        ug[code]=dict(code=code,title=title,description=desc or (ug.get(code,{}).get('description','')),credits=f'{au} AU',
                      source_url=f'{POST} [POST acadsem={fn[:6]}; r_course_yr={u.split("r_course_yr=")[1].split(" ")[0]}]',retrieved_utc=ts)
g={}
for p in sorted(glob.glob(D+'/grad__master-of-science-*.html')):
    fn=os.path.basename(p); t=open(p,encoding='utf-8',errors='replace').read()
    ts,u=log[fn]
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        tds=[T(x) for x in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(tds)>=2 and re.fullmatch(r'EE\d{4}[A-Z]?', tds[0]):
            code=tds[0]; au=tds[3] if len(tds)>=4 else ''
            if code in g:
                if not g[code]['description'] and len(tds)>2: g[code]['description']=tds[2]
                g[code]['progs'].append(fn); continue
            g[code]=dict(code=code,title=tds[1],description=tds[2] if len(tds)>2 else '',credits=f'{au} AU' if au else '',source_url=u,retrieved_utc=ts,progs=[fn])
LR_UG='Listed in NTU undergraduate "Content of Courses" (wis.ntu.edu.sg) for EEE-school UG programmes'
LR_G='Listed in NTU EEE MSc programme curriculum (graduate courses offered by MSc)'
rows=[]
for code in sorted(set(ug)|set(g)):
    a,b=ug.get(code),g.get(code)
    if a and b:
        r=dict(a); lvl='UG/G'; lr=LR_UG+'; also '+LR_G+' ('+b['source_url']+')'
        if not r['description']: r['description']=b['description']
    elif a: r=dict(a); lvl='UG'; lr=LR_UG
    else: r=dict(b); r.pop('progs'); lvl='G'; lr=LR_G
    r.update(university='Nanyang Technological University', level=lvl, level_rule=lr)
    rows.append(r)
write_rows('ntu', rows)
print('UG-only list codes',len(ug),'MSc codes',len(g),'overlap',len(set(ug)&set(g)))
