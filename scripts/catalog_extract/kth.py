import sys, re, json, html, urllib.parse
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows, clean
DEPTS=['JJ','JJN','JJG','JJF','JRL','JRO','JRQ']
LV={'First cycle':('UG','KTH utbildningstyp "First cycle" (grundnivå) => UG'),
    'Second cycle':('G','KTH utbildningstyp "Second cycle" (avancerad nivå) => G'),
    'Third cycle':('G','KTH utbildningstyp "Third cycle" (forskarnivå, PhD) => G')}
def txt(s): return clean(html.unescape(re.sub(r'<[^>]+>',' ',s)))
def store(t):
    return json.loads(urllib.parse.unquote(re.search(r'__compressedApplicationStore__ = "([^"]+)"',t).group(1)))
rows=[]; seen=set()
for dp in DEPTS:
    url=f'https://www.kth.se/student/kurser/org/{dp}?l=en'
    t,ts=fetch('kth',url,f'org_{dp}_en.html')
    d=store(t); dname=d.get('departmentName')
    print(dp,dname,len(d['departmentCourses']))
    for c in d['departmentCourses']:
        code=c['kod']
        if code in seen: continue
        seen.add(code)
        lvl,rule=LV.get(c.get('utbildningstyp'),('unknown',f'KTH utbildningstyp "{c.get("utbildningstyp")}" not mapped => unknown'))
        curl=f'https://www.kth.se/student/kurser/kurs/{code}?l=en'
        desc=''; cts=ts
        try:
            p,cts=fetch('kth',curl,f'kurs_{code}_en.html',sleep=1.0)
            parts=[]
            for h in ['Course contents','Intended learning outcomes']:
                m=re.search(r'<h3>'+h+r'<sup>.*?</sup></h3>(.*?)(?=<h3|<h2|</section|<div id=)',p,re.S)
                if m: parts.append(txt(m.group(1)))
            desc=' '.join(parts)
        except Exception as e: print('ERR',code,e)
        rows.append(dict(university='KTH Royal Institute of Technology',code=code,title=c['benamning'],description=desc,
             level=lvl,level_rule=rule+f'; dept {dp} {dname}',credits=c.get('omfattning',''),
             source_url=curl if desc else url,retrieved_utc=cts if desc else ts))
write_rows('kth',rows)
