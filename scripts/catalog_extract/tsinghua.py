"""Tsinghua Dept. of Electronic Engineering (电子工程系).
UG: English 'Curriculum' page (4 tabs: basic/major/restricted/free) - rows kept only where the offering
    department column = 'Department of Electronic Engineering'.
G : Chinese page 研究生课程 (zsjx/yjs/yjskc.htm) - course names only (no codes/credits/descriptions), kept in Chinese."""
import sys,re,html
sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, clean, write_rows
from tsinghua_parse import parse_cur, CUR
U='Tsinghua University, Department of Electronic Engineering (电子工程系)'
rows=[]
o,ts=parse_cur()
CATN={'basic':'Basic Foundation','major':'Major Required','restricted':'Restricted Electives','free':'Free Electives'}
for cat,c in o:
    if len(c)<5 or c[2]!='Department of Electronic Engineering': continue
    code,title,dept,term,cr=c[:5]
    if code[:1] in '6789':
        lev='UG/G'; rule=('listed in the EE undergraduate curriculum (English Curriculum page, tab "'+CATN[cat]+'") AND code is in the 6/7/8-series '
            'that Tsinghua graduate training programmes use for graduate courses (seen in EEA 2024 graduate programme PDFs, eea_pdf_2/3.pdf); '
            'numbering convention inferred, not a published rule. Dept. Chinese UG page states electives include 本研贯通专业课程')
    else:
        lev='UG'; rule='listed in the EE undergraduate curriculum (English Curriculum page, tab "'+CATN[cat]+'"); classified by programme document'
    rows.append(dict(university=U,code=code,title=title,description='',level=lev,level_rule=rule,
        credits=cr+(' credits; term: '+term if term else ' credits'),source_url=CUR,retrieved_utc=ts))
# graduate page (Chinese only)
GU='https://www.ee.tsinghua.edu.cn/zsjx/yjs/yjskc.htm'
b,ts=fetch('tsinghua',GU,'ee_cn_zsjx_yjs_yjskc.htm',binary=True); s=b.decode('utf-8','replace')
s=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>','\n',s)); lines=[l.strip() for l in t.split('\n') if l.strip()]
i=next(k for k,l in enumerate(lines) if l.startswith('电子系以'))
grp=''
for l in lines[i+1:]:
    if l=='相关链接': break
    if re.match(r'^(\d\.|（\d）)',l): grp=l; continue
    rows.append(dict(university=U,code='',title=l,description='',level='G',
        level_rule='listed on department page 研究生课程 (graduate courses), group: '+grp+'; classified by programme document',
        credits='',source_url=GU,retrieved_utc=ts))
# Dedup graduate names listed in two groups
seen=set(); out=[]
for r in rows:
    k=(r['code'],r['title'],r['level'])
    if k in seen: continue
    seen.add(k); out.append(r)
write_rows('tsinghua',out)
