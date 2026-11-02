import sys,re,html; sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, write_rows, clean
import xml.etree.ElementTree as ET
U="https://explorecourses.stanford.edu/search?view=xml-20140630&filter-coursestatus-Active=on&q=EE&filter-departmentcode-EE=on&academicYear=&page=0"
t,ts=fetch('stanford',U,'ec_EE_page0.xml')
RULE=('Stanford ExploreCourses XML field administrativeInformation/academicCareer (UG -> UG, GR -> G), academic year {y}. '
      'Note: Stanford numbering 100-299 courses are frequently open to both undergraduates and graduates; this is not encoded here (single career per course record).')
r=ET.fromstring(t.encode())
rows=[]
for c in r.iter('course'):
    if c.findtext('subject')!='EE': continue
    car=c.findtext('administrativeInformation/academicCareer')
    lev={'UG':'UG','GR':'G'}.get(car,'unknown')
    umin,umax=c.findtext('unitsMin'),c.findtext('unitsMax')
    cr=umin if umin==umax else f'{umin}-{umax}'
    rows.append(dict(university='Stanford University',code='EE '+c.findtext('code'),title=html.unescape(c.findtext('title') or ''),
        description=html.unescape(c.findtext('description') or ''),level=lev,level_rule=RULE.format(y=c.findtext('year'))+f' [academicCareer={car}]',
        credits=cr+' units',source_url=U,retrieved_utc=ts))
write_rows('stanford',rows)
