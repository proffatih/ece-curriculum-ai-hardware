import sys, re, html, os, subprocess
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows, clean, RAW
B='https://www.imperial.ac.uk/engineering/departments/electrical-engineering/study/module-catalogue/'
PAGES=['1st-year-eee-and-eie','2nd-year-eee-and-eie','3rd-year-eee-and-eie','4th-year-eee-and-eie','4th-year-year-abroad','msc']
def txt(s): return clean(html.unescape(re.sub(r'<[^>]+>',' ',s)))
mods={}
for p in PAGES:
    t,ts=fetch('imperial',B+p+'/',f'catalogue_{p}.html')
    yr=re.findall(r'<h2>([^<]*20\d\d-\d\d)</h2>',t)
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',t,re.S):
        tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
        if not tds: continue
        cell=tds[0]
        m=re.search(r'\b([A-Z]{4}\d{5})\b\s*(.*)',txt(cell))
        if not m: continue
        code=m.group(1); title=re.sub(r'\.pdf$','',m.group(2)).strip(' -')
        a=re.search(r'href="([^"]+)"',cell)
        pdf=html.unescape(a.group(1)) if a else ''
        if pdf.startswith('/'): pdf='https://www.imperial.ac.uk'+pdf
        rec=mods.setdefault(code,dict(code=code,title=title,pdf=pdf,pages=set(),years=set(),list_url=B+p+'/',list_ts=ts))
        rec['pages'].add(p); rec['years'].update(yr)
        if pdf and not rec['pdf']: rec['pdf']=pdf
print(len(mods),'modules', sum(1 for m in mods.values() if m['pdf']),'with pdf')
if 'list' in sys.argv:
    for m in mods.values(): print(m['code'],m['title'],sorted(m['pages']),sorted(m['years']),bool(m['pdf']))
    sys.exit()
def sect(t,start,stops):
    i=t.find(start)
    if i<0: return ''
    j=len(t)
    for s in stops:
        k=t.find(s,i+len(start))
        if k>0: j=min(j,k)
    return t[i+len(start):j]
rows=[]
for code,m in sorted(mods.items()):
    desc=''; lvl='unknown'; rule='no module descriptor PDF; level unknown'; credits=''; src=m['list_url']; rts=m['list_ts']
    if m['pdf']:
        fn='pdf_'+re.sub(r'[^A-Za-z0-9._-]+','_',m['pdf'].rsplit('/',1)[-1])
        try:
            b,rts=fetch('imperial',m['pdf'],fn,binary=True,sleep=1.0); src=m['pdf']
            pt=subprocess.run(['pdftotext','-layout',os.path.join(RAW,'imperial',fn),'-'],capture_output=True,text=True).stdout
            lv=re.search(r'FHEQ level\s+(?:Level\s+|L)?(\d)',pt)
            if lv:
                L=int(lv.group(1)); lvl='G' if L>=7 else 'UG'
                rule=f'Imperial module specification "FHEQ level {L}" (levels 4-6 => UG, level 7 => G)'
            else:
                L=int(code[4]); lvl='G' if L>=7 else 'UG'; rule=f'FHEQ level not printed in descriptor; inferred from Imperial module code level digit {L} (4-6 UG, 7 G)'
            ec=re.search(r'Credit value\s+(\d+(?:\.\d+)?)',pt)
            if ec: credits=ec.group(1)+' ECTS'
            bd=sect(pt,'Brief description',['Available as a standalone','Statutory details'])
            bd=re.sub(r'of module|\(approx\. 600 chars\.\)','',bd)
            mm=re.search(r'Module content(.*?)(?=\n\s*Learning and|\n\s*Assessment|\n\s*Reading list|\Z)',pt,re.S)
            mc=mm.group(1) if mm else ''
            desc=clean(bd+' '+mc)
        except Exception as e:
            print('ERR',code,e)
    if lvl=='unknown':
        L=int(code[4]); lvl='G' if L>=7 else 'UG'; rule=f'no descriptor fetched; inferred from Imperial module code level digit {L} (4-6 UG, 7 G)'
    rule+='; listed on EEE module catalogue page(s): '+','.join(sorted(m['pages']))+' ('+','.join(sorted(m['years']))+')'
    rows.append(dict(university='Imperial College London',code=code,title=m['title'],description=desc,level=lvl,level_rule=rule,credits=credits,source_url=src,retrieved_utc=rts))
write_rows('imperial',rows)
