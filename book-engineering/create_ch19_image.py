from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch19-bayes.webp'
im=Image.new('RGB',(1600,850),'#121828');d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(x,y,s,n=36):d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),anchor='mt',direction='rtl',fill='#f1f5ff')
text(800,65,'مثال فرضی بیز: ۱۰٬۰۰۰ نفر',48)
for x,title,v1,v2 in [(100,'دارای ویژگی','100 expected','90 positive'),(850,'فاقد ویژگی','9,900 expected','495 positive')]:
 d.rounded_rectangle((x,220,x+650,560),radius=28,fill='#293c60',outline='#aec3ee',width=3);text(x+325,270,title,38);text(x+325,365,v1,36);text(x+325,455,v2,36)
text(800,660,'از ۵۸۵ نتیجه مثبت مورد انتظار، ۹۰ مورد واقعی',37)
p.parent.mkdir(parents=True,exist_ok=True);im.save(p,'WEBP',quality=88,method=6);print('bytes=',p.stat().st_size)
