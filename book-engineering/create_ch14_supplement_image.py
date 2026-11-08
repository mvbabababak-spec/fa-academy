from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch14-testing.webp'
im=Image.new('RGB',(1600,900),'#111827'); d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(x,y,s,n=38): d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),fill='#eff4ff',anchor='mt',direction='rtl')
text(800,95,'چرخه بهبود نرم‌افزار',48)
for x,y,label in [(200,270,'طراحی'),(1000,270,'آزمون'),(1000,580,'مشاهده'),(200,580,'اصلاح')]:
 d.rounded_rectangle((x,y,x+400,y+150),radius=24,fill='#293d62',outline='#a9bcf4',width=3); text(x+200,y+48,label,40)
for a,b in [((620,345),(980,345)),((1200,440),(1200,560)),((980,655),(620,655)),((400,560),(400,440))]:
 d.line((a,b),fill='#7be4cb',width=7)
 import math
 angle=math.atan2(b[1]-a[1],b[0]-a[0]); wing=18
 d.polygon([b,(b[0]-25*math.cos(angle)+wing*math.sin(angle),b[1]-25*math.sin(angle)-wing*math.cos(angle)),(b[0]-25*math.cos(angle)-wing*math.sin(angle),b[1]-25*math.sin(angle)+wing*math.cos(angle))],fill='#7be4cb')
p.parent.mkdir(parents=True,exist_ok=True);im.save(p,'WEBP',quality=88,method=6);print('bytes=',p.stat().st_size)
