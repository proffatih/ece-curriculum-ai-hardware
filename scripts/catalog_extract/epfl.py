import sys, re, html
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch, write_rows, clean
BASE='https://edu.epfl.ch'
PLANS=[('propedeutics','https://edu.epfl.ch/studyplan/en/propedeutics/electrical-and-electronics-engineering/','propedeutics_studyplan.html','UG','EPFL propaedeutic cycle (Bachelor yr1) study plan => UG'),
       ('bachelor','https://edu.epfl.ch/studyplan/en/bachelor/electrical-and-electronics-engineering/','bachelor_studyplan.html','UG','EPFL Bachelor cycle study plan (Bachelor 3-6) => UG'),
       ('master','https://edu.epfl.ch/studyplan/en/master/electrical-and-electronics-engineering/','master_studyplan.html','G','EPFL Master study plan (Master cycle) => G')]
def txt(s): return clean(html.unescape(re.sub(r'<[^>]+>',' ',s)))
rows=[]; fr_codes=[]
for name,url,fn,lvl,rule in PLANS:
    t,ts=fetch('epfl',url,fn)
    blocks=t.split('class="line-down"')[1:]
    for b in blocks:
        m=re.search(r'class="cours-name"><a href="([^"]+)">(.*?)</a>',b)
        if not m: continue
        href,title=m.group(1),txt(m.group(2))
        info=re.search(r'class="cours-info">(.*?)</div>',b)
        code=txt(info.group(1)).split('/')[0].strip() if info else ''
        cr=re.search(r'class="credit-time">(.*?)</div>',b)
        credits=txt(cr.group(1)) if cr else ''
        cburl=BASE+href
        slugf='cb_'+re.sub(r'[^A-Za-z0-9._-]+','_',href.split('/coursebook/')[-1])+'.html'
        desc=''; cts=ts
        try:
            c,cts=fetch('epfl',cburl,slugf,sleep=1.0)
            parts=[]
            for h in ['Summary','Résumé','Zusammenfassung','Content','Contenu','Inhalt']:
                mm=re.search(r'<h2 class="h5">'+h+r'</h2>(.*?)</div>\s*(?:<button|</div>)',c,re.S)
                if mm: parts.append(txt(mm.group(1)))
            desc=' '.join(parts)
            if re.search(r'<h2 class="h5">(Résumé|Contenu)</h2>',c): fr_codes.append(code)
        except Exception as e:
            print('ERR',cburl,e)
        rows.append(dict(university='EPFL',code=code,title=title,description=desc,level=lvl,level_rule=rule,
             credits=credits+' ECTS' if credits else '',source_url=cburl if desc else url,retrieved_utc=cts if desc else ts))
write_rows('epfl',rows); print('french-language descriptions:',len(fr_codes))
