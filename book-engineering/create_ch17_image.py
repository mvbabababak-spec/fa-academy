from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch17-matrix.webp'
im=Image.new('RGB',(1600,850),'#121828');d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(x,y,s,n=40):
 d.text((x,y),s,font=ImageFont.truetype(f,n,layout_engine=ImageFont.Layout.RAQM),anchor='mt',direction='rtl',fill='#f1f5ff')
text(800,90,'سازگاری ابعاد در ضرب ماتریسی',48)
for x,title,shape in [(110,'ماتریس A','2 × 3'),(600,'ماتریس B','3 × 2'),(1090,'حاصل AB','2 × 2')]:
 d.rounded_rectangle((x,285,x+400,535),radius=22,fill='#283b5e',outline='#aac0f2',width=4)
 text(x+200,330,title,38);d.text((x+200,425),shape,font=ImageFont.truetype(f,55),anchor='mt',direction='ltr',fill='#f1f5ff')
text(555,375,'×',55);text(1045,375,'=',55);text(800,655,'ابعاد داخلی برابر؛ ابعاد خارجی نتیجه',38)
p.parent.mkdir(parents=True,exist_ok=True);im.save(p,'WEBP',quality=88,method=6);print('bytes=',p.stat().st_size)
