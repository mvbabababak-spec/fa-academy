from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch13-git.webp';p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1600,900),'#111525');d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(x,y,s,n=34,color='#f0f3ff'):d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl',anchor='mt')
text(800,100,'جریان محلی Git',52)
for x,label,en in [(80,'فایل کاری','Working tree'),(600,'آماده‌سازی','Staging'),(1120,'تاریخ محلی','Commit')]:
 d.rounded_rectangle((x,320,x+400,590),radius=25,fill='#293656',outline='#a7b9e7',width=3);text(x+200,380,label,35);text(x+200,475,en,27)
for x,label in [(500,'git add'),(1020,'git commit')]:
 d.line((x-10,450,x+75,450),fill='#79d7ce',width=5);d.polygon([(x+75,450),(x+55,437),(x+55,463)],fill='#79d7ce');text(x+30,620,label,24)
text(800,740,'انتشار راه دور گامی جداگانه است',35)
im.save(p,'WEBP',quality=88,method=6);print(p.stat().st_size)
