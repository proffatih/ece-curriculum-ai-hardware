import sys,re,html,os; sys.path.insert(0,'raw/_scripts')
from catv2 import write_rows, clean
from headless import hfetch
LIST='https://catalog.purdue.edu/content.php?catoid=19&navoid=25468&filter%5B27%5D=ECE&filter%5B29%5D=&filter%5Bkeyword%5D=&filter%5B32%5D=1&filter%5Bcpage%5D={p}&cur_cat_oid=19&expand={e}&search_database=Filter&filter%5Bexact_match%5D=1'
RULE=('Purdue 2026-2027 University Catalog, Courses page "Course Numbering Information": "10000-29999 Lower-division courses ... 30000-49999 Upper-division courses ... 50000-59999 Dual-level courses - may be scheduled by juniors, seniors and graduate students for graduate credits; 60000-69999 Graduate-level courses" '
      '(https://catalog.purdue.edu/content.php?catoid=19&navoid=25468). Mapping: 10000-49999=UG, 50000-59999=UG/G, 60000-69999=G.')
def txt(s): return re.sub(r'\s+([.,;:])',r'\1',clean(html.unescape(re.sub(r'<[^>]+>',' ',s))))
def lev(n):
    n=int(n)
    if n<50000: return 'UG'
    if n<60000: return 'UG/G'
    if n<70000: return 'G'
    return 'unknown'
rows=[]
for p in [1,2,3]:
    tl,_=hfetch('purdue',LIST.format(p=p,e=''),'ece_list_p1_headless.html' if p==1 else f'ece_list_p{p}_headless.html')
    coid={txt(n):c for c,n in re.findall(r'preview_course_nopop\.php\?catoid=19&(?:amp;)?coid=(\d+)[^>]*>(ECE[^<]+)<',tl)}
    te,ts=hfetch('purdue',LIST.format(p=p,e='1'),f'ece_list_expand_p{p}.html',budget=30000)
    for li in re.findall(r'<h3>(ECE.*?)</li>',te,re.S):
        h,rest=li.split('</h3>',1)
        head=txt(h); code,title=[clean(x) for x in head.split(' - ',1)]
        parts=rest.split('<hr>')
        main=txt(parts[1]) if len(parts)>1 else ''
        m=re.match(r'Credit Hours:\s*([\d.]+(?:\s*(?:to|or)\s*[\d.]+)?)\.?\s*(.*)',main,re.S)
        cr,desc=(m.group(1).rstrip('.'),m.group(2)) if m else ('',main)
        lo=''
        for x in parts[2:]:
            if 'Learning Outcomes' in x: lo=txt(x)
        if lo: desc=(desc+' '+lo).strip()
        c=coid.get(head)
        src=f'https://catalog.purdue.edu/preview_course_nopop.php?catoid=19&coid={c}' if c else LIST.format(p=p,e='1')
        num=re.search(r'(\d{5})',code).group(1)
        rows.append(dict(university='Purdue University',code=code,title=title,description=desc,level=lev(num),level_rule=RULE,credits=cr,source_url=src,retrieved_utc=ts))
print('no coid',sum('coid=' not in r['source_url'] for r in rows))
write_rows('purdue',rows)
