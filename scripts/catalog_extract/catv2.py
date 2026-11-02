"""Shared helpers for EDU01 catalogue v2 extraction.
Usage in a per-programme script:
    import sys; sys.path.insert(0, 'raw/_scripts')
    from catv2 import fetch, write_rows, RAW
"""
import csv, os, time, datetime, hashlib, re
import requests

RAW = 'raw'
OUT = 'data/catalog_v2'
COLS = ['university','code','title','description','level','level_rule','credits','source_url','retrieved_utc']
LEVELS = {'UG','G','UG/G','unknown'}
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 (academic curriculum research; fatih.gul@erdogan.edu.tr)'}
_FETCH_LOG = {}

def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def fetch(slug, url, fname=None, sleep=1.5, binary=False, use_cache=True, **kw):
    """GET url, save raw to RAW/slug/fname, return (text_or_bytes, retrieved_utc). Cached on disk."""
    d = os.path.join(RAW, slug); os.makedirs(d, exist_ok=True)
    if fname is None:
        fname = re.sub(r'[^A-Za-z0-9._-]+', '_', url.split('://',1)[-1])[:150]
    p = os.path.join(d, fname)
    if use_cache and os.path.exists(p) and os.path.getsize(p) > 0:
        ts = _FETCH_LOG.get(p) or datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        data = open(p,'rb').read()
        return (data if binary else data.decode('utf-8','replace')), ts
    headers = dict(UA); headers.update(kw.pop('headers', {}))
    r = requests.get(url, headers=headers, timeout=60, **kw)
    time.sleep(sleep)
    r.raise_for_status()
    open(p,'wb').write(r.content)
    ts = now_utc(); _FETCH_LOG[p] = ts
    with open(os.path.join(d, '_fetch_log.tsv'), 'a') as f:
        f.write(f'{ts}\t{r.status_code}\t{url}\t{fname}\n')
    return (r.content if binary else r.content.decode(r.encoding or r.apparent_encoding or 'utf-8', 'replace')), ts

def clean(s):
    if s is None: return ''
    return re.sub(r'\s+', ' ', str(s)).strip()

def write_rows(slug, rows):
    """rows: list of dicts with COLS keys. Validates and writes OUT/slug.csv. Dedups on (code,title,level)."""
    os.makedirs(OUT, exist_ok=True)
    seen=set(); out=[]
    for r in rows:
        r = {c: clean(r.get(c,'')) for c in COLS}
        assert r['level'] in LEVELS, (r['code'], r['level'])
        assert r['code'] or r['title'], r
        assert r['source_url'] and r['retrieved_utc'] and r['level_rule'], r
        k=(r['code'], r['title'], r['level'])
        if k in seen: continue
        seen.add(k); out.append(r)
    p=os.path.join(OUT, f'{slug}.csv')
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(out)
    from collections import Counter
    c=Counter(r['level'] for r in out)
    nd=sum(1 for r in out if r['description'])
    print(f'{slug}: {len(out)} rows, levels={dict(c)}, with_desc={nd}')
    return out
