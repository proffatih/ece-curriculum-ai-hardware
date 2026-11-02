import sys, os, re, json, html, time, requests
sys.path.insert(0, 'raw/_scripts')
from catv2 import write_rows, clean, RAW, UA, now_utc
D=os.path.join(RAW,'tudelft'); os.makedirs(D,exist_ok=True)
API='https://curriculum.tudelft.nl/publisher/api/v0/courses/items/search'
YEAR=sys.argv[1] if len(sys.argv)>1 else '2026-2027'
items=[]; off=0; tsmap={}
while True:
    fn=os.path.join(D,f'search_{YEAR}_off{off:05d}.json')
    if os.path.exists(fn):
        d=json.load(open(fn)); ts=open(fn+'.ts').read().strip()
    else:
        r=requests.post(API,params={'size':100,'offset':off},json={'query':'','filters':{'jaar':[YEAR]},'language':'en'},
                        headers={**UA,'Accept':'application/json'},timeout=120)
        time.sleep(1.5); r.raise_for_status(); d=r.json(); ts=now_utc()
        json.dump(d,open(fn,'w')); open(fn+'.ts','w').write(ts)
        with open(os.path.join(D,'_fetch_log.tsv'),'a') as f: f.write(f'{ts}\t{r.status_code}\tPOST {API}?size=100&offset={off} body={{"query":"","filters":{{"jaar":["{YEAR}"]}},"language":"en"}}\t{os.path.basename(fn)}\n')
    for x in d['data']: items.append((x,ts))
    off+=100
    if off>=d['meta']['total']: break
print('total items',len(items))
def txt(s): return clean(html.unescape(re.sub(r'<[^>]+>',' ',s or '')))
def en(v):
    if isinstance(v,dict): return v.get('en') or v.get('nl') or ''
    return v or ''
progs={}
for x,ts in items:
    for n in x['attributes']['data'].get('opleidingen_namen') or []: progs[n]=progs.get(n,0)+1
print({k:v for k,v in progs.items() if 'lectric' in k})
TARGET={'BSc Electrical Engineering':'UG','MSc Electrical Engineering':'G'}
rows=[]
for x,ts in items:
    a=x['attributes']['data']
    names=set(a.get('opleidingen_namen') or [])
    lv={TARGET[n] for n in names if n in TARGET}
    if not lv: continue
    level='UG/G' if lv=={'UG','G'} else lv.pop()
    nm=en(a.get('course_name_2')) or a['name']
    desc=txt(en(a.get('vakbeschrijving')))
    lo=txt(en(a.get('leerdoelen')))
    if lo: desc=(desc+' Learning objectives: '+lo).strip()
    cr=en(a.get('cr_level'))
    rows.append(dict(university='Delft University of Technology',code=a.get('code',''),title=nm,description=desc,level=level,
        level_rule=f'TU Delft study guide {YEAR}: listed in programme(s) '+'; '.join(sorted(n for n in names if n in TARGET))+' (BSc EE=>UG, MSc EE=>G, both=>UG/G); catalogue cr_level='+','.join(cr if isinstance(cr,list) else [cr]),
        credits=f"{a.get('studiepunten_ects')} ECTS" if a.get('studiepunten_ects') is not None else '',
        source_url=f"https://studiegids.tudelft.nl/courses/study-guide/modules/{x['id']}",retrieved_utc=ts))
write_rows('tudelft',rows)
