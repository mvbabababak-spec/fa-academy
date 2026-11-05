from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent; p=root/'assets/images/babak-ai/ch08-distributed.webp';p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1600,950),'#101321');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def t(xy,s,n,rtl=False,color='#edf2ff',anchor='mt',heavy=False):d.text(xy,s,font=ImageFont.truetype(bold if heavy else font,n,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
def b(xy,fill='#252d50',line='#7888c9'):d.rounded_rectangle(xy,radius=22,fill=fill,outline=line,width=3)
t((1510,55),'توپولوژی مفهومی چندگره‌ای',46,True,anchor='ra',heavy=True);t((90,135),'MULTI-NODE · CONCEPTUAL',25,color='#9eaed5',anchor='la')
for x,fa,en in [(80,'سرور اول','NODE A'),(900,'سرور دوم','NODE B')]:
 b((x,230,x+620,680));t((x+310,260),fa,36,True,heavy=True);t((x+310,315),en,24,color='#a5c5dd')
 for i in range(2):
  xx=x+65+i*280;b((xx,390,xx+220,520),'#354175','#9ba9f5');t((xx+110,430),f'GPU {i+1}',32,heavy=True)
 d.line((x+300,455,x+320,455),fill='#7fd8e7',width=5)
 t((x+310,590),'مسیر داخلی وابسته به سخت‌افزار',26,True,color='#c9d8e5')
d.line((715,440,885,440),fill='#8ee3eb',width=7);d.polygon([(885,440),(865,428),(865,452)],fill='#8ee3eb');d.polygon([(715,440),(735,428),(735,452)],fill='#8ee3eb')
t((800,375),'شبکه',30,True,heavy=True);t((800,745),'سرعت و مسیرهای واقعی به توپولوژی و پیکربندی وابسته‌اند',28,True,color='#d4c9f0')
im.save(p,'WEBP',quality=88,method=6);print(p,im.size,p.stat().st_size)
