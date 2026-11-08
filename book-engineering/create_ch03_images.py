"""Draw Persian educational WebP diagrams with Pillow and RAQM."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'assets/images/babak-ai'
out.mkdir(parents=True, exist_ok=True)
regular = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(size, strong=False):
    return ImageFont.truetype(bold if strong else regular, size, layout_engine=ImageFont.Layout.RAQM)
def text(d, xy, value, size, color='#edf2ff', rtl=False, strong=False, anchor='mt'):
    d.text(xy, value, font=font(size, strong), fill=color, direction='rtl' if rtl else 'ltr', anchor=anchor)
def box(d, coords, fill='#242d50', outline='#7987cb'):
    d.rounded_rectangle(coords, radius=20, fill=fill, outline=outline, width=3)
def arrow(d, start, end, color='#73d9e5'):
    x1,y1=start; x2,y2=end; d.line((x1,y1,x2,y2),fill=color,width=6)
    if x2>x1: d.polygon([(x2,y2),(x2-19,y2-11),(x2-19,y2+11)],fill=color)
    elif x2<x1: d.polygon([(x2,y2),(x2+19,y2-11),(x2+19,y2+11)],fill=color)
    elif y2>y1: d.polygon([(x2,y2),(x2-11,y2-19),(x2+11,y2-19)],fill=color)
    else: d.polygon([(x2,y2),(x2-11,y2+19),(x2+11,y2+19)],fill=color)
def save(im, name):
    p=out/name; im.save(p,'WEBP',quality=88,method=6); print(name, im.size, p.stat().st_size, 'bytes')

im=Image.new('RGB',(1600,950),'#101321'); d=ImageDraw.Draw(im)
text(d,(1510,55),'چرخه حیات یک مدل',48,rtl=True,strong=True,anchor='ra')
text(d,(90,140),'MODEL LIFECYCLE · CONCEPTUAL',26,'#a3b4dc',anchor='la')
steps=[(1110,235,1510,390,'تعریف مسئله','DEFINE'),(600,235,1000,390,'داده و تقسیم','DATA & SPLIT'),(90,235,490,390,'آموزش','TRAIN'),(90,510,490,665,'ارزیابی و انتخاب','EVALUATE'),(600,510,1000,665,'استقرار و استنتاج','DEPLOY & INFER'),(1110,510,1510,665,'پایش و بازخورد','MONITOR')]
for x1,y1,x2,y2,fa,en in steps:
 box(d,(x1,y1,x2,y2)); cx=(x1+x2)//2
 text(d,(cx,y1+30),fa,35,rtl=True,strong=True);text(d,(cx,y1+95),en,24,'#a6cae6')
arrow(d,(1100,312),(1010,312));arrow(d,(590,312),(500,312));arrow(d,(290,402),(290,498));arrow(d,(500,587),(590,587));arrow(d,(1010,587),(1100,587))
d.line([(1310,680),(1310,760),(1310,820),(1510,820),(1540,820),(1540,190),(1310,190),(1310,220)],fill='#b6a6ff',width=5)
d.polygon([(1299,220),(1321,220),(1310,237)],fill='#b6a6ff')
text(d,(800,785),'بازخورد برای بازنگری؛ نه الزاماً بازآموزی خودکار',29,'#d1c9f2',rtl=True)
save(im,'ch03-lifecycle.webp')

im=Image.new('RGB',(1600,950),'#101321');d=ImageDraw.Draw(im)
text(d,(1510,55),'سه مجموعه، سه نقش متفاوت',48,rtl=True,strong=True,anchor='ra')
text(d,(90,140),'TRAIN · VALIDATION · TEST',26,'#a3b4dc',anchor='la')
box(d,(540,210,1060,310),'#1b3046','#67b9cb');text(d,(800,236),'داده‌های مجاز و بررسی‌شده',35,rtl=True,strong=True)
d.line((800,310,800,355),fill='#73d9e5',width=5);d.line((280,355,1320,355),fill='#73d9e5',width=5)
for x in (280,800,1320):arrow(d,(x,355),(x,410))
for x,fa,en,desc in [(280,'آموزش','TRAIN','تنظیم پارامترها'),(800,'اعتبارسنجی','VALIDATION','انتخاب مدل و تنظیمات'),(1320,'آزمون','TEST','گزارش نهایی مستقل')]:
 box(d,(x-220,415,x+220,625));text(d,(x,448),fa,37,rtl=True,strong=True);text(d,(x,510),en,24,'#a6cae6');text(d,(x,560),desc,27,'#d4def3',rtl=True)
box(d,(110,705,1490,835),'#24273f','#817ac5')
text(d,(800,735),'نمونه‌ها و اطلاعات آینده بین بخش‌ها نشت نکنند',34,'#e2d9ff',rtl=True,strong=True)
save(im,'ch03-splits.webp')
