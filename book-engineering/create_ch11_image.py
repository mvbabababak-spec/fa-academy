from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch11-function.webp';p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1500,850),'#101321');d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def t(x,y,s,n=36):d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),fill='#edf2ff',direction='rtl',anchor='mt')
t(750,70,'تابع: ورودی، پردازش و خروجی',46)
for x,label,en in [(80,'ورودی','INPUT'),(575,'تابع','FUNCTION'),(1070,'خروجی','RETURN')]:
 d.rounded_rectangle((x,300,x+350,520),radius=24,fill='#283454',outline='#9aace7',width=3);t(x+175,345,label,38);d.text((x+175,420),en,font=ImageFont.truetype(f,26),fill='#a4d5e1',anchor='mt')
for x in [440,935]:d.line((x,410,x+115,410),fill='#7bd9e5',width=6);d.polygon([(x+115,410),(x+96,397),(x+96,423)],fill='#7bd9e5')
t(750,650,'بازگرداندن نتیجه با نمایش آن یکسان نیست',30)
im.save(p,'WEBP',quality=88,method=6);print(p.stat().st_size)
