"""Add chapter 2 without replacing other chapters/books. Requires mistune 3.
Run from the repository root: python book-engineering/build_chapter.py
"""
import json
from pathlib import Path
import re
import mistune

root = Path(__file__).resolve().parent.parent
chapter = root / 'book-engineering/chapters/02-ai-families.md'
text = chapter.read_text(encoding='utf-8')
parts = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
assert len(parts) == 27, f'Expected 13 sections, got {(len(parts)-1)//2}'
render = mistune.create_markdown(plugins=['table'])
sections = []
for n in range(1, len(parts), 2):
    title = parts[n].strip()
    content = parts[n + 1]
    content = (parts[0] + '\n' if n == 1 else '') + '## ' + title + '\n' + content
    sections.append({'id': f'art-science-v1-ch02-s{(n+1)//2:02}', 'title': title,
                     'file': 'book-engineering/chapters/02-ai-families.md', 'html': render(content)})
path = root / 'data.json'
data = json.loads(path.read_text(encoding='utf-8'))
books = [b for b in data['books'] if b['id'] == 'art-science-intelligence-v1']
assert len(books) == 1
book = books[0]
book['subtitle'] = 'از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل برنامه‌ریزی‌شده · فصل‌های ۱ و ۲ منتشر شده'
book['cover'] = 'assets/images/art-science-cover.webp'
new = {'num': 2, 'id': 'art-science-v1-ch02', 'title': 'خانواده هوش مصنوعی: از الگوریتم تا مدل زبانی', 'icon': '◈', 'sections': sections}
existing = [i for i,c in enumerate(book['chapters']) if c['id'] == new['id']]
assert len(existing) <= 1
if existing:
    book['chapters'][existing[0]] = new
else:
    book['chapters'].append(new)
book['chapters'].sort(key=lambda c:c['num'])
path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print('Chapter 2:', len(sections), 'sections; total published chapters:',len(book['chapters']))
