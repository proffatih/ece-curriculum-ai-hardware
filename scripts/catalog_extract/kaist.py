"""KAIST School of EE: Undergraduate and Graduate 'Subject Lists' (ee.kaist.ac.kr/en/under-curr-list, /en/graduate-curr-list), paginated ?page=N.
Level: listed on Undergraduate Subject List -> UG; Graduate Subject List -> G; both -> UG/G."""
import sys, re, html, glob, os
sys.path.insert(0, 'raw/_scripts')
from catv2 import write_rows, RAW
D=os.path.join(RAW,'kaist')
log={}
for line in open(os.path.join(D,'_fetch_log.tsv')):
    ts,st,u,fn=line.rstrip('\n').split('\t'); log[fn]=(ts,u)
recs={}; dup=[]
for kind,lv in [('under','UG'),('graduate','G')]:
    tot=0
    for p in sorted(glob.glob(f'{D}/{kind}_p*.html')):
        fn=os.path.basename(p); ts,u=log[fn]
        t=open(p,encoding='utf-8',errors='replace').read()
        t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
        L=[l.strip() for l in html.unescape(re.sub(r'<[^>]+>','\n',t)).split('\n') if l.strip()]
        for i,l in enumerate(L):
            if not re.fullmatch(r'EE\.\d{5}(\([0-9A-Z]+\))?[A-Z]?',l): continue
            if re.search(r'\(EE\.',l): continue
            back=L[max(0,i-3):i]
            if not any(re.fullmatch(r'[\d.]+credits',x) or x in ('Required','Elective','Research','Seminar','졸업작품') for x in back): continue
            cr=L[i-1] if re.fullmatch(r'[\d.]+credits',L[i-1]) else ''
            cls=L[i-2] if cr else L[i-1]
            div=L[i-3] if cr else L[i-2]
            j=i+2; desc=[]
            while j<len(L) and L[j]!='Recommend': desc.append(L[j]); j+=1
            code,title=l,L[i+1]; tot+=1
            if code in recs:
                if recs[code]['level']!=lv:
                    recs[code]['level']='UG/G'; recs[code]['source_url']+=' ; '+u
                    continue
                if re.sub(r'\s','',recs[code]['title'])==re.sub(r'\s','',title): dup.append((code,title)); continue
                code_key=code+'|'+title
            else: code_key=code
            if code_key in recs: continue
            recs[code_key]=dict(university='Korea Advanced Institute of Science and Technology',code=code,title=title,description=' '.join(desc),
                level=lv,credits=cr.replace('credits',' credits'),source_url=u,retrieved_utc=ts,division=div,classification=cls)
    print(kind,'items',tot)
LR={'UG':'Listed on KAIST EE Undergraduate Subject Lists (https://ee.kaist.ac.kr/en/under-curr-list/)',
    'G':'Listed on KAIST EE Graduate Subject Lists (https://ee.kaist.ac.kr/en/graduate-curr-list/)',
    'UG/G':'Listed on both KAIST EE Undergraduate and Graduate Subject Lists'}
rows=[]
for r in recs.values():
    r['level_rule']=LR[r['level']]; rows.append(r)
import collections
print(collections.Counter((r['code'][3],r['level']) for r in rows))
print(collections.Counter(r['classification'] for r in rows))
print('dups skipped',dup)
print('no-credit',[r['code'] for r in rows if not r['credits']])
write_rows('kaist',rows)
