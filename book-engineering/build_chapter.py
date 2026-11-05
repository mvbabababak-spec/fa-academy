"""Publish chapter 3 into the existing app data. Requires mistune 3."""
import json
from pathlib import Path
import re
import mistune

root = Path(__file__).resolve().parent.parent
source = 'book-engineering/chapters/03-model-lifecycle.md'
text = (root / source).read_text(encoding='utf-8')
parts = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
assert len(parts) == 27, f'Expected 13 sections, got {(len(parts)-1)//2}'
render = mistune.create_markdown(plugins=['table'])
sections = []
for n in range(1, len(parts), 2):
    title = parts[n].strip()
    content = (parts[0] + '\n' if n == 1 else '') + '## ' + title + '\n' + parts[n+1]
    sections.append({'id': f'art-science-v1-ch03-s{(n+1)//2:02}', 'title': title,
                     'file': source, 'html': render(content)})
path = root / 'data.json'
data = json.loads(path.read_text(encoding='utf-8'))
books = [b for b in data['books'] if b['id'] == 'art-science-intelligence-v1']
assert len(books) == 1
book = books[0]
assert {c['num'] for c in book['chapters']} >= {1, 2}, 'Earlier chapters are required'
book['subtitle'] = 'از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل برنامه‌ریزی‌شده · فصل‌های ۱ تا ۳ منتشر شده'
chapter = {'num': 3, 'id': 'art-science-v1-ch03', 'title': 'چرخه حیات مدل: از داده تا استنتاج و بازخورد', 'icon': '◉', 'sections': sections}
indices = [i for i, c in enumerate(book['chapters']) if c['id'] == chapter['id']]
assert len(indices) <= 1
if indices:
    book['chapters'][indices[0]] = chapter
else:
    book['chapters'].append(chapter)
book['chapters'].sort(key=lambda c: c['num'])
path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print(f'Chapter 3: {len(sections)} sections; {len(book["chapters"])} chapters total')
