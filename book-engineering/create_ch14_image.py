from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch14-tests.webp'
im=Image.new('RGB',(1600,900),'#101525'); d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(x,y,s,n=36): d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),fill='#edf3ff',direction='rtl',anchor='mt')
text(800,85,'از ورودی تا آزمون',49)
for x,fa,en in [(70,'ورودی','Input'),(570,'داده و SQL','SQLite'),(1070,'بررسی نتیجه','Test')]:
 d.rounded_rectangle((x,320,x+430,600),radius=24,fill='#293655',outline='#a5b7e5',width=3);text(x+215,380,fa,38);text(x+215,475,en,30)
for x in (510,1010):
 d.line((x,460,x+55,460),fill='#82dacf',width=5);d.polygon([(x+55,460),(x+37,447),(x+37,473)],fill='#82dacf')
text(800,725,'اعتبارسنجی، پارامتر و تست',38)
p.parent.mkdir(parents=True,exist_ok=True);im.save(p,'WEBP',quality=88,method=6);print(p.stat().st_size)
