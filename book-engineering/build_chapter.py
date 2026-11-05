"""Insert chapters 20 and 21 without changing prior app content (mistune 3)."""
import json
from pathlib import Path
import re
import mistune

root = Path(__file__).resolve().parent.parent
path = root / 'data.json'
data = json.loads(path.read_text(encoding='utf-8'))
books = [b for b in data['books'] if b['id'] == 'art-science-intelligence-v1']
assert len(books) == 1
book = books[0]
assert {c['num'] for c in book['chapters']} >= set(range(1,20))
render = mistune.create_markdown(plugins=['table'])
for number, slug, title, icon, expected in [
    (20, '20-optimization', 'بهینه‌سازی، گرادیان‌کاهشی و پایداری عددی', '◈', 10),
    (21, '21-information-theory', 'نظریه اطلاعات: آنتروپی، آنتروپی متقاطع و KL', '▣', 10),
]:
    source = f'book-engineering/chapters/{slug}.md'
    text = (root / source).read_text(encoding='utf-8')
    parts = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
    assert (len(parts)-1)//2 == expected
    sections = []
    for n in range(1, len(parts), 2):
        title_section = parts[n].strip()
        content = (parts[0]+'\n' if n == 1 else '')+'## '+title_section+'\n'+parts[n+1]
        sections.append({'id': f'art-science-v1-ch{number:02}-s{(n+1)//2:02}',
                         'title': title_section, 'file': source, 'html': render(content)})
    chapter = {'num': number, 'id': f'art-science-v1-ch{number:02}', 'title': title,
               'icon': icon, 'sections': sections}
    indices = [i for i,c in enumerate(book['chapters']) if c['id']==chapter['id']]
    assert len(indices)<=1
    if indices:
        assert book['chapters'][indices[0]] == chapter, 'Chapter exists; refusing to replace it'
        print(f'Chapter {number} already present, unchanged')
    else:
        assert all(c['num'] != number for c in book['chapters']), 'Chapter number already exists'
        book['chapters'].append(chapter)
    print(f'Chapter {number}: {len(sections)} sections')
book['chapters'].sort(key=lambda c: c['num'])
book['subtitle']='از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل برنامه‌ریزی‌شده · فصل‌های ۱ تا ۲۱ در مخزن انتشار'
path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
