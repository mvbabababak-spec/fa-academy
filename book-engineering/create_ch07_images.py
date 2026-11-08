from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent
out=root/'assets/images/babak-ai';out.mkdir(parents=True,exist_ok=True)
regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,xy,s,size,color='#edf2ff',rtl=False,anchor='mt',heavy=False):
 d.text(xy,s,font=ImageFont.truetype(bold if heavy else regular,size,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
def box(d,xy,fill='#252d50',line='#7b86ca'):
 d.rounded_rectangle(xy,radius=22,fill=fill,outline=line,width=3)
def arrow(d,start,end,color='#77d8e4'):
 x1,y1=start;x2,y2=end;d.line((x1,y1,x2,y2),fill=color,width=5)
 if y2>y1:d.polygon([(x2,y2),(x2-11,y2-18),(x2+11,y2-18)],fill=color)
 elif x2>x1:d.polygon([(x2,y2),(x2-18,y2-11),(x2-18,y2+11)],fill=color)
def save(im,name):
 p=out/name;im.save(p,'WEBP',quality=88,method=6);print(name,im.size,p.stat().st_size,'bytes')

im=Image.new('RGB',(1600,1050),'#101321');d=ImageDraw.Draw(im)
text(d,(1510,55),'زنجیره سازگاری اجرای مدل',47,rtl=True,anchor='ra',heavy=True)
text(d,(90,140),'SOFTWARE AND HARDWARE STACK · CONCEPTUAL',25,'#a3b4d7',anchor='la')
levels=[('برنامه و مدل','APPLICATION & MODEL'),('چارچوب یادگیری ماشین','ML FRAMEWORK'),('کتابخانه، بک‌اند و محیط اجرا','BACKEND · LIBRARY · RUNTIME'),('سیستم‌عامل و درایور','OS & DRIVER'),('شتاب‌دهنده سازگار','SUPPORTED ACCELERATOR')]
for i,(fa,en) in enumerate(levels):
 y=215+i*145;box(d,(255,y,1345,y+105),fill=['#252d50','#273452','#2b3158','#233a4d','#1e3941'][i]);text(d,(1280,y+25),fa,34,rtl=True,anchor='ra',heavy=True);text(d,(315,y+34),en,23,'#a8c7df',anchor='la')
 if i<4:arrow(d,(800,y+110),(800,y+140))
save(im,'ch07-stack.webp')

im=Image.new('RGB',(1600,930),'#101321');d=ImageDraw.Draw(im)
text(d,(1510,55),'انتخاب مسیر محاسباتی',47,rtl=True,anchor='ra',heavy=True)
text(d,(90,140),'SELECT · VERIFY · TEST · MEASURE',25,'#a3b4d7',anchor='la')
steps=[('۱. تعریف نیاز','MODEL & GOAL'),('۲. بررسی سازگاری','COMPATIBILITY'),('۳. آزمون صحت','CORRECTNESS'),('۴. سنجش هزینه','MEASURE & COST')]
for i,(fa,en) in enumerate(steps):
 y=220+i*145;box(d,(180,y,1420,y+100));text(d,(1350,y+24),fa,33,rtl=True,anchor='ra',heavy=True);text(d,(245,y+32),en,24,'#a7c6dc',anchor='la')
 if i<3:arrow(d,(800,y+105),(800,y+140))
text(d,(800,850),'تصمیم نهایی به بار واقعی، ایمنی و منابع بستگی دارد',28,'#d8d0f2',rtl=True)
save(im,'ch07-selection.webp')
