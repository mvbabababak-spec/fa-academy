from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent
out=root/'assets/images/babak-ai';out.mkdir(parents=True,exist_ok=True)
regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,s,size,color='#edf2ff',rtl=False,anchor='mt',heavy=False):
 d.text(xy,s,font=ImageFont.truetype(bold if heavy else regular,size,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
def box(d,xy,fill='#252d50',line='#7b86ca'):
 d.rounded_rectangle(xy,radius=22,fill=fill,outline=line,width=3)
def arrow(d,x1,x2,y):
 d.line((x1,y,x2,y),fill='#76d7e3',width=6);d.polygon([(x2,y),(x2-18,y-11),(x2-18,y+11)],fill='#76d7e3')
def save(im,name):
 p=out/name;im.save(p,'WEBP',quality=88,method=6);print(name,im.size,p.stat().st_size,'bytes')

im=Image.new('RGB',(1600,920),'#101321');d=ImageDraw.Draw(im)
text(d,(1510,55),'مسیر مفهومی داده در رایانه',47,rtl=True,anchor='ra',heavy=True)
text(d,(90,140),'DATA FLOW · SIMPLIFIED',25,'#9cafd6',anchor='la')
items=[('ذخیره‌سازی','STORAGE'),('حافظه اصلی','RAM'),('حافظه نهان','CACHE'),('پردازنده','CPU')]
for i,(fa,en) in enumerate(items):
 x=70+i*390;box(d,(x,290,x+290,485));text(d,(x+145,335),fa,34,rtl=True,heavy=True);text(d,(x+145,405),en,26,'#a9cbe3')
 if i<3:arrow(d,x+300,x+380,385)
box(d,(160,600,1440,750),'#1e303d','#58bccc')
text(d,(800,630),'سیستم‌عامل، برنامه و درایورها حرکت داده را مدیریت می‌کنند',30,rtl=True,heavy=True)
text(d,(800,689),'THE REAL PATH DEPENDS ON HARDWARE AND SOFTWARE',22,'#b2c8d6')
save(im,'ch05-data-path.webp')

im=Image.new('RGB',(1600,930),'#101321');d=ImageDraw.Draw(im)
text(d,(1510,55),'سه ویژگی متفاوت حافظه و انتقال',47,rtl=True,anchor='ra',heavy=True)
text(d,(90,140),'CAPACITY · BANDWIDTH · LATENCY',25,'#a1b4d7',anchor='la')
items=[('ظرفیت','CAPACITY','چه مقدار داده جا می‌شود؟'),('پهنای باند','BANDWIDTH','چه مقدار داده در واحد زمان منتقل می‌شود؟'),('تأخیر','LATENCY','چه مدت برای یک دسترسی منتظر می‌مانیم؟')]
for i,(fa,en,desc) in enumerate(items):
 y=225+i*190;box(d,(90,y,1510,y+150),fill=['#222a4a','#283154','#243c4c'][i]);text(d,(1430,y+23),fa,37,rtl=True,anchor='ra',heavy=True);text(d,(160,y+30),en,27,'#a5cce1',anchor='la');text(d,(1430,y+88),desc,29,'#cbd6e8',rtl=True,anchor='ra')
text(d,(800,840),'نمودار کیفی است و سرعت یک دستگاه مشخص را نشان نمی‌دهد',27,'#c1bedf',rtl=True)
save(im,'ch05-capacity.webp')
