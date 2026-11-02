import sys,re,html
sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, clean
URL='https://eee.metu.edu.tr/all-courses'
def get_list():
    s,ts=fetch('metu',URL,'eee_all-courses.html')
    rows=[]
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',s,flags=re.S):
        tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,flags=re.S)
        if len(tds)<2: continue
        href=re.search(r'href="([^"]+)"',tds[0])
        cells=[clean(html.unescape(re.sub(r'<[^>]+>',' ',t))) for t in tds]
        rows.append(dict(code=cells[0],title=cells[1],cells=cells,href=html.unescape(href.group(1)) if href else ''))
    return rows,ts
if __name__=='__main__':
    r,ts=get_list(); print(len(r),ts)
    for x in r: print(x['cells'],x['href'][-30:])
