"""Bilkent EEE: official Online Academic Catalog (OAC) department course list dc12.html + course pages."""
import sys,re,html
sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, clean, write_rows
BASE='https://catalog.bilkent.edu.tr'
LIST=BASE+'/dep/dc12.html'
fetch('bilkent',BASE+'/dep/d12.html','dep_d12.html')  # dept/programme page (curricula), saved for provenance
s,ts0=fetch('bilkent',LIST,'dep_dc12.html')
def txt(h): return clean(html.unescape(re.sub(r'<[^>]+>',' ',h)).replace('\xa0',' '))
rows=[]
for tr in re.findall(r'<TR[^>]*>(.*?)</TR>',s,flags=re.S|re.I):
    tds=re.findall(r'<TD[^>]*>(.*?)</TD>',tr,flags=re.S|re.I)
    m=re.search(r'HREF="\.\./course/(c\d+\.html)"',tr,flags=re.I)
    if not m or len(tds)<3: continue
    code=txt(tds[0]); title=txt(tds[1]); cells=[txt(t) for t in tds]
    curl=BASE+'/course/'+m.group(1)
    c,ts=fetch('bilkent',curl,'course_'+m.group(1))
    c2=re.sub(r'<style.*?</style>','',c,flags=re.S)
    t=txt(c2)
    # page text: "... EEE 501 Linear System Theory <desc> Credit units: 3 ECTS Credit units: 5. Bilkent University Main Page"
    desc=''; cr=''
    mm=re.search(re.escape(code)+r'\s+'+re.escape(title)+r'\s*(.*?)\s*(Credit units:.*?)\s*Bilkent University Main Page',t,flags=re.S)
    if mm: desc=mm.group(1); cr=mm.group(2)
    else:
        mm=re.search(r'(Credit units:.*?)\s*Bilkent University Main Page',t)
        cr=mm.group(1) if mm else ''
        print('desc-parse-fail',code)
    if not cr: cr='list: '+' | '.join(cells[2:])
    n=int(re.search(r'(\d{3})',code).group(1))
    level='UG' if n<500 else 'G'
    rows.append(dict(university='Bilkent University, Dept. of Electrical and Electronics Engineering',
        code=code,title=title,description=desc,level=level,
        level_rule='numbering convention (Bilkent EEE 1xx-4xx undergraduate, 5xx-6xx graduate; consistent with OAC programme pages d12.html where MS/PhD curricula list EEE 599/699 and graduate electives)',
        credits=cr,source_url=curl,retrieved_utc=ts))
write_rows('bilkent',rows)
