"""Append the first three chapters of volume 2; never overwrite existing work."""
import json
import re
from pathlib import Path
import mistune

ROOT=Path(__file__).resolve().parent.parent
file=ROOT/'data.json'
data=json.loads(file.read_text(encoding='utf8'))
render=mistune.create_markdown(plugins=['table'])
specs=[(1,'22-learning-paradigms','شیوه‌های یادگیری ماشین و صورت‌بندی مسئله','◈'),
       (2,'23-regression','رگرسیون خطی و لجستیک از پایه','▣'),
       (3,'24-classical-models','درخت، جنگل، SVM و نزدیک‌ترین همسایه‌ها','✦')]
chapters=[]
for n,slug,title,icon in specs:
    path=f'book-engineering/chapters/{slug}.md';text=(ROOT/path).read_text(encoding='utf8')
    parts=re.split(r'^## (.+)$',text,flags=re.MULTILINE)
    sections=[]
    for i in range(1,len(parts),2):
        body=(parts[0]+'\n' if i==1 else '')+'## '+parts[i]+'\n'+parts[i+1]
        sections.append({'id':f'art-science-v2-ch{n:02}-s{(i+1)//2:02}', 'title':parts[i].strip(),'file':path,'html':render(body)})
    assert len(sections)>0
    chapters.append({'num':n,'id':f'art-science-v2-ch{n:02}','title':title,'icon':icon,'sections':sections})
book={'id':'art-science-intelligence-v2','title':'هنر و علم ساخت هوش — جلد دوم',
      'subtitle':'یادگیری ماشین و شبکه‌های عصبی | فصل‌های ۱ تا ۳ منتشر شده‌اند',
      'author':'Babak & Ai','cover':'assets/images/art-science-cover.webp','chapters':chapters}
found=[b for b in data['books'] if b['id']==book['id']]
if found:
    assert len(found)==1 and found[0]==book,'Volume 2 already exists; refusing to replace it'
    print('Volume 2 already exists and matches; no change')
else:
    i=next(i for i,b in enumerate(data['books']) if b['id']=='art-science-intelligence-v1')
    data['books'].insert(i+1,book)
    file.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
    print('Added volume 2:',[(c['num'],len(c['sections'])) for c in chapters])
