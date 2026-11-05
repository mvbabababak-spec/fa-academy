"""Append chapters 7–9 to volume 2 without replacing existing chapters."""
import json,re
from pathlib import Path
import mistune
ROOT=Path(__file__).resolve().parent.parent
path=ROOT/'data.json';data=json.loads(path.read_text(encoding='utf8'))
books=[b for b in data['books'] if b['id']=='art-science-intelligence-v2'];assert len(books)==1
book=books[0];assert [c['num'] for c in book['chapters'][:6]]==list(range(1,7))
render=mistune.create_markdown(escape=False,plugins=['table'])
specs=[(7,'28-backprop','تابع زیان، پس‌انتشار و بررسی گرادیان','◈'),(8,'29-optimizers','SGD، Adam، AdamW، نرمال‌سازی و Dropout','▣'),(9,'30-neural-network','ساخت و بازتولید شبکه عصبی با NumPy و PyTorch','✦')]
for n,slug,title,icon in specs:
    source=f'book-engineering/chapters/{slug}.md';text=(ROOT/source).read_text(encoding='utf8')
    parts=re.split(r'^## (.+)$',text,flags=re.MULTILINE);sections=[]
    for i in range(1,len(parts),2):
        body=(parts[0]+'\n' if i==1 else '')+'## '+parts[i]+'\n'+parts[i+1]
        sections.append({'id':f'art-science-v2-ch{n:02}-s{(i+1)//2:02}','title':parts[i].strip(),'file':source,'html':render(body)})
    chapter={'num':n,'id':f'art-science-v2-ch{n:02}','title':title,'icon':icon,'sections':sections}
    existing=[c for c in book['chapters'] if c['num']==n or c['id']==chapter['id']]
    if existing:
        assert len(existing)==1 and existing[0]==chapter,'Refusing to replace existing chapter'
        print('Already present, unchanged:',n)
    else:
        assert [c['num'] for c in book['chapters']]==list(range(1,n)), 'Chapters must be appended in order'
        book['chapters'].append(chapter);print('Added:',n,len(sections),'sections')
if len(book['chapters'])==9:book['subtitle']='یادگیری ماشین و شبکه‌های عصبی | فصل‌های ۱ تا ۹ منتشر شده‌اند'
path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
