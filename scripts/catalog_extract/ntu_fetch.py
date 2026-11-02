"""Fetch NTU 'Content of Courses' (wis.ntu.edu.sg AUS_SUBJ_CONT) for EEE-school programme lists via POST. Saves raw HTML."""
import sys, os, re, time, html
sys.path.insert(0, 'raw/_scripts')
from catv2 import RAW, UA, now_utc
import requests
D=os.path.join(RAW,'ntu'); os.makedirs(D,exist_ok=True)
URL='https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1'
main=open(os.path.join(D,'main.html')).read()
opts=re.findall(r'<option[^>]*value=([^>\s]+)>([^<]*)', main)
want=[(v,l.strip()) for v,l in opts if re.match(r'(EEE;|ENG;EEE;|EESJ;|IEM;|IEEC;|EEEC;|REP;EEE;|REP;IEM;|GLOAD;EEE;)', v)]
print(len(want), want)
SEMS=sys.argv[1:] or ['2025_1','2025_2','2025_S','2026_1']
for sem in SEMS:
    for v,l in want:
        fn=f"{sem}__{re.sub(r'[^A-Za-z0-9]+','_',v)}.html"; p=os.path.join(D,fn)
        if os.path.exists(p) and os.path.getsize(p)>0: continue
        a,s=sem.split('_')
        r=requests.post(URL, headers=UA, timeout=90, data={'acadsem':sem,'r_course_yr':v,'r_subj_code':'Enter Keywords or Course Code','boption':'CLoad','acad':a,'semester':s})
        time.sleep(1.5)
        ts=now_utc()
        open(p,'wb').write(r.content)
        with open(os.path.join(D,'_fetch_log.tsv'),'a') as f:
            f.write(f"{ts}\t{r.status_code}\tPOST {URL} acadsem={sem} r_course_yr={v} boption=CLoad\t{fn}\n")
        print(sem, v, r.status_code, len(r.content))
