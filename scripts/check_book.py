#!/usr/bin/env python3
"""Check source citations and rendered local links, fragments, scripts, and images."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import re,sys
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'outputs/site'
errors=[]
source='\n'.join(p.read_text() for p in ROOT.glob('*.qmd'))
bib='\n'.join(p.read_text() for p in (ROOT/'assets').glob('refs-*.bib'))
keys=re.findall(r'@\w+\s*\{\s*([^,]+),',bib)
for key,n in Counter(keys).items():
    if n>1: errors.append('Duplicate bibliography key: '+key)
for key in set(re.findall(r'@((?:f|c|m|s)_[\w-]+)',source)):
    if key not in keys: errors.append('Missing citation: '+key)
labels=re.findall(r'\{#((?:eq|sec|fig|tbl)-[\w-]+)',source)
for label,n in Counter(labels).items():
    if n>1: errors.append('Duplicate source label: '+label)
for label in set(re.findall(r'@((?:eq|sec|fig|tbl)-[\w-]+)',source)):
    if label not in labels: errors.append('Missing source reference: '+label)
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.ids=set(); self.links=[]; self.math=0; self.cites=0
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='a' and 'href'in a:self.links.append(a['href'])
        if tag in ['img','script'] and 'src'in a:self.links.append(a['src'])
        if tag=='link' and 'href'in a:self.links.append(a['href'])
        if 'math' in a.get('class','').split():self.math+=1
        if 'citation' in a.get('class','').split():self.cites+=1
pages={p.resolve():Page(p.read_text()) for p in SITE.glob('*.html')}
if len(pages)<17:errors.append(f'Expected at least 17 HTML pages, found {len(pages)}')
for p,obj in pages.items():
    raw=p.read_text()
    if 'quarto-unresolved-ref' in raw or re.search(r'<strong>\?@',raw):errors.append('Unresolved reference in '+p.name)
    for link in obj.links:
        u=urlsplit(link)
        if u.scheme or u.netloc or not(u.path or u.fragment):continue
        if u.path.startswith('/'):
            # Project-relative canonical links include the GitHub Pages repository prefix.
            path=u.path.removeprefix('/quantum-measurement-textbook/')
            target=SITE/path.lstrip('/')
        else:target=p.parent/unquote(u.path) if u.path else p
        if target.is_dir():target=target/'index.html'
        target=target.resolve()
        if not target.exists():errors.append(f'{p.name}: missing {link}')
        elif u.fragment and target.suffix=='.html':
            page=pages.get(target)
            if page and unquote(u.fragment) not in page.ids:
                errors.append(f'{p.name}: missing anchor {link}')
# Numeric labels must agree with the single global reference list.
reftext=(SITE/'references.html').read_text() if (SITE/'references.html').exists() else ''
refnums=dict(re.findall(r'id="ref-([^"]+)"[^>]*>\s*<div class="csl-left-margin">\[(\d+)\]',reftext))
for p in pages:
    for key,num in re.findall(r'href="[^"#]*#ref-([^"]+)" role="doc-biblioref">(\d+)</a>',p.read_text()):
        if refnums.get(key)!=num:errors.append(f'{p.name}: inconsistent numeric citation {key}')
pdf=SITE/'quantum-measurement.pdf'
if not pdf.exists() or pdf.stat().st_size<10000:errors.append('Missing combined PDF')
print(f'{len(pages)} HTML pages, {len(keys)} bibliography entries, {len(labels)} source labels, {sum(p.math for p in pages.values())} math spans, {sum(p.cites for p in pages.values())} citation spans')
if errors:
    print('\n'.join(sorted(set(errors))));sys.exit(1)
print('PASS: source citations, unique labels, local navigation, anchors, images, scripts, styles, and PDF.')
