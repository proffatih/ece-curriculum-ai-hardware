import sys,re; sys.path.insert(0,'raw/_scripts')
from catv2 import fetch
t=open('raw/cmu/courses_ece_root.html').read()
hrefs=sorted(set(h for h in re.findall(r'<td><a href="([^"]+)">',t) if not re.fullmatch(r'\d{5}',h)))
print(len(hrefs),flush=True)
for h in hrefs:
    try: fetch('cmu','https://courses.ece.cmu.edu/'+h,'pages/course_'+h+'.html',sleep=1.2)
    except Exception as e: print(h,e,flush=True)
print('done')
