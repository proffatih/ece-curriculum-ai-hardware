"""Headless Chrome fetch that mirrors catv2.fetch logging."""
import os,subprocess,time,sys
sys.path.insert(0,'raw/_scripts')
from catv2 import RAW, now_utc
def hfetch(slug,url,fname,budget=15000,sleep=1.5,use_cache=True):
    d=os.path.join(RAW,slug); p=os.path.join(d,fname); os.makedirs(os.path.dirname(p),exist_ok=True)
    if use_cache and os.path.exists(p) and os.path.getsize(p)>2000:
        import datetime
        return open(p).read(), datetime.datetime.fromtimestamp(os.path.getmtime(p),datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    out=subprocess.run(['timeout','120','google-chrome','--headless','--disable-gpu',f'--virtual-time-budget={budget}','--dump-dom',url],capture_output=True)
    open(p,'wb').write(out.stdout); ts=now_utc()
    with open(os.path.join(d,'_fetch_log.tsv'),'a') as f: f.write(f'{ts}\theadless-rc{out.returncode}\t{url}\t{fname}\n')
    time.sleep(sleep)
    return out.stdout.decode('utf-8','replace'), ts
