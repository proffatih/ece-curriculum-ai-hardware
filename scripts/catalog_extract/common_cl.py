"""CourseLeaf courseblock helpers."""
import re, html
def txt(s):
    s = re.sub(r'<br\s*/?>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).replace(' ',' ').replace('\xa0',' ').strip()
def blocks(t):
    # split on courseblock divs
    parts = re.split(r'<div class="courseblock">', t)[1:]
    return parts
def cls(block, name):
    m = re.search(r'<(?:p|span|h\d|div)[^>]*class="%s[^"]*"[^>]*>(.*?)</(?:p|span|h\d|div)>' % re.escape(name), block, re.S)
    return m.group(1) if m else ''
