import sys,re
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch
for kind,n in [('under',9),('graduate',15)]:
    p=1
    while True:
        u=f'https://ee.kaist.ac.kr/en/{kind}-curr-list/' + (f'?page={p}' if p>1 else '')
        t,ts=fetch('kaist',u,f'{kind}_p{p:02d}.html')
        codes=re.findall(r'EE\.\d{5}',t)
        print(kind,p,len(codes),ts)
        nxt=re.search(r'href="[^"]*\?page=%d"'%(p+1),t)
        if not codes or (not nxt and p>=n): break
        p+=1
        if p>40: break
