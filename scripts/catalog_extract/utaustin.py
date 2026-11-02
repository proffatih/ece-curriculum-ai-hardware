import sys,re,html; sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, write_rows, clean
U='https://catalog.utexas.edu/general-information/coursesatoz/ece/'
t,ts=fetch('utaustin',U,'ug_ece.html')
fetch('utaustin','https://catalog.utexas.edu/general-information/academic-policies-and-procedures/credit-value-and-course-numbers/','course_numbers_rule.html')
RULEBASE=('UT Austin 2026-2027 General Information Catalog, "Credit Value and Course Numbers": "the second and third digits of the course number indicate the rank of the course; if they are 01 through 19, the course is of lower-division rank; if 20 through 79, of upper-division rank; and if 80 through 99, of graduate rank" '
          '(catalog.utexas.edu/general-information/academic-policies-and-procedures/credit-value-and-course-numbers/). Course appears under the "{sec}" heading of the ECE Courses A to Z page.')
def txt(s): return re.sub(r'\s+([.,;:])',r'\1',clean(html.unescape(re.sub(r'<[^>]+>',' ',s))))
i=t.find('id="ececourses"'); j=t.find('<!--end content-container',i); body=t[i:j]
rows=[]; sec=None
for m in re.finditer(r'<h4 class="coursedivider">(.*?)</h4>|<h5>(.*?)</h5>(.*?)(?=<h5>|<h4|$)',body,re.S):
    if m.group(1): sec=txt(m.group(1)); continue
    head=txt(m.group(2)).rstrip('.')
    mm=re.match(r'(ECE\s+\S+?)\.\s+(.*)',head)
    code=clean(mm.group(1)); title=mm.group(2)
    desc=txt(m.group(3))
    num=re.match(r'ECE\s+(\w)(\d\d)',code); rank=int(num.group(2))
    lev_num='UG' if rank<80 else 'G'
    lev_sec={'Lower-Division Courses':'UG','Upper-Division Courses':'UG','Graduate Courses':'G'}[sec]
    assert lev_num==lev_sec,(code,sec)
    cr='' if num.group(1)=='X' else num.group(1)
    rows.append(dict(university='University of Texas at Austin',code=code,title=title,description=desc,level=lev_sec,level_rule=RULEBASE.format(sec=sec),credits=cr,source_url=U,retrieved_utc=ts))
write_rows('utaustin',rows)
