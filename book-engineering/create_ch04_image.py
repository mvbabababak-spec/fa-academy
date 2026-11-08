from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent
out=root/'assets/images/babak-ai/ch04-timeline.webp';out.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1600,1050),'#101321');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def t(xy,s,size,color='#ecf0ff',rtl=False,anchor='mt',heavy=False):
 d.text(xy,s,font=ImageFont.truetype(bold if heavy else font,size,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
t((1510,55),'نقاط عطف منتخب هوش مصنوعی',48,rtl=True,anchor='ra',heavy=True)
t((90,136),'SELECTED MILESTONES · PUBLICATION YEARS',24,'#a2b2d6',anchor='la')
d.line((205,220,205,930),fill='#6ccadf',width=5)
entries=[('1943','نورون منطقی','McCulloch & Pitts'),('1950','بازی تقلید','Turing'),('1955 / 1956','پیشنهاد و پروژه دارتموث','Dartmouth'),('1958','پرسپترون','Rosenblatt'),('1986','پس‌انتشار و نمایش‌ها','Rumelhart et al.'),('2012','شبکه کانولوشنی AlexNet','Krizhevsky et al.'),('2017','معماری Transformer','Vaswani et al.')]
for i,(year,fa,en) in enumerate(entries):
 y=230+i*100;d.ellipse((195,y+16,215,y+36),fill='#9de8f3');d.rounded_rectangle((255,y,1510,y+76),radius=15,fill='#232b4a',outline='#56618d',width=2)
 t((320,y+18),year,26,'#9be4f3',anchor='la',heavy=True);t((1455,y+14),fa,31,rtl=True,anchor='ra',heavy=True);t((750,y+21),en,22,'#a8b4d5',anchor='ma')
im.save(out,'WEBP',quality=88,method=6);print(out,im.size,out.stat().st_size)
