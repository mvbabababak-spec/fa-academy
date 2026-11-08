"""Rebuild selected existing chapters and the standalone volume without changing IDs.
Usage: python book-engineering/rebuild_audit.py 14 15 16
Requires mistune 3. Never creates or removes chapters or sections.
"""
import json
from pathlib import Path
import re
import sys
import mistune

root = Path(__file__).resolve().parent.parent
path = root / 'data.json'
data = json.loads(path.read_text(encoding='utf-8'))
book = next(b for b in data['books'] if b['id'] == 'art-science-intelligence-v1')
assert [c['num'] for c in book['chapters']] == list(range(1, 22))
selected = {int(n) for n in sys.argv[1:]}
assert selected <= set(range(1, 22))
render = mistune.create_markdown(plugins=['table'])
render_math = mistune.create_markdown(renderer=mistune.HTMLRenderer(escape=False), plugins=['table'])
for chapter in book['chapters']:
    if chapter['num'] not in selected:
        continue
    sources = {s['file'] for s in chapter['sections']}
    assert len(sources) == 1
    source = next(iter(sources))
    text = (root / source).read_text(encoding='utf-8')
    parts = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
    assert (len(parts) - 1) // 2 == len(chapter['sections']), 'Section count changed'
    for i, section in enumerate(chapter['sections']):
        n = 2*i + 1
        content = (parts[0] + '\n' if i == 0 else '') + '## ' + parts[n].strip() + '\n' + parts[n+1]
        section['title'] = parts[n].strip()
        section['html'] = (render_math if '<math ' in content else render)(content)
    print(f"Rebuilt chapter {chapter['num']}: {len(chapter['sections'])} stable IDs")
path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

base = 'https://raw.githubusercontent.com/mvbabababak-spec/fa-academy/gh-pages/'
intro = ['# هنر و علم ساخت هوش — جلد اول: پایه‌های ساخت هوش',
         '**The Art & Science of Building Intelligence — Babak & Ai**', '',
         '**شناسنامه:** جلد اول؛ نسخه کاری 0.9.0-rc (در حال ممیزی، نه انتشار نهایی)؛ مبنای تغییرات: fb733b65a65d6f511aed87e533c7e15b7f199ef4؛ تاریخ ۵ نوامبر ۲۰۲۶. مجوز انتشار: مشخص نشده و نیازمند تصمیم صاحب اثر است. روش ارجاع: Babak & Ai، هنر و علم ساخت هوش، جلد اول، نسخه و commit مورد استفاده. محدودیت: برخی آزمون‌ها و بررسی‌های نشر هنوز باز هستند.', '',
         'این فایل نسخه یکپارچهٔ متن ۲۱ فصل جلد اول برای مطالعه و بازبینی است. منابع، کدها و بخش‌های تکمیلی هر فصل حفظ شده‌اند.', '',
         '[پروژه‌ها](https://github.com/mvbabababak-spec/fa-academy/tree/gh-pages/book-engineering/projects) · [نقشه پنج جلد](https://github.com/mvbabababak-spec/fa-academy/blob/gh-pages/BOOK_ROADMAP_FA.md)', '', '## فهرست فصل‌ها', '']
for c in book['chapters']:
    intro.append(f"{c['num']}. {c['title']} — [فایل منبع فصل]({base+c['sections'][0]['file']})")
parts = ['\n'.join(intro) + '\n\n---\n']
for c in book['chapters']:
    files = {s['file'] for s in c['sections']}
    assert len(files) == 1
    text = (root / next(iter(files))).read_text(encoding='utf-8').strip()
    text = re.sub(r'(!\[[^\]]*\]\()(assets/[^)]+)(\))', lambda m: m[1]+base+m[2]+m[3], text)
    parts.append(text + '\n\n---\n')
(root / 'volume-1-full-fa.md').write_text('\n'.join(parts), encoding='utf-8')
