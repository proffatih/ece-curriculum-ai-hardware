import sys, re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows, clean
R='raw/oxford/'
U_PRE='https://eng.ox.ac.uk/media/hbxnuycd/prelims-handbook-2026-27-final.pdf'
U_FHS='https://eng.ox.ac.uk/media/l1lfctjq/fhs-handbook-2026-27-final.pdf'
U_B='https://eng.ox.ac.uk/media/xryh013e/3rd-year-syllabus-2025-26-final.pdf'
U_C='https://eng.ox.ac.uk/media/onzmb5xf/4th-year-syllabus-2025-26-final.pdf'
ts={}
for u,f in [(U_PRE,'prelims_handbook_2026-27.pdf'),(U_FHS,'fhs_handbook_2026-27.pdf'),(U_B,'syllabus_3rd_year_2025-26.pdf'),(U_C,'syllabus_4th_year_2025-26.pdf')]:
    _,ts[u]=fetch('oxford',u,f,binary=True)
UG_RULE='Oxford MEng Engineering Science {part} (year {y}); Parts before Part C lead to BA exit award (FHS handbook 2026-27 s.12.8) => UG'
G_RULE='Oxford MEng Engineering Science Part C (year 4): FHS handbook 2026-27 states the MEng is an integrated Masters taught to FHEQ Level 7 and students not entering Part C exit with a BA (s.12.8), so Part C is the Masters-only year => G'
rows=[]
pre=open(R+'prelims_handbook_2026-27.txt').read()
sy=pre[pre.find('7.6 Course syllabus\nIn P1'):]
sy=sy[:sy.find('More detailed information on the syllabus')]
paras=[clean(p) for p in sy.split('\n\n') if p.strip()]
P={'P1':'Mathematics','P2':'Electronic and Information Engineering','P3':'Structures and Mechanics','P4':'Energy','P5':'Engineering Coursework'}
for c,t in P.items():
    d=next((p for p in paras if p.startswith(f'In {c} ') or p.startswith(f'For {c} ')),'')
    assert f'{c} {t}' in pre, c
    rows.append(dict(university='University of Oxford',code=c,title=t,description=d,level='UG',level_rule=UG_RULE.format(part='Preliminary year (Prelims)',y=1),credits='',source_url=U_PRE,retrieved_utc=ts[U_PRE]))
fhs=open(R+'fhs_handbook_2026-27.txt').read()
A={'A1':'Mathematics','A2':'Electronic and Information Engineering','A3':'Structures, Materials and Dynamics','A4':'Energy Systems','A5':'Engineering Practical Work'}
for c,t in A.items():
    assert re.search(c+r'\s+'+re.escape(t.split()[0]),fhs), c
    rows.append(dict(university='University of Oxford',code=c,title=t,description='',level='UG',level_rule=UG_RULE.format(part='FHS Part A',y=2),credits='',source_url=U_FHS+' (s.11.2)',retrieved_utc=ts[U_FHS]))
def parse(fn,url,lvl,rule,pfx):
    t=open(R+fn).read()
    t=re.sub(r'\n\s*[34](rd|th) Year Syllabus 2025-26\s+Department of Engineering Science\s*\n','\n',t)
    heads=list(re.finditer(r'^\s*(?:Paper\s+)?('+pfx+r'\d{1,2}(?:E\d)?)\s*:?\s+([A-Z][^\n;]+)$',t,re.M))
    out=[]
    for i,h in enumerate(heads):
        end=heads[i+1].start() if i+1<len(heads) else len(t)
        body=t[h.end():end]
        title=clean(h.group(2)).replace('(EEM pathway only)','').strip()
        out.append(dict(university='University of Oxford',code=h.group(1),title=title,description=clean(body),level=lvl,level_rule=rule,credits='',source_url=url,retrieved_utc=ts[url]))
    return out
B=parse('syllabus_3rd_year_2025-26.txt',U_B,'UG',UG_RULE.format(part='FHS Part B',y=3),'B')
C=parse('syllabus_4th_year_2025-26.txt',U_C,'G',G_RULE,'C')
b3=open(R+'syllabus_3rd_year_2025-26.txt').read()
m=re.search(r'(Paper B3 will consist of.*?Course Handbook\.)',b3,re.S)
B.append(dict(university='University of Oxford',code='B3',title='Group Design Project',description=clean(m.group(1)) if m else '',level='UG',level_rule=UG_RULE.format(part='FHS Part B',y=3),credits='',source_url=U_B,retrieved_utc=ts[U_B]))
B.append(dict(university='University of Oxford',code='B4',title='Engineering Practical Work',description='',level='UG',level_rule=UG_RULE.format(part='FHS Part B',y=3),credits='',source_url=U_FHS+' (s.12.4)',retrieved_utc=ts[U_FHS]))
C.append(dict(university='University of Oxford',code='4YP',title='Fourth Year Project',description='',level='G',level_rule=G_RULE,credits='',source_url=U_FHS+' (s.13.4)',retrieved_utc=ts[U_FHS]))
rows+=B+C
for r in B+C: print(r['code'],'|',r['title'][:60],'|',len(r['description']))
write_rows('oxford',rows)
