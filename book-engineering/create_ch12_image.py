from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch12-object.webp';p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1500,900),'#101321');d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def t(x,y,s,n=36):d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),fill='#edf2ff',direction='rtl',anchor='mt')
t(750,70,'نمونه‌ای از یک کلاس',46)
d.rounded_rectangle((220,200,1280,730),radius=28,fill='#283454',outline='#9aace7',width=3);t(750,245,'جلسه مطالعه | StudySession',40)
d.line((300,330,1200,330),fill='#8698c6',width=3)
t(750,380,'ویژگی‌ها: موضوع و دقیقه',38);t(750,490,'متد: تبدیل به داده',38);t(750,600,'اعتبارسنجی در زمان ساخت',32)
im.save(p,'WEBP',quality=88,method=6);print(p.stat().st_size)
