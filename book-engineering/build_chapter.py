"""Insert chapters 6 and 7 without changing earlier app content (mistune 3)."""
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
assert {c['num'] for c in book['chapters']} >= {1, 2, 3, 4, 5}
render = mistune.create_markdown(plugins=['table'])
for number, slug, title, icon, expected in [
    (6, '06-gpu-parallelism', 'GPU و NPU: محاسبات موازی و حافظه مدل', '◈', 13),
    (7, '07-compute-ecosystems', 'اکوسیستم‌های محاسبات هوش مصنوعی: CUDA، ROCm، TPU و Apple Silicon', '▣', 13),
]:
    source = f'book-engineering/chapters/{slug}.md'
    text = (root / source).read_text(encoding='utf-8')
    parts = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
    assert (len(parts)-1)//2 == expected
    sections = []
    for n in range(1, len(parts), 2):
        section_title = parts[n].strip()
        content = (parts[0]+'\n' if n == 1 else '')+'## '+section_title+'\n'+parts[n+1]
        sections.append({'id': f'art-science-v1-ch{number:02}-s{(n+1)//2:02}',
                         'title': section_title, 'file': source, 'html': render(content)})
    chapter = {'num': number, 'id': f'art-science-v1-ch{number:02}', 'title': title,
               'icon': icon, 'sections': sections}
    indices = [i for i,c in enumerate(book['chapters']) if c['id']==chapter['id']]
    assert len(indices)<=1
    if indices: book['chapters'][indices[0]]=chapter
    else: book['chapters'].append(chapter)
    print(f'Chapter {number}: {len(sections)} sections')
book['chapters'].sort(key=lambda c: c['num'])
book['subtitle']='از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل برنامه‌ریزی‌شده · فصل‌های ۱ تا ۷ منتشر شده'
path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
