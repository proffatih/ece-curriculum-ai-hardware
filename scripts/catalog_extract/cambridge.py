import sys, re, html
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows, clean
REP='https://www.admin.cam.ac.uk/reporter/2024-25/weekly/6788/section3.shtml'
SO='https://www.admin.cam.ac.uk/univ/so/pdfs/2025/Cambridge-Statutes-and-Ordinances-2025.pdf'
t,ts=fetch('cambridge',REP,'reporter_6788_section3.html')
_,ts_so=fetch('cambridge',SO,'statutes_ordinances_2025.pdf',binary=True)
def txt(s): return clean(html.unescape(re.sub(r'<[^>]+>',' ',s)))
# restrict to the Engineering Tripos notice (before Manufacturing Engineering Tripos notice body)
a=t.find('Part II<span'); 
start=t.find('The Faculty Board of Engineering gives notice')
end=t.find('Manufacturing Engineering Tripos',start)
body=t[start:end]
iib_at=body.find('Part II<sub>b</sub> Modules') if 'Part II<sub>b</sub> Modules' in body else None
rows=[]
# split into IIA/IIB by locating 'Part IIb Modules' heading text
plain_idx=[m.start() for m in re.finditer(r'Part(?:&nbsp;|\s)II\s*(?:<[^>]+>)?\s*b\s*(?:</[^>]+>)?\s*Modules',body)]
cut=plain_idx[0] if plain_idx else len(body)
G_RULE_IIB='Engineering Tripos Part IIB (4th year of integrated MEng); per Cambridge Statutes & Ordinances 2025 ("Degrees in Engineering: Master of Engineering", p.438) honours in Part IIB entitles the student to proceed to the M.Eng. degree => G (Masters-level part)'
UG_RULE_IIA='Engineering Tripos Part IIA (3rd year; precedes the MEng year Part IIB) => UG'
for part,seg in [('IIA',body[:cut]),('IIB',body[cut:])]:
    group=''
    for tr in re.findall(r'<tr>(.*?)</tr>',seg,re.S):
        tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
        if len(tds)==1:
            group=txt(tds[0]); continue
        if len(tds)>=2:
            code,title=txt(tds[0]),txt(tds[1])
            if code in ('Unit',) or not re.match(r'^\d[A-Z]',code): continue
            if part=='IIA':
                shared=group.startswith('Group S')
                lvl='UG/G' if shared else 'UG'
                rule=UG_RULE_IIA if not shared else 'Engineering Tripos Part IIA "Group S: modules shared with Part IIB" => offered in Part IIA (UG) and Part IIB (G) => UG/G'
            else:
                lvl='G'; rule=G_RULE_IIB
            rows.append(dict(university='University of Cambridge',code=code,title=title,description='',level=lvl,
                 level_rule=rule+f'; Reporter group: {group}',credits='',source_url=REP,retrieved_utc=ts))
shared={r['code'] for r in rows if r['level']=='UG/G'}
rows=[r for r in rows if not (r['code'] in shared and r['level']=='G')]
# Part IA / IB papers: Statutes & Ordinances 2025, Engineering Tripos regulations 8 and 12
IA=['Mechanical engineering','Structures and materials','Electrical and information engineering','Mathematical methods']
IB=['Mechanics','Structures','Materials','Thermofluid mechanics','Electrical engineering','Information engineering','Mathematical methods','Selected topics']
so_txt=open('raw/cambridge/so2025.txt').read()
for part,lst in [('IA',IA),('IB',IB)]:
    for i,ti in enumerate(lst,1):
        assert ti in so_txt, ti
        rows.append(dict(university='University of Cambridge',code=f'Part {part} Paper {i}',title=ti,description='',level='UG',
             level_rule=f'Engineering Tripos Part {part} paper (Statutes & Ordinances 2025, Engineering Tripos reg. {"8" if part=="IA" else "12"}); years 1-2 of BA/MEng => UG',
             credits='',source_url=SO+(' (p.322)'),retrieved_utc=ts_so))
write_rows('cambridge',rows)
from collections import Counter
print(Counter(r['level_rule'].split(';')[0][:40] for r in rows))
