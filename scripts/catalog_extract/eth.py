import sys, re, html
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows, clean
B='https://www.vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebot.view'
SECT={'Electrical Engineering and Information Technology Bachelor':('UG','BSc'),
      'Electrical Engineering and Information Technology Master':('G','MSc'),
      'Doctorate Information Technology and Electrical Engineering':('G','Doctorate')}
def txt(s): return clean(html.unescape(re.sub(r'<br\s*/?>',' ',re.sub(r'<(?!br)[^>]+>',' ',s))).replace('<br />',' '))
def txt(s):
    s=re.sub(r'<[^>]+>',' ',s); return clean(html.unescape(s))
import requests
from catv2 import UA
_s=requests.Session(); _s.headers.update(UA)
try: _s.get('https://www.vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebotPre.view?lang=en',timeout=60)
except Exception as e: print(e)
CK=_s.cookies.get_dict(); print('cookies',CK)
found={}  # code -> dict
for sem in ['2025W','2026S']:
    f,ts=fetch('eth',f'https://www.vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebotPre.view?lang=en&semkez={sem}',f'form_{sem}.html',cookies=CK)
    m=re.search(r'<select[^>]*name="studiengangAbschnittId".*?</select>',f,re.S)
    opts={html.unescape(n).strip():v for v,n in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)',m.group(0))}
    for sname,(lvl,tag) in SECT.items():
        sid=opts.get(sname); print(sem,sname,sid)
        if not sid: continue
        url=(f'{B}?lerneinheitscode=&deptId=&famname=&unterbereichAbschnittId=&seite=0&strukturAus=on&lerneinheitstitel=&rufname=&kpRange=0,999'
             f'&lehrsprache=&bereichAbschnittId=&semkez={sem}&studiengangAbschnittId={sid}&studiengangTyp=&ansicht=2&lang=en&katalogdaten=&wahlinfo=')
        t,ts=fetch('eth',url,f'catalog_{sem}_{tag}.html',sleep=2)
        parts=re.split(r'<tr><td class="border-no" style="border-top: 1px solid #ccc"><b>',t)[1:]
        print('  n',len(parts))
        for p in parts:
            code=p.split('</b>')[0].strip()
            m=re.search(r'<a href="(/Vorlesungsverzeichnis/lerneinheit\.view\?[^"]+)">(.*?)</a>',p)
            title=txt(m.group(2)) if m else ''
            lurl='https://www.vvz.ethz.ch'+html.unescape(m.group(1)) if m else url
            cr=re.search(r'<td>([\d.]+)&nbsp;credits</td>',p)
            fields={}
            for k,v in re.findall(r'<tr><td class="border-no">([^<]+)</td><td colspan="5">(.*?)</td></tr>',p,re.S):
                fields[k.strip()]=txt(v)
            desc=' '.join(fields[k] for k in ['Abstract','Content'] if fields.get(k))
            rec=found.setdefault(code,dict(code=code,title=title,desc='',credits='',levels=set(),tags=set(),sems=set(),url=lurl,ts=ts,listurl=url))
            if len(desc)>len(rec['desc']): rec['desc']=desc
            if cr: rec['credits']=cr.group(1)+' ECTS'
            rec['levels'].add(lvl); rec['tags'].add(tag); rec['sems'].add(sem)
rows=[]
for c,r in found.items():
    lv='UG/G' if r['levels']=={'UG','G'} else next(iter(r['levels']))
    rule=('ETH VVZ programme section(s) '+'+'.join(sorted(r['tags']))+' ('+','.join(sorted(r['sems']))+'); BSc EEIT section=>UG, MSc EEIT/Doctorate ITET section=>G; listed in both=>UG/G')
    rows.append(dict(university='ETH Zurich',code=c,title=r['title'],description=r['desc'],level=lv,level_rule=rule,credits=r['credits'],source_url=r['url'],retrieved_utc=r['ts']))
write_rows('eth',rows)
