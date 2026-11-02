"""Bogazici EE: department English course-description pages (Undergraduate Courses 1268, Graduate Courses 1282).
Scope: EE-prefixed entries only (pages also list service/other-department courses, excluded and counted)."""
import sys,re,html
sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, clean, write_rows
PAGES=[('UG','https://ee.bogazici.edu.tr/en/pages/undergraduate-courses-new/1268','en_undergraduate-courses_1268.html'),
       ('G','https://ee.bogazici.edu.tr/en/pages/graduate-courses/1282','en_graduate-courses_1282.html')]
def txt(h): return clean(html.unescape(re.sub(r'<[^>]+>',' ',h)).replace('\xa0',' '))
rows=[]; excl={}
for lev,url,fn in PAGES:
    s,ts=fetch('bogazici',url,fn)
    items=s.split('accordion-module-v2-item')[1:]
    n=0
    for it in items:
        mt=re.search(r'<div class="title">(.*?)</div>',it,flags=re.S)
        if not mt: continue
        head=txt(mt.group(1))
        m=re.match(r'([A-Z]{2,4})\s*(\d{2,3}[A-Z]?)\s*(.*)',head)
        if not m: print('nohead',head); continue
        pre,num,title=m.groups()
        if pre!='EE': excl[(lev,pre)]=excl.get((lev,pre),0)+1; continue
        mc=re.search(r'<div class="text">(.*?)</div>\s*</div>\s*</div>',it,flags=re.S)
        body=mc.group(1) if mc else ''
        paras=[txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>',body,flags=re.S)]
        paras=[p for p in paras if p]
        if not paras and body: paras=[txt(body)]
        credits=''; desc=[]; i=0
        while i<len(paras):
            p=paras[i]
            if p.startswith('Credits:'):
                rest=p[len('Credits:'):].strip()
                if rest:
                    mm=re.match(r'^(\d+(?:\s*P/F)?)\s+(\S.*)$',rest)
                    if mm: credits=mm.group(1); desc.append(mm.group(2))
                    else: credits=rest
                elif i+1<len(paras): credits=paras[i+1]; i+=1
            elif p.startswith('Prerequisite'): break
            elif p=='Syllabus': pass
            else: desc.append(p)
            i+=1
        n+=1
        rows.append(dict(university='Boğaziçi University, Dept. of Electrical and Electronics Engineering',
            code=f'EE {num}',title=title,description=' '.join(desc),level=lev,
            level_rule=('listed on department page "Undergraduate Courses" (UNDERGRADUATE PROGRAM section)' if lev=='UG'
                        else 'listed on department page "Graduate Courses" (GRADUATE PROGRAMS section)')+'; i.e. classified by which programme document lists it',
            credits=credits,source_url=url,retrieved_utc=ts))
    print(lev,'EE items',n)
print('excluded non-EE',excl)
have={r['code'] for r in rows}
# Supplement 1: curriculum page (Ders Programi 1204; table text is English) - EE rows not on the course-description pages
CURR='https://ee.bogazici.edu.tr/tr/pages/ders-programi/1204'
s,ts=fetch('bogazici',CURR,'tr_ders-programi_1204.html')
for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',s,flags=re.S):
    tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,flags=re.S)
    if len(tds)<4: continue
    code=txt(tds[0])
    if not re.match(r'EE \d{3}$',code) or code in have: continue
    parts=[txt(x) for x in re.split(r'<br\s*/?>',tds[1]) if txt(x)]
    title=parts[0]; desc=' '.join(parts[2:]) if len(parts)>2 else ''
    rows.append(dict(university='Boğaziçi University, Dept. of Electrical and Electronics Engineering',code=code,title=title,description=desc,level='UG',
        level_rule='listed in the department undergraduate curriculum (Ders Programi) page; classified by which programme document lists it',
        credits=f'{txt(tds[2])} credits; ECTS {txt(tds[3])}',source_url=CURR,retrieved_utc=ts)); have.add(code); print('curr add',code,title)
# Supplement 2: Turkish undergraduate course-description page 1206 - EE entries absent from the English page (kept in original Turkish)
TRU='https://ee.bogazici.edu.tr/tr/pages/ders-icerikleri/1206'
s,ts=fetch('bogazici',TRU,'tr_ders-icerikleri_1206.html')
for it in s.split('accordion-module-v2-item')[1:]:
    mt=re.search(r'<div class="title">(.*?)</div>',it,flags=re.S)
    if not mt: continue
    m=re.match(r'EE\s*(\d{3})\s*(.*)',txt(mt.group(1)))
    if not m or 'EE '+m.group(1) in have: continue
    mc=re.search(r'<div class="text">(.*?)</div>\s*</div>\s*</div>',it,flags=re.S)
    paras=[txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>',mc.group(1) if mc else '',flags=re.S)]
    paras=[p for p in paras if p]; cr=''; desc=[]; i=0
    while i<len(paras):
        p=paras[i]
        if p.startswith('Kredi:'):
            rest=p[6:].strip()
            if rest: cr=rest
            elif i+1<len(paras): cr=paras[i+1]; i+=1
        elif p.startswith('Prerequisite') or p.startswith('Önkoşul'): break
        else: desc.append(p)
        i+=1
    code='EE '+m.group(1)
    rows.append(dict(university='Boğaziçi University, Dept. of Electrical and Electronics Engineering',code=code,title=m.group(2),description=' '.join(desc),level='UG',
        level_rule='listed on department Turkish page "Ders İçerikleri" under LİSANS (undergraduate); classified by which programme document lists it',
        credits=cr,source_url=TRU,retrieved_utc=ts)); have.add(code); print('tr add',code,m.group(2))
write_rows('bogazici',rows)
