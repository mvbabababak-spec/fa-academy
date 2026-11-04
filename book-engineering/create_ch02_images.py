"""Create compact WebP editorial diagrams using Pillow and RAQM."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

root = Path(__file__).resolve().parent.parent
out = root / 'assets/images/babak-ai'
out.mkdir(parents=True, exist_ok=True)
font = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(size, heavy=False): return ImageFont.truetype(bold if heavy else font, size, layout_engine=ImageFont.Layout.RAQM)
def label(draw, xy, text, size, color='#eef1ff', rtl=False, heavy=False, anchor=None):
    draw.text(xy, text, font=f(size, heavy), fill=color, direction='rtl' if rtl else 'ltr', anchor=anchor)
def canvas(w,h): return Image.new('RGB', (w,h), '#101321')
def box(d,xy,fill,outline='#484f7f',radius=24,width=2): d.rounded_rectangle(xy,radius,fill=fill,outline=outline,width=width)
def save(im, path): im.save(path,'WEBP',quality=88,method=6)

# Nested fields: generator described separately to avoid misleading hierarchy.
im=canvas(1600,1000); d=ImageDraw.Draw(im)
label(d,(1510,65),'نقشه خانواده‌های هوش مصنوعی',48,rtl=True,heavy=True,anchor='ra')
label(d,(90,142),'AI · MACHINE LEARNING · DEEP LEARNING',27,'#9caad2')
box(d,(90,210,1510,705),'#1a2140','#6872a6',30,3)
label(d,(1445,245),'هوش مصنوعی  |  AI',43,rtl=True,heavy=True,anchor='ra')
box(d,(160,325,1350,650),'#23305b','#7587d3',25,3)
label(d,(1290,360),'یادگیری ماشین  |  ML',41,rtl=True,heavy=True,anchor='ra')
box(d,(240,445,1120,594),'#33366d','#a99eff',22,3)
label(d,(1060,480),'یادگیری عمیق  |  Deep Learning',36,rtl=True,heavy=True,anchor='ra')
box(d,(90,755,1510,918),'#1d303c','#50c1cf',24,3)
label(d,(1445,782),'هوش مولد  |  Generative AI',38,rtl=True,heavy=True,anchor='ra')
label(d,(1445,845),'نوع کاربرد و خروجی؛ می‌تواند با روش‌های بالا هم‌پوشانی داشته باشد',27,'#b9d4dc',rtl=True,anchor='ra')
save(im,out/'ch02-families.webp')

im=canvas(1600,760);d=ImageDraw.Draw(im)
label(d,(1510,60),'چرخه ساده تولید توکن بعدی',47,rtl=True,heavy=True,anchor='ra')
label(d,(90,140),'AUTOREGRESSIVE GENERATION · CONCEPTUAL',25,'#9caad2')
boxes=[(70,270,385,435),(450,270,765,435),(830,270,1145,435),(1210,270,1525,435)]
labels=[('متن و زمینه','Context'),('توکن‌سازی','Tokenizer'),('مدل و توزیع','Model + probabilities'),('انتخاب توکن','Token selection')]
for xy,(fa,en) in zip(boxes,labels):
 box(d,xy,'#222949','#7a89d0',23,3);cx=(xy[0]+xy[2])//2
 label(d,(cx,304),fa,35,rtl=True,heavy=True,anchor='mt'); label(d,(cx,365),en,24,'#9ec9e0',anchor='mt')
for x in (385,765,1145):
 d.line((x+10,352,x+52,352),fill='#79d7e5',width=6);d.polygon([(x+52,340),(x+68,352),(x+52,364)],fill='#79d7e5')
d.line([(1365,455),(1365,550),(225,550),(225,455)],fill='#ae9bff',width=5)
d.polygon([(213,467),(225,450),(237,467)],fill='#ae9bff')
label(d,(795,586),'توکن انتخاب‌شده به زمینه افزوده می‌شود',30,'#d5caff',rtl=True,anchor='mt')
save(im,out/'ch02-token-cycle.webp')

# Replace the book's SVG with an editorial WebP cover, no generated text rendering dependency.
im=canvas(900,1200);d=ImageDraw.Draw(im)
for y in range(1200):
 t=y/1199;d.line((0,y,900,y),fill=(int(16+18*t),int(19+12*t),int(36+42*t)))
d.line((90,100,810,100),fill='#6f719c',width=2)
label(d,(90,143),'VOLUME 01  /  FOUNDATIONS',25,'#aab7df')
pts=[(190,500),(325,390),(460,490),(620,360),(735,500),(620,635),(460,610),(300,675)]
for a,b in [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,2),(1,6),(2,5),(3,6),(2,7)]: d.line((pts[a],pts[b]),fill='#687cc4',width=3)
for x,y in pts:d.ellipse((x-9,y-9,x+9,y+9),fill='#91e7f5')
for y,s,col in [(790,'THE ART & SCIENCE','#f4f3ff'),(850,'OF BUILDING','#f4f3ff'),(910,'INTELLIGENCE','#8fe4f2')]:label(d,(90,y),s,49,col,heavy=True)
d.line((90,1035,810,1035),fill='#6f719c',width=2);label(d,(90,1080),'BABAK & AI',29,'#c9cdeb')
save(im,root/'assets/images/art-science-cover.webp')
for p in [out/'ch02-families.webp',out/'ch02-token-cycle.webp',root/'assets/images/art-science-cover.webp']:
 print(p.relative_to(root),p.stat().st_size,'bytes')
