"""Insert the authored chapter in the existing app data, preserving other books.
Run from the repository root with Python 3 and mistune 3 installed.
"""
import json
from pathlib import Path
import re
import mistune

root = Path(__file__).resolve().parent.parent
chapter = root / 'book-engineering/chapters/01-intelligence.md'
text = chapter.read_text(encoding='utf-8')
parts = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
assert len(parts) == 23, f'Expected 11 sections, got {(len(parts)-1)//2}'
render = mistune.create_markdown(plugins=['table'])
sections = []
for n in range(1, len(parts), 2):
    title = parts[n].strip()
    content = parts[n + 1]
    if n == 1:
        content = parts[0] + '\n## ' + title + '\n' + content
    else:
        content = '## ' + title + '\n' + content
    sections.append({'id': f'art-science-v1-ch01-s{(n+1)//2:02}', 'title': title,
                     'file': 'book-engineering/chapters/01-intelligence.md', 'html': render(content)})
path = root / 'data.json'
data = json.loads(path.read_text(encoding='utf-8'))
book = {'id': 'art-science-intelligence-v1', 'title': 'هنر و علم ساخت هوش — جلد اول',
        'subtitle': 'از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل برنامه‌ریزی‌شده · فصل ۱ منتشر شده',
        'author': 'Babak & Ai', 'cover': 'assets/images/art-science-cover.svg',
        'chapters': [{'num': 1, 'id': 'art-science-v1-ch01', 'title': 'هوش چیست؟ از انسان تا ماشین', 'icon': '✦', 'sections': sections}]}
books = data['books']
indices = [i for i, item in enumerate(books) if item['id'] == book['id']]
assert len(indices) <= 1
if indices:
    books[indices[0]] = book
else:
    books.insert(0, book)
path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print(f'Updated {book["id"]}: {len(sections)} sections')
