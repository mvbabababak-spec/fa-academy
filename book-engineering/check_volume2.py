"""Validate volume 2 structure, local illustrations, answer keys and MathML."""
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(); self.images=[]; self.math=0
    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))
        if tag == 'math': self.math += 1

books=[b for b in json.loads((ROOT/'data.json').read_text(encoding='utf8'))['books'] if b['id']=='art-science-intelligence-v2']
assert len(books)==1
book=books[0]
assert book.get('subtitle')=='یادگیری ماشین و شبکه‌های عصبی | جلد دوم: ۱۱ فصل'
assert book.get('author')=='Babak Moradvand'
chapters=book['chapters']; assert [c['num'] for c in chapters]==list(range(1,12))
ids=[]; parser=Inspector(); count=0
for c in chapters:
    ids.append(c['id']); assert c['sections']
    for s in c['sections']:
        ids.append(s['id']); assert s['html'].strip(); parser.feed(s['html']); count+=1
assert count==101 and len(set(ids))==len(ids)
assert len(parser.images)==11
for img in parser.images:
    src=img.get('src',''); assert img.get('alt','').strip() and src.startswith('assets/') and src.endswith('.webp') and (ROOT/src).is_file(),src
answers=list((ROOT/'book-engineering/answers').glob('*.md'))
for c in chapters:
    stem=Path(c['sections'][0]['file']).stem; p=ROOT/'book-engineering/answers'/f'{stem}-fa.md'; assert p.is_file() and p.read_text(encoding='utf8').strip(),p
assert parser.math>=10
print(f'PASS volume 2: {len(chapters)} chapters, {count} sections, {len(parser.images)} WebP images with alt, 11 answer keys, {parser.math} MathML blocks')
