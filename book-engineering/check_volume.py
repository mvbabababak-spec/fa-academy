"""Structural checks of volume 1, its local WebP images, and generated MathML."""
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.math = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'math':
            self.math += 1

book = next(b for b in json.loads((ROOT/'data.json').read_text(encoding='utf-8'))['books'] if b['id'] == 'art-science-intelligence-v1')
assert book.get('subtitle') == 'از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل'
assert book.get('author') == 'Babak Moradvand'
assert [c['num'] for c in book['chapters']] == list(range(1, 22))
ids = []
parser = Images()
for chapter in book['chapters']:
    ids.append(chapter['id'])
    for section in chapter['sections']:
        ids.append(section['id'])
        assert section['html'].strip(), section['id']
        parser.feed(section['html'])
assert len(ids) == len(set(ids))
for image in parser.images:
    src = image.get('src', '')
    assert image.get('alt', '').strip(), src
    assert src.startswith('assets/') and src.endswith('.webp'), src
    assert (ROOT/src).is_file(), src
assert parser.math >= 6
print(f"PASS {len(book['chapters'])} chapters, {len(ids)-len(book['chapters'])} sections, {len(parser.images)} local WebP images with alt, {parser.math} MathML blocks")
