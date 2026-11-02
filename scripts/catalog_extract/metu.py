"""METU EEE: course list from live dept page eee.metu.edu.tr/all-courses (catalog.metu.edu.tr times out
from this host); per-course description + 'Level of Study' from Internet Archive snapshots of the
catalog.metu.edu.tr course pages linked from that list."""
import sys,re,html,os,time,requests
sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, clean, write_rows, RAW
from metu_list import get_list, URL

def wb(code, href):
    fname=f'wayback_course_{code}.html'
    p=os.path.join(RAW,'metu',fname)
    if os.path.exists(p) and os.path.getsize(p)==0: return None,None,None
    if os.environ.get('METU_CACHE_ONLY') and not os.path.exists(p): return None,None,None
    wurl='https://web.archive.org/web/2026id_/'+href
    for attempt in range(4):
        try:
            b,ts=fetch('metu',wurl,fname,binary=True,sleep=3,headers={'User-Agent':'EDU01-curriculum-research/1.0 (academic catalogue study)'})
            break
        except requests.HTTPError as e:
            sc=e.response.status_code
            if sc==404: open(p,'wb').close(); return None,None,None
            print('  http',code,sc,flush=True)
            if sc in (429,500,502,503,504): time.sleep(180); continue
            return None,None,None
        except Exception as e:
            print('  exc',code,type(e).__name__,flush=True); time.sleep(15)
    else:
        return None,None,None
    return b.decode('iso-8859-9','replace'),ts,wurl

def parse(s):
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
    t=re.sub(r'<br\s*/?>','\n',t); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    d={}
    for k in ['Level of Study:','METU Credit (Theoretical-Laboratory hours/week):','ECTS Credit:','Course Code:']:
        if k in lines: d[k]=lines[lines.index(k)+1]
    if 'Course Content' in lines:
        i=lines.index('Course Content'); out=[]
        for l in lines[i+1:]:
            if l.startswith('Design:') or l.startswith('CC-IG') or l in ('Contact','FAQ'): break
            out.append(l)
        d['desc']=' '.join(out)
    # title line "EE201 CIRCUIT THEORY I"
    return d

rows=[]
lst,ts0=get_list()
for x in lst:
    c=x['cells']
    if c[0]=='Course Code' or not c[0]: continue
    code=c[0]; title=c[1]
    num=int(re.match(r'EE(\d+)',code).group(1)); n3=num if num<1000 else num//10
    desc=''; level=None; rule=''; src=URL; ts=ts0
    if x['href']:
        s,tsw,wurl=wb(code,x["href"]); print(code, bool(s), flush=True)
        if s:
            d=parse(s)
            desc=d.get('desc','')
            lv=d.get('Level of Study:','')
            if lv.lower().startswith('undergraduate'): level='UG'
            elif lv.lower().startswith('graduate'): level='G'
            if level: rule="METU catalogue course page field 'Level of Study' (Internet Archive snapshot of catalog.metu.edu.tr)"
            src=URL+' ; '+wurl
            pass
    if not level:
        level='UG' if n3<500 else 'G'
        rule='numbering convention (METU EE 1xx-4xx undergraduate, 5xx-7xx/4-digit 5xxx-7xxx graduate; consistent with catalogue Level of Study fields where captured)'
    cr = f'METU {c[2]} ({c[3]}-{c[4]}); ECTS {c[5]}' if len(c)>=6 and c[2] else ''
    rows.append(dict(university='Middle East Technical University (METU/ODTÜ), Dept. of Electrical and Electronics Engineering',
        code=code,title=title,description=desc,level=level,level_rule=rule,credits=cr,source_url=src,retrieved_utc=ts))
write_rows('metu',rows)
