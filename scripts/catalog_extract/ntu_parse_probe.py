import os,re,html,glob,collections
D='raw/ntu'
def parse(p):
    t=open(p,encoding='utf-8',errors='replace').read()
    out=[]
    for tb in re.findall(r'<table\s*>(.*?)</table>', t, re.S|re.I):
        m=re.search(r'COLOR=#0000FF>([A-Z]{2,3}\d{4}[A-Z]?)</FONT>.*?COLOR=#0000FF>(.*?)</FONT>.*?COLOR=#0000FF>\s*([\d.]+)\s*AU',tb,re.S)
        if not m: continue
        dm=re.search(r'<TD WIDTH="650" colspan="3"><FONT SIZE=2>(.*?)</TD>',tb,re.S|re.I)
        desc=html.unescape(re.sub(r'<[^>]+>',' ',dm.group(1))) if dm else ''
        out.append((m.group(1),html.unescape(m.group(2)).strip(),m.group(3),re.sub(r'\s+',' ',desc).strip()))
    return out
c=collections.Counter(); codes=collections.defaultdict(set)
for p in sorted(glob.glob(D+'/20*.html')):
    for code,ti,au,de in parse(p):
        pre=re.match(r'[A-Z]+',code).group(); c[pre]+=1; codes[pre].add(code)
print({k:len(v) for k,v in codes.items()})
print(sorted(codes['EE'])[:400]); print(sorted(codes.get('IM',[]))); print(sorted(codes.get('IE',[])))
