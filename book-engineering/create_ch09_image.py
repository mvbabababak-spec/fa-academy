from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent;p=root/'assets/images/babak-ai/ch09-flow.webp';p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1500,1120),'#101321');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(xy,s,n,rtl=False,color='#edf2ff',anchor='mt',heavy=False):d.text(xy,s,font=ImageFont.truetype(bold if heavy else font,n,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
text((1420,55),'فلوچارت جمع دو عدد',46,True,anchor='ra',heavy=True);text((80,140),'INPUT → COMPUTE → OUTPUT',25,color='#a3b4d7',anchor='la')
steps=[('شروع','START'),('دریافت دو عدد','INPUT TWO NUMBERS'),('محاسبه مجموع','ADD'),('نمایش نتیجه','DISPLAY RESULT'),('پایان','END')]
for i,(fa,en) in enumerate(steps):
 y=215+i*160;d.rounded_rectangle((320,y,1180,y+105),radius=50 if i in (0,4) else 18,fill='#252f50',outline='#8998d0',width=3);text((750,y+15),fa,34,True,heavy=True);text((750,y+62),en,20,color='#a5c9df')
 if i<4:d.line((750,y+110,750,y+145),fill='#79d8e6',width=5);d.polygon([(750,y+155),(738,y+138),(762,y+138)],fill='#79d8e6')
im.save(p,'WEBP',quality=88,method=6);print(p,im.size,p.stat().st_size)
