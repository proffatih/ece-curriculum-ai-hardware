import sys,re,html
sys.path.insert(0,'raw/_scripts')
from catv2 import fetch, clean
CUR='https://www.ee.tsinghua.edu.cn/en/Academics/Curriculum.htm'
def txt(h): return clean(html.unescape(re.sub(r'<[^>]+>',' ',h)))
def parse_cur():
    b,ts=fetch('tsinghua',CUR,'ee_en_Academics_Curriculum.htm',binary=True); s=b.decode('utf-8','replace')
    out=[]
    # split by tab containers
    parts=re.split(r'<div id="list-(\w+)" class="course-list-container[^"]*">',s)
    for i in range(1,len(parts),2):
        cat=parts[i]; body=parts[i+1]
        for it in re.findall(r'<div class="course-item">(.*?)</div>\s*</div>',body,flags=re.S):
            cols=[txt(c) for c in re.findall(r'<div class="[a-z-]+">(.*?)</div>',it+'</div>',flags=re.S)]
            out.append((cat,cols))
    return out,ts
if __name__=='__main__':
    from collections import Counter
    o,ts=parse_cur(); print(len(o),ts)
    print(Counter(c for c,_ in o))
    print(Counter((c,x[2]) for c,x in o).most_common(40))
    print(Counter((c,x[0][0]) for c,x in o if x))
    for c,x in o:
        if c=='restricted' and x[0][0] in '6789': print(x)
